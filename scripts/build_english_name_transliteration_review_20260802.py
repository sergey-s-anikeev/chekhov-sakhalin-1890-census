"""Build Item 4 English-name transliteration candidate and review inventories."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/clean_sakhalin_1890_ru_v5_20260731.csv"
OUTPUT = ROOT / "outputs/english_name_transliteration_review_20260802"

BASE = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e",
    "ё": "yo", "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k",
    "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r",
    "с": "s", "т": "t", "у": "u", "ф": "f", "х": "kh", "ц": "ts",
    "ч": "ch", "ш": "sh", "щ": "shch", "ъ": "", "ы": "y", "ь": "",
    "э": "e", "ю": "yu", "я": "ya",
}
E_YE_AFTER = set("аеёиоуыэюяйъь")
CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
ORDINAL_RE = re.compile(r"(?<!\w)(\d+)-(?:й|я)(?!\w)", re.IGNORECASE)
NON_NAME_EXCEPTIONS = {"Человек неизвестного звания": "Person of unknown rank"}
OWNER_OVERRIDES = {
    "P001151": "Lyubov Aleksandrova Vetskaya",
    "P004592": "Fedot Larionov Masyukevich",
    "P005221": "Iogan Peters",
}


def transliterate_char(ch: str, previous_cyrillic: str | None, at_word_start: bool) -> str:
    lower = ch.lower()
    if lower not in BASE:
        return ch
    if lower == "е" and (at_word_start or previous_cyrillic in E_YE_AFTER):
        value = "ye"
    else:
        value = BASE[lower]
    if ch.isupper() and value:
        return value[0].upper() + value[1:]
    return value


def transliterate_name(person_id: str, value: str) -> tuple[str, str]:
    if person_id in OWNER_OVERRIDES:
        return OWNER_OVERRIDES[person_id], "owner_override_20260802"
    if value in NON_NAME_EXCEPTIONS:
        return NON_NAME_EXCEPTIONS[value], "explicit_non_name_exception"

    value = ORDINAL_RE.sub(lambda m: f"({m.group(1)})", value)
    out: list[str] = []
    previous_cyrillic: str | None = None
    at_word_start = True
    for ch in value:
        if ch.lower() in BASE:
            out.append(transliterate_char(ch, previous_cyrillic, at_word_start))
            previous_cyrillic = ch.lower()
            at_word_start = False
        else:
            out.append(ch)
            previous_cyrillic = None
            at_word_start = not ch.isalpha()
    return "".join(out), "general_rule"


def review_reasons(row: dict[str, str], candidate: str) -> list[str]:
    raw = row["name_raw"]
    reasons: list[str] = []
    model = row["naming_model"]
    if model != "russian_historical":
        reasons.append(f"naming_model:{model}")
    if len(raw.split()) == 1:
        reasons.append("one_token")
    if len(raw.split()) >= 4:
        reasons.append("four_plus_tokens")
    if "-" in raw:
        reasons.append("hyphenated")
    if any(ch.isdigit() for ch in raw):
        reasons.append("numbered_disambiguator")
    if re.search(r"[A-Za-z]", raw):
        reasons.append("mixed_latin_cyrillic")
    if "*" in raw:
        reasons.append("masked_characters")
    if "ъ" in raw.lower():
        reasons.append("hard_sign")
    if raw in NON_NAME_EXCEPTIONS:
        reasons.append("descriptive_non_name")
    if CYRILLIC_RE.search(candidate):
        reasons.append("qa_cyrillic_remaining")
    return reasons


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    candidate_rows: list[dict[str, str]] = []
    by_english: dict[str, set[str]] = defaultdict(set)
    reason_counts: Counter[str] = Counter()

    for row in rows:
        candidate, method = transliterate_name(row["person_id"], row["name_raw"])
        reasons = review_reasons(row, candidate)
        for reason in reasons:
            reason_counts[reason] += 1
        by_english[candidate].add(row["name_raw"])
        candidate_rows.append({
            "person_id": row["person_id"],
            "district": row["district"],
            "settlement": row["settlement"],
            "religion": row["religion"],
            "naming_model": row["naming_model"],
            "name_raw": row["name_raw"],
            "full_name_candidate": candidate,
            "method": method,
            "review_reasons": "; ".join(reasons),
        })

    collisions = {k: sorted(v) for k, v in by_english.items() if len(v) > 1}
    collision_names = set(collisions)
    for row in candidate_rows:
        if row["full_name_candidate"] in collision_names:
            row["review_reasons"] = "; ".join(filter(None, [row["review_reasons"], "transliteration_collision"]))
            reason_counts["transliteration_collision"] += 1

    high_markers = {
        "numbered_disambiguator", "mixed_latin_cyrillic", "masked_characters",
        "hard_sign", "descriptive_non_name", "qa_cyrillic_remaining",
        "transliteration_collision",
    }
    priority_rows = [
        r for r in candidate_rows
        if high_markers.intersection(r["review_reasons"].split("; "))
    ]
    extended_rows = [r for r in candidate_rows if r["review_reasons"]]

    fieldnames = list(candidate_rows[0])
    for filename, data in [
        ("name_transliteration_candidate_20260802.csv", candidate_rows),
        ("name_transliteration_priority_review_20260802.csv", priority_rows),
        ("name_transliteration_extended_inventory_20260802.csv", extended_rows),
    ]:
        with (OUTPUT / filename).open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    with (OUTPUT / "name_transliteration_staged_20260802.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["person_id", "name_raw", "full_name", "method"])
        writer.writeheader()
        writer.writerows({
            "person_id": r["person_id"],
            "name_raw": r["name_raw"],
            "full_name": r["full_name_candidate"],
            "method": r["method"],
        } for r in candidate_rows)

    collision_rows = [
        {"full_name_candidate": english, "distinct_cyrillic_names": len(raws), "canonical_names": " | ".join(raws)}
        for english, raws in sorted(collisions.items())
    ]
    with (OUTPUT / "name_transliteration_collisions_20260802.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["full_name_candidate", "distinct_cyrillic_names", "canonical_names"])
        writer.writeheader()
        writer.writerows(collision_rows)

    summary = {
        "source_records": len(rows),
        "candidate_records": len(candidate_rows),
        "blank_candidates": sum(not r["full_name_candidate"] for r in candidate_rows),
        "cyrillic_remaining": sum(bool(CYRILLIC_RE.search(r["full_name_candidate"])) for r in candidate_rows),
        "distinct_canonical_names": len({r["name_raw"] for r in candidate_rows}),
        "distinct_candidate_names": len({r["full_name_candidate"] for r in candidate_rows}),
        "priority_review_records": len(priority_rows),
        "extended_inventory_records": len(extended_rows),
        "collision_groups": len(collisions),
        "collision_records": sum("transliteration_collision" in r["review_reasons"] for r in candidate_rows),
        "owner_overrides_applied": sum(r["method"] == "owner_override_20260802" for r in candidate_rows),
        "reason_counts": dict(sorted(reason_counts.items())),
    }
    (OUTPUT / "name_transliteration_summary_20260802.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    workbook_data = {
        "summary": summary,
        "priority_rows": priority_rows,
        "extended_rows": extended_rows,
        "collision_rows": collision_rows,
    }
    (OUTPUT / "name_transliteration_workbook_data_20260802.json").write_text(
        json.dumps(workbook_data, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
