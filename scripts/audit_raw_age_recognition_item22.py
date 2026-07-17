from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data/raw/raw_district_files"
STAGED = ROOT / "data/staging/arrival_year_item21_20260717/clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_item18_comments_item21_staged.csv"
REVIEW_DIR = ROOT / "data/review/raw_age_recognition_item22_20260717"
QA_DIR = ROOT / "outputs/qa/raw_age_recognition_item22_20260717"

DISTRICTS = {
    "raw_extracted_alexandrovsky.csv": "Александровский",
    "raw_extracted_tymovsky.csv": "Тымовский",
    "raw_extracted_korsakovsky.csv": "Корсаковский",
}

ANGLE = re.compile(r"<[^<>]*>")
UNCERTAINTY_WITH_FOOTNOTE = re.compile(r"\(\s*\?\s*\)\d*|\?+")
SPACE = re.compile(r"\s+")
PLAIN_INTEGER = re.compile(r"^\d{1,3}$")


def clean_text(value: str) -> str:
    return SPACE.sub(" ", value.strip()).casefold()


def clean_name(value: str) -> str:
    value = value.split(",", 1)[0]
    value = ANGLE.sub("", value)
    return clean_text(value)


def clear_age_candidate(raw_age: str) -> str | None:
    """Return the visible integer after struck text and uncertainty marks are removed."""
    visible = ANGLE.sub("", raw_age)
    visible = UNCERTAINTY_WITH_FOOTNOTE.sub("", visible)
    tokens = re.findall(r"\d+", visible)
    # A single footnote digit can remain between a leading deletion and the
    # replacement value, e.g. `<71>2 64`; the final token is the visible age.
    if (
        raw_age.lstrip().startswith("<")
        and len(tokens) == 2
        and len(tokens[0]) == 1
        and re.fullmatch(r"\s*\d\s+\d{1,3}\s*", visible)
    ):
        visible = tokens[1]
    else:
        visible = SPACE.sub("", visible)
    return visible if PLAIN_INTEGER.fullmatch(visible) else None


def risk_class(raw_age: str) -> str:
    if re.search(r"\d<[^<>]*>\d", raw_age):
        return "embedded_struck_content"
    if "<" in raw_age or ">" in raw_age:
        return "struck_content"
    if "?" in raw_age:
        return "uncertain_integer"
    return "other_nonplain_expression"


def semantic_age_candidate(raw_age: str) -> tuple[str, str] | None:
    """Parse clear year/month/week/day expressions into staged age fields."""
    visible = ANGLE.sub("", raw_age)
    visible = UNCERTAINTY_WITH_FOOTNOTE.sub("", visible)
    visible = visible.replace("[", "").replace("]", "")
    visible = SPACE.sub(" ", visible.strip()).casefold()

    match = re.match(r"^(\d+)\s*(?:г(?:од|ода)?|лет|л)\D+(\d+)\s*(?:м|мес|месяц)", visible)
    if match:
        years, months = map(int, match.groups())
        return str(years), str(years * 12 + months)
    match = re.match(r"^(\d+)\s*(?:м|мес|месяц|есяц)", visible)
    if match:
        months = int(match.group(1))
        return "0", str(months)
    match = re.match(r"^(\d+)\s*н(?:ед)?", visible)
    if match:
        weeks = int(match.group(1))
        return "0", "1" if weeks == 4 else "0"
    match = re.match(r"^(\d+)\s*дн", visible)
    if match:
        return "0", "0"
    match = re.match(r"^(\d+)\s+1\s*/\s*2(?:\s|$)", visible)
    if match:
        years = int(match.group(1))
        return str(years), str(years * 12 + 6)
    if re.match(r"^1\s*/\s*2\s*(?:г|год)", visible):
        return "0", "6"
    return None


