from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


INPUT = Path("data/staging/legal_status_norm_item17_20260712/clean_sakhalin_1890_ru_legal_status_norm_v1.csv")
OUT = Path("data/review/illness_item15_20260712")
STAGING = Path("data/staging/illness_item15_20260712")
QA = Path("outputs/qa/illness_item15_20260712")

MAPPING = {
    "": ("", "straightforward", "Blank source value."),
    "Сифилис": ("Сифилис", "straightforward", "Already categorical."),
    "Слепой": ("Слепота", "straightforward", "Gender-neutral condition noun."),
    "Слепая": ("Слепота", "straightforward", "Gender-neutral condition noun."),
    "В богадельщиках": ("Богадельщик", "straightforward", "Approved analytical category."),
    "Богадельщик": ("Богадельщик", "straightforward", "Already the approved category."),
    "Психическое расстройство": ("Психическое расстройство", "straightforward", "Already categorical."),
    "Псих": ("Психическое расстройство", "owner_review", "Interpret abbreviated historical wording."),
    "Удушье": ("Удушье", "straightforward", "Already categorical."),
    "Водянкой, в богадельщиках": ("Водянка; Богадельщик", "owner_review", "Compound condition and institutional category."),
    "Слеп и помешан умом": ("Слепота; Психическое расстройство", "owner_review", "Compound historical wording."),
    "Ревматизм": ("Ревматизм", "straightforward", "Already categorical."),
    "Слабосилен": ("Слабосилен", "owner_corrected", "Preserve owner-approved historical wording."),
    "Слаб": ("Слабосилен", "owner_corrected", "Normalize to the owner-approved category."),
    "Чахотка и сифилис": ("Чахотка; Сифилис", "owner_review", "Compound historical conditions."),
    "Контужен": ("Контужен", "owner_corrected", "Preserve owner-approved historical wording."),
    "Глухая": ("Глухота", "straightforward", "Gender-neutral condition noun."),
    "Глуха": ("Глухота", "straightforward", "Gender-neutral condition noun."),
    "Бронхиальный катар": ("Бронхиальный катар", "straightforward", "Already categorical."),
    "Разбита параличом": ("Разбита параличом", "owner_corrected", "Preserve owner-approved historical wording."),
    "Рак": ("Рак", "straightforward", "Already categorical."),
    "Застарелый вывих в левом локтевом сочленении": ("Застарелый вывих в левом локтевом сочленении", "owner_corrected", "Preserve owner-approved historical wording."),
    "Ревматизм и катар желудка": ("Ревматизм; Катар желудка", "owner_review", "Compound historical conditions."),
    "Плеврит": ("Плеврит", "straightforward", "Already categorical."),
    "Женская болезнь": ("Женская болезнь", "owner_review", "Historically vague condition; preserve wording."),
    "Левая рука не работает": ("Левая рука не работает", "owner_corrected", "Preserve owner-approved historical wording."),
    "Чахотка": ("Чахотка", "straightforward", "Preserve historical condition term."),
    "Немой": ("Немой", "owner_corrected", "Preserve owner-approved historical wording."),
    "Слабое зрение": ("Слабое зрение", "straightforward", "Already a condition phrase."),
    "Хронический катар желудка и кишок": ("Хронический катар желудка и кишок", "straightforward", "Preserve historical diagnostic wording."),
    "Коньюктивит": ("Конъюнктивит", "straightforward", "Correct spelling."),
}

