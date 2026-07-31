#!/usr/bin/env python3
"""Observed-only name splitting for the reviewed Sakhalin 1890 dataset.

The parser never infers components from household relationships. It preserves
name_raw/name_alias, uses deterministic source-order rules, applies a small
reviewed exception table, and routes uncertain structures to manual review.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


SPACE_RE = re.compile(r"\s+")
EDGE_PUNCT_RE = re.compile(r"^[,.;:]+|[,.;:]+$")
ORDINAL_RE = re.compile(r"^(?:\d+-(?:й|я|е)|\d+(?:й|я|е)|[IVX]+)$", re.IGNORECASE)

OUTPUT_FIELDS = [
    "first_name", "patronymic_name", "last_name",
    "first_name_source", "patronymic_source", "last_name_source",
    "parse_status", "parse_confidence", "parse_rule", "name_order_detected",
    "naming_model", "manual_review_reason", "patronymic_name_proposed",
    "proposal_rule",
]


def norm(value: str | None) -> str:
    return SPACE_RE.sub(" ", (value or "").strip()).casefold()


def clean_name(value: str | None) -> str:
    return " ".join(
        EDGE_PUNCT_RE.sub("", token)
        for token in SPACE_RE.split((value or "").strip()) if token
    )


def canonical_sex(value: str | None) -> str:
    value = norm(value)
    if value in {"м", "муж", "мужской", "male", "m"}:
        return "male"
    if value in {"ж", "жен", "женский", "female", "f"}:
        return "female"
    return "unknown"


def naming_model(religion: str | None) -> str:
    value = norm(religion)
    if any(x in value for x in ("мусуль", "магомет", "ислам")):
        return "muslim"
    if "катол" in value:
        return "catholic"
    if "лютеран" in value:
        return "lutheran"
    if any(x in value for x in ("иудей", "армяно-григориан")):
        return "other_documented"
    if any(x in value for x in ("православ", "расколь", "старообряд", "молокан")):
        return "russian_historical"
    return "unknown"


def load_lexicon(path: Path):
    result = defaultdict(list)
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            result[norm(row["name"])].append(row)
    return result


def load_exceptions(path: Path):
    result = {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            pid = row["person_id"].strip()
            if not pid or pid in result:
                raise ValueError(f"invalid or duplicate exception person_id: {pid}")
            result[pid] = row
    return result


def first_name_match(token, sex, model, lexicon):
    entries = lexicon.get(norm(token), [])
    if not entries:
        return False, "unknown"
    if sex == "unknown":
        return True, "possible"
    if any(entry["sex"] == sex for entry in entries):
        return True, "match"
    return True, "conflict"


def patronymic_like(token, sex):
    value = norm(token)
    if sex == "female":
        return value.endswith(("овна", "евна", "ична", "инична", "ова", "ева", "ина"))
    if sex == "male":
        return value.endswith(("ович", "евич", "ич", "ов", "ев", "ин"))
    return value.endswith(("ович", "евич", "овна", "евна"))


def proposed_short_patronymic(parent_first, child_sex):
    value = norm(parent_first)
    irregular = {"илья": "ильин", "фома": "фомин", "лука": "лукин"}
    if value in irregular:
        base = irregular[value]
    elif value.endswith("й"):
        base = value[:-1] + "ев"
    elif value.endswith(("а", "я")):
        return ""
    elif value.endswith("ь"):
        base = value[:-1] + "ев"
    elif value:
        base = value + "ов"
    else:
        return ""
    if child_sex == "female":
        base += "а"
    return base[:1].upper() + base[1:]


def empty_result(model):
    return {
        "first_name": "", "patronymic_name": "", "last_name": "",
        "first_name_source": "", "patronymic_source": "", "last_name_source": "",
        "parse_status": "unresolved", "parse_confidence": "low", "parse_rule": "",
        "name_order_detected": "", "naming_model": model,
        "manual_review_reason": "", "patronymic_name_proposed": "", "proposal_rule": "",
    }


def set_component(out, field, value, source="observed"):
    out[field] = value
    source_field = {
        "first_name": "first_name_source",
        "patronymic_name": "patronymic_source",
        "last_name": "last_name_source",
    }[field]
    out[source_field] = source if value else ""


def apply_exception(row, out, exception):
    if clean_name(row.get("name_raw", "")) != clean_name(exception["match_name_raw"]):
        raise ValueError(f"exception name_raw mismatch for {row.get('person_id')}")
    expected_alias = exception.get("match_name_alias", "").strip()
    if expected_alias and norm(row.get("name_alias", "")) != norm(expected_alias):
        raise ValueError(f"exception name_alias mismatch for {row.get('person_id')}")
    set_component(out, "first_name", exception["first_name"], "reviewed_exception")
    set_component(out, "patronymic_name", exception["patronymic_name"], "reviewed_exception")
    set_component(out, "last_name", exception["last_name"], "reviewed_exception")
    out.update(parse_status="observed", parse_confidence="high",
               parse_rule=exception["parse_rule"], name_order_detected="reviewed_exception",
               manual_review_reason=exception["review_reason"])
    return out


def parse_one(row, columns, lexicon, exceptions=None):
    exceptions = exceptions or {}
    model = naming_model(row.get(columns.religion, ""))
    out = empty_result(model)
    pid_col = getattr(columns, "person_id", "person_id")
    pid = row.get(pid_col, "")
    if pid in exceptions:
        return apply_exception(row, out, exceptions[pid])

    raw_tokens = clean_name(row.get(columns.name, "")).split()
    ordinal_tokens = [token for token in raw_tokens if ORDINAL_RE.match(token)]
    tokens = [token for token in raw_tokens if not ORDINAL_RE.match(token)]
    sex = canonical_sex(row.get(columns.sex, ""))
    matches = [first_name_match(token, sex, model, lexicon) for token in tokens]

    if not tokens:
        out["manual_review_reason"] = "empty_name"
        return out

    # Owner direction: complex Muslim names are not auto-split. Straightforward
    # two-token names still use First + Last below.
    if model == "muslim" and len(tokens) >= 3:
        out.update(parse_status="manual_review", parse_confidence="low",
                   parse_rule="complex_muslim_manual",
                   manual_review_reason="complex_muslim_name_requires_manual_splitting")
        return out

    # Hyphenation can hide multiple semantic Muslim-name elements inside a
    # two-token string. These cases require the same owner review as longer
    # Muslim structures.
    if model == "muslim" and len(tokens) == 2 and any("-" in token for token in tokens):
        out.update(parse_status="manual_review", parse_confidence="low",
                   parse_rule="hyphenated_two_token_muslim_manual",
                   manual_review_reason="hyphenated_muslim_name_requires_manual_splitting")
        return out

    if len(tokens) == 1:
        token = tokens[0]
        if norm(token) == "некрещеная":
            set_component(out, "last_name", token)
            out.update(parse_status="observed", parse_confidence="high",
                       parse_rule="reviewed_descriptor_as_last", name_order_detected="last_only")
        elif matches[0][0]:
            set_component(out, "first_name", token)
            out.update(parse_status="observed", parse_confidence="high",
                       parse_rule="recognized_first_only", name_order_detected="first_only")
        elif model == "muslim":
            out.update(parse_status="manual_review", parse_confidence="low",
                       parse_rule="single_muslim_manual",
                       manual_review_reason="single_muslim_token_role_unknown")
        else:
            set_component(out, "last_name", token, "observed_tentative")
            out.update(parse_status="ambiguous", parse_confidence="medium",
                       parse_rule="single_unknown_as_last", name_order_detected="last_only")
        return out

    if len(tokens) == 2:
        # Source-first default. Reverse only when the second token is a curated
        # first name and the first is not. Catholic and Lutheran records retain
        # source order unless a reviewed exception supplies contrary evidence.
        if model not in {"catholic", "lutheran"} and matches[1][0] and not matches[0][0]:
            first_i, last_i, order = 1, 0, "last_first"
        else:
            first_i, last_i, order = 0, 1, "first_last"
        set_component(out, "first_name", tokens[first_i])
        set_component(out, "last_name", tokens[last_i])
        out.update(parse_status="observed", parse_confidence="high",
                   parse_rule="two_token_source_order", name_order_detected=order)
        return out

    if len(tokens) == 3:
        # Catholic and Lutheran names include both Russianized patronymics and
        # compound given names. Preserve source order: accept a morphologically
        # clear middle patronymic, otherwise propose tokens 1+2 as the compound
        # first name and route the record to review.
        if model in {"catholic", "lutheran"}:
            if patronymic_like(tokens[1], sex):
                set_component(out, "first_name", tokens[0])
                set_component(out, "patronymic_name", tokens[1])
                set_component(out, "last_name", tokens[2])
                out.update(parse_status="observed", parse_confidence="high",
                           parse_rule="catholic_lutheran_patronymic",
                           name_order_detected="first_patronymic_last")
            else:
                set_component(out, "first_name", " ".join(tokens[:2]), "observed_tentative")
                set_component(out, "last_name", tokens[2], "observed_tentative")
                out.update(parse_status="manual_review", parse_confidence="medium",
                           parse_rule="catholic_lutheran_compound_given_manual",
                           name_order_detected="compound_first_last",
                           manual_review_reason="verify_catholic_lutheran_compound_given_name")
            return out

        first_positions = [i for i, (matched, _) in enumerate(matches) if matched]
        if first_positions == [1] or (1 in first_positions and 0 not in first_positions):
            fi, pi, li, order = 1, 2, 0, "last_first_patronymic"
        elif first_positions == [2]:
            fi, pi, li, order = 2, 0, 1, "patronymic_last_first"
        else:
            fi, pi, li, order = 0, 1, 2, "first_patronymic_last"

        # Two consecutive recognized given names are never silently converted.
        if fi == 0 and matches[0][0] and matches[1][0] and not patronymic_like(tokens[1], sex):
            set_component(out, "first_name", tokens[0])
            set_component(out, "last_name", tokens[2])
            proposed = (proposed_short_patronymic(tokens[1], sex)
                        if model == "russian_historical" else "")
            out.update(parse_status="manual_review", parse_confidence="medium",
                       parse_rule="second_given_name_manual_review",
                       name_order_detected="first_second_given_last",
                       patronymic_name_proposed=proposed,
                       proposal_rule="second_given_to_historical_short_patronymic" if proposed else "",
                       manual_review_reason=(
                           "verify_second_given_name_before_patronymic_conversion" if proposed
                           else "verify_possible_compound_given_name"
                       ))
            return out

        set_component(out, "first_name", tokens[fi])
        set_component(out, "patronymic_name", tokens[pi])
        set_component(out, "last_name", tokens[li])
        out.update(parse_status="observed", parse_confidence="high",
                   parse_rule="three_token_deterministic", name_order_detected=order)
        return out

    if model in {"catholic", "lutheran"}:
        set_component(out, "first_name", " ".join(tokens[:-1]), "observed_tentative")
        set_component(out, "last_name", tokens[-1], "observed_tentative")
        out.update(parse_status="manual_review", parse_confidence="medium",
                   parse_rule="catholic_lutheran_multi_given_manual",
                   name_order_detected="compound_first_last",
                   manual_review_reason="verify_catholic_lutheran_multi_given_name")
    else:
        out.update(parse_status="manual_review", parse_confidence="low",
                   parse_rule="complex_token_count_manual",
                   manual_review_reason="four_or_more_semantic_tokens_require_review")
    if ordinal_tokens:
        out["manual_review_reason"] += "; ordinal_marker_ignored_for_structure"
    return out


def validate_results(rows, parsed, columns):
    issues = []
    valid_status = {"observed", "ambiguous", "manual_review", "unresolved"}
    for csv_row, (row, result) in enumerate(zip(rows, parsed), start=2):
        pid = row.get(getattr(columns, "person_id", "person_id"), "")
        if result["parse_status"] not in valid_status:
            issues.append((csv_row, pid, "invalid_status", result["parse_status"]))
        for field, source_field in (("first_name", "first_name_source"),
                                    ("patronymic_name", "patronymic_source"),
                                    ("last_name", "last_name_source")):
            value, source = result[field], result[source_field]
            if bool(value) != bool(source):
                issues.append((csv_row, pid, "component_source_mismatch", field))
        if any(source.startswith("inferred_") for source in
               (result["first_name_source"], result["patronymic_source"], result["last_name_source"])):
            issues.append((csv_row, pid, "family_inference_forbidden", ""))
        if result["parse_status"] == "manual_review" and not result["manual_review_reason"]:
            issues.append((csv_row, pid, "manual_review_without_reason", ""))
    return issues


def write_qa(qa_dir, rows, parsed, columns, input_path):
    qa_dir.mkdir(parents=True, exist_ok=True)
    issues = validate_results(rows, parsed, columns)
    status = Counter(result["parse_status"] for result in parsed)
    rules = Counter(result["parse_rule"] or "blank" for result in parsed)
    summary = {
        "input": str(input_path), "records": len(rows),
        "parse_status": dict(status), "parse_rules": dict(rules),
        "manual_review_count": status["manual_review"],
        "patronymic_proposal_count": sum(bool(r["patronymic_name_proposed"]) for r in parsed),
        "family_inference_count": 0,
        "hard_issue_count": len(issues), "hard_checks_passed": not issues,
    }
    (qa_dir / "name_split_qa_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with (qa_dir / "name_split_qa_issues.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle); writer.writerow(["csv_row", "person_id", "check", "detail"]); writer.writerows(issues)
    context = [name for name in ("person_id", "source_position_id", "name_raw", "name_alias",
                                  "sex", "religion", "family_status", "district", "settlement")
               if not rows or name in rows[0]]
    with (qa_dir / "name_split_manual_review.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=context + OUTPUT_FIELDS); writer.writeheader()
        for row, result in zip(rows, parsed):
            if result["parse_status"] in {"manual_review", "ambiguous", "unresolved"}:
                combined = {**row, **result}
                writer.writerow({field: combined.get(field, "") for field in context + OUTPUT_FIELDS})
    return issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--lexicon", type=Path, default=Path(__file__).with_name("name_lexicon.csv"))
    parser.add_argument("--exceptions", type=Path, default=Path(__file__).with_name("name_split_exceptions.csv"))
    parser.add_argument("--manual-exceptions", type=Path,
                        default=Path(__file__).with_name("name_split_muslim_review_all_20260723.csv"))
    parser.add_argument("--review-exceptions", type=Path,
                        default=Path(__file__).with_name("name_split_patronymic_review_exceptions_20260723.csv"))
    parser.add_argument("--first-name-review-exceptions", type=Path,
                        default=Path(__file__).with_name("name_split_first_name_review_exceptions_20260723.csv"))
    parser.add_argument("--ambiguous-review-exceptions", type=Path,
                        default=Path(__file__).with_name("name_split_ambiguous_review_exceptions_20260723.csv"))
    parser.add_argument("--qa-dir", type=Path)
    parser.add_argument("--fail-on-qa-error", action="store_true")
    parser.add_argument("--name", default="name_raw")
    parser.add_argument("--sex", default="sex")
    parser.add_argument("--religion", default="religion")
    parser.add_argument("--person-id", default="person_id")
    args = parser.parse_args()

    with args.input.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle); rows = list(reader); fields = list(reader.fieldnames or [])
    missing = [field for field in (args.name, args.sex, args.religion, args.person_id) if field not in fields]
    if missing:
        parser.error("missing required columns: " + ", ".join(missing))
    lexicon = load_lexicon(args.lexicon)
    exceptions = load_exceptions(args.exceptions)
    for exception_path in (
        args.manual_exceptions,
        args.review_exceptions,
        args.first_name_review_exceptions,
        args.ambiguous_review_exceptions,
    ):
        if exception_path.exists():
            manual_exceptions = load_exceptions(exception_path)
            overlap = set(exceptions) & set(manual_exceptions)
            if overlap:
                parser.error("duplicate person_id across exception files: " + ", ".join(sorted(overlap)))
            exceptions.update(manual_exceptions)
    parsed = [parse_one(row, args, lexicon, exceptions) for row in rows]
    with args.output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields + [field for field in OUTPUT_FIELDS if field not in fields])
        writer.writeheader()
        for row, result in zip(rows, parsed): writer.writerow({**row, **result})
    if args.qa_dir:
        issues = write_qa(args.qa_dir, rows, parsed, args, args.input)
        if issues and args.fail_on_qa_error:
            raise SystemExit(f"QA failed with {len(issues)} hard issue(s)")


if __name__ == "__main__":
    main()