def main() -> None:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    QA_DIR.mkdir(parents=True, exist_ok=True)

    with STAGED.open("r", encoding="utf-8-sig", newline="") as handle:
        staged = list(csv.DictReader(handle))

    by_archive = defaultdict(list)
    by_page_name = defaultdict(list)
    for row in staged:
        by_archive[(row["district"], clean_text(row["notes_raw"]))].append(row)
        by_page_name[(row["district"], row["page_number"], clean_name(row["name_raw"]))].append(row)

    raw_rows = []
    for filename, district in DISTRICTS.items():
        path = RAW_DIR / filename
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for raw in csv.DictReader(handle):
                raw["_raw_file"] = filename
                raw["_district"] = district
                raw_rows.append(raw)

    audit_rows = []
    unmatched_rows = []
    match_status = Counter()
    for raw in raw_rows:
        candidates = by_archive[(raw["_district"], clean_text(raw["notes_raw"]))]
        if len(candidates) > 1:
            candidates = [row for row in candidates if row["page_number"] == raw["page_number"]]
        if len(candidates) != 1:
            name_key = clean_name(raw["name_raw"])
            fallback = by_page_name[(raw["_district"], raw["page_number"], name_key)]
            if len(fallback) == 1:
                candidates = fallback
        status = "matched" if len(candidates) == 1 else ("ambiguous" if len(candidates) > 1 else "unmatched")
        match_status[status] += 1
        if status != "matched":
            unmatched_rows.append(
                {
                    "match_status": status,
                    "district": raw["_district"],
                    "raw_file": raw["_raw_file"],
                    "settlement": raw["settlement"],
                    "page_number": raw["page_number"],
                    "household_number": raw["household_number"],
                    "name_raw": raw["name_raw"],
                    "raw_age": raw["age"],
                    "notes_raw": raw["notes_raw"],
                    "source_record_number": raw["source_record_number"],
                    "source_block_raw": raw["source_block_raw"],
                }
            )
            continue

        staged_row = candidates[0]
        raw_age = raw["age"].strip()
        proposed = clear_age_candidate(raw_age)
        semantic = semantic_age_candidate(raw_age)
        nonplain = bool(raw_age and not PLAIN_INTEGER.fullmatch(raw_age))
        if not nonplain:
            continue
        audit_rows.append(
            {
                "person_id": staged_row["person_id"],
                "source_position_id": staged_row["source_position_id"],
                "district": staged_row["district"],
                "settlement": staged_row["settlement"],
                "page_number": staged_row["page_number"],
                "household_id": staged_row["household_id"],
                "name_raw": staged_row["name_raw"],
                "raw_age": raw_age,
                "staged_age": staged_row["age"],
                "staged_age_months": staged_row.get("age_months", ""),
                "visible_integer_after_struck_removal": proposed or "",
                "semantic_expected_age": semantic[0] if semantic else "",
                "semantic_expected_age_months": semantic[1] if semantic else "",
                "risk_class": risk_class(raw_age),
                "comparison": (
                    "owner_verified_override"
                    if staged_row["person_id"] == "P003286"
                    else
                    "mismatch_review"
                    if proposed is not None and proposed != staged_row["age"]
                    else "consistent"
                    if proposed is not None
                    else "manual_parse_required"
                ),
                "origin_place": staged_row["origin_place"],
                "arrival_year": staged_row["arrival_year"],
                "legal_status": staged_row["legal_status"],
                "family_status": staged_row["family_status"],
                "notes_raw": staged_row["notes_raw"],
                "raw_file": raw["_raw_file"],
                "source_record_number": raw["source_record_number"],
                "source_block_raw": raw["source_block_raw"],
            }
        )

    fields = list(audit_rows[0])
    with (REVIEW_DIR / "raw_age_nonplain_inventory.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(audit_rows)

    mismatch_rows = [row for row in audit_rows if row["comparison"] == "mismatch_review"]
    with (REVIEW_DIR / "raw_age_mismatch_review.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(mismatch_rows)

    with (REVIEW_DIR / "raw_rows_unmatched_to_staged.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        fields_unmatched = list(unmatched_rows[0]) if unmatched_rows else ["match_status"]
        writer = csv.DictWriter(handle, fieldnames=fields_unmatched, lineterminator="\n")
        writer.writeheader()
        writer.writerows(unmatched_rows)

    semantic_mismatches = [
        row
        for row in audit_rows
        if row["semantic_expected_age"]
        and (
            row["semantic_expected_age"] != row["staged_age"]
            or row["semantic_expected_age_months"] != row["staged_age_months"]
        )
    ]
    with (REVIEW_DIR / "raw_age_semantic_mismatch_review.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(semantic_mismatches)

    qa = {
        "raw_directory": str(RAW_DIR.relative_to(ROOT)),
        "staged_dataset": str(STAGED.relative_to(ROOT)),
        "raw_row_count": len(raw_rows),
        "staged_row_count": len(staged),
        "raw_to_staged_match_status": dict(match_status),
        "matched_nonplain_age_count": len(audit_rows),
        "comparison_counts": dict(Counter(row["comparison"] for row in audit_rows)),
        "risk_class_counts": dict(Counter(row["risk_class"] for row in audit_rows)),
        "mismatch_review_count": len(mismatch_rows),
        "semantic_mismatch_review_count": len(semantic_mismatches),
    }
    (QA_DIR / "raw_age_recognition_qa.json").write_text(
        json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