OWNER_CORRECTED_VALUES = {
    "Застарелый вывих в левом локтевом сочленении",
    "Контужен",
    "Левая рука не работает",
    "Немой",
    "Разбита параличом",
    "Слабосилен",
    "Слаб",
}


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with INPUT.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    counts = Counter(row["illness"].strip() for row in rows)
    unknown = sorted(set(counts) - set(MAPPING))
    if unknown:
        raise ValueError(f"Unmapped illness values: {unknown}")
    examples: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        value = row["illness"].strip()
        if len(examples[value]) < 3:
            examples[value].append(row)

    inventory = []
    representative = []
    for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        proposed, tier, basis = MAPPING[value]
        decision = "correct" if value in OWNER_CORRECTED_VALUES else "approve"
        inventory.append(
            {
                "illness": value,
                "record_count": str(count),
                "illness_norm_proposed": proposed,
                "review_tier": tier,
                "proposal_basis": basis,
                "owner_decision": decision,
                "owner_illness_norm": proposed,
                "reviewer_notes": "",
            }
        )
        for row in examples[value]:
            representative.append(
                {
                    "illness": value,
                    "record_count": str(count),
                    "person_id": row["person_id"],
                    "source_position_id": row["source_position_id"],
                    "name_raw": row["name_raw"],
                    "legal_status": row["legal_status"],
                    "age": row["age"],
                    "comments": row["comments"],
                }
            )
    write_csv(OUT / "illness_norm_mapping_proposal.csv", inventory, list(inventory[0]))
    write_csv(OUT / "illness_norm_approved_mapping.csv", inventory, list(inventory[0]))
    write_csv(OUT / "illness_owner_review_cases.csv", [row for row in inventory if row["review_tier"] in {"owner_review", "owner_corrected"}], list(inventory[0]))
    write_csv(OUT / "illness_representative_records.csv", representative, list(representative[0]))

    tier_distinct = Counter(row["review_tier"] for row in inventory)
    tier_records = Counter()
    for row in inventory:
        tier_records[row["review_tier"]] += int(row["record_count"])
    summary = [
        {"metric": "input_records", "value": str(len(rows))},
        {"metric": "distinct_values_including_blank", "value": str(len(inventory))},
        {"metric": "nonblank_records", "value": str(len(rows) - counts[""])},
        {"metric": "straightforward_distinct_values", "value": str(tier_distinct["straightforward"])},
        {"metric": "straightforward_records", "value": str(tier_records["straightforward"])},
        {"metric": "owner_review_distinct_values", "value": str(tier_distinct["owner_review"])},
        {"metric": "owner_review_records", "value": str(tier_records["owner_review"])},
    ]
    write_csv(OUT / "illness_profile_summary.csv", summary, ["metric", "value"])

    approved_map = {row["illness"]: row["owner_illness_norm"] for row in inventory}
    input_fields = list(rows[0])
    insert_at = input_fields.index("illness") + 1
    staged_fields = input_fields[:insert_at] + ["illness_norm"] + input_fields[insert_at:]
    staged_rows = []
    diff_rows = []
    for row in rows:
        staged = dict(row)
        staged["illness_norm"] = approved_map[row["illness"].strip()]
        staged_rows.append(staged)
        if staged["illness_norm"]:
            diff_rows.append(
                {
                    "person_id": row["person_id"],
                    "source_position_id": row["source_position_id"],
                    "illness": row["illness"],
                    "illness_norm": staged["illness_norm"],
                }
            )
    write_csv(STAGING / "clean_sakhalin_1890_ru_illness_norm_v1.csv", staged_rows, staged_fields)
    write_csv(QA / "illness_norm_diff.csv", diff_rows, list(diff_rows[0]))
    non_target_changes = sum(
        any(before[field] != after[field] for field in input_fields)
        for before, after in zip(rows, staged_rows)
    )
    lowercase_categories = sorted(
        {
            part.strip()
            for value in approved_map.values()
            for part in value.split(";")
            if part.strip() and next((char for char in part.strip() if char.isalpha()), "").islower()
        }
    )
    qa = [
        {"check": "input_records", "value": str(len(rows)), "pass": str(len(rows) == 7446).upper()},
        {"check": "staged_records", "value": str(len(staged_rows)), "pass": str(len(staged_rows) == len(rows)).upper()},
        {"check": "approved_distinct_values_including_blank", "value": str(len(approved_map)), "pass": str(len(approved_map) == 31).upper()},
        {"check": "nonblank_illness_norm_records", "value": str(len(diff_rows)), "pass": str(len(diff_rows) == 53).upper()},
        {"check": "unmapped_illness_values", "value": "0", "pass": str(all(row["illness"].strip() in approved_map for row in rows)).upper()},
        {"check": "illness_preserved", "value": str(sum(a["illness"] != b["illness"] for a, b in zip(rows, staged_rows))), "pass": str(all(a["illness"] == b["illness"] for a, b in zip(rows, staged_rows))).upper()},
        {"check": "lowercase_normalized_categories", "value": str(len(lowercase_categories)), "pass": str(not lowercase_categories).upper()},
        {"check": "non_target_field_changes", "value": str(non_target_changes), "pass": str(non_target_changes == 0).upper()},
    ]
    write_csv(QA / "illness_norm_qa_summary.csv", qa, ["check", "value", "pass"])


if __name__ == "__main__":
    main()
