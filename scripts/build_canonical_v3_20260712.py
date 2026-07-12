from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


BASE = Path("data/processed/clean_sakhalin_1890_ru_v2_20260711.csv")
OUT = Path("data/processed")
QA = Path("outputs/qa/canonical_v3_20260712")

HOUSEHOLD = Path("data/staging/household_structure_20260711_v2/clean_sakhalin_1890_ru_household_structure_v2.csv")
NOTES = Path("data/staging/notes_raw_suffix_recovery_20260711/clean_sakhalin_1890_ru_notes_raw_item4_v1.csv")
RELIGION = Path("data/staging/item13_religion_20260711/clean_sakhalin_1890_ru_item13_religion_v2.csv")
LITERACY = Path("data/staging/capitalization_item9_20260712/clean_sakhalin_1890_ru_capitalization_item9_v1.csv")
ITEM10 = Path("data/staging/items_10_14_20260711/clean_sakhalin_1890_ru_item10_legal_status_v1.csv")
SEX = Path("data/staging/sex_item3_20260712/clean_sakhalin_1890_ru_sex_item3_v1.csv")
LEGAL_MAPPING = Path("data/review/legal_status_item17_20260712/legal_status_norm_approved_mapping.csv")
LEGAL_STAGE = Path("data/staging/legal_status_norm_item17_20260712/clean_sakhalin_1890_ru_legal_status_norm_v1.csv")
FAMILY_MAPPING = Path("data/review/family_status_norm_item11_20260712/family_status_norm_approved_mapping.csv")
ILLNESS_MAPPING = Path("data/review/illness_item15_20260712/illness_norm_approved_mapping.csv")

OUTPUTS = {
    "Александровский": OUT / "clean_alexandrovsky_ru_v3_20260712.csv",
    "Тымовский": OUT / "clean_tymovsky_ru_v3_20260712.csv",
    "Корсаковский": OUT / "clean_korsakovsky_ru_v3_20260712.csv",
}
COMBINED = OUT / "clean_sakhalin_1890_ru_v3_20260712.csv"

FIELDS = [
    "person_id", "source_position_id", "district_code", "district", "settlement_order", "settlement",
    "person_order_in_settlement", "page_number", "household_id", "household_type", "household_details",
    "legal_status", "legal_status_norm", "name_raw", "name_alias", "sex", "sex_evidence",
    "family_status", "family_status_norm", "age", "religion", "origin_place", "arrival_year",
    "occupation", "literacy", "marriage_status", "allowance_status", "illness", "illness_norm",
    "comments", "notes_raw",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def by_person(path: Path) -> dict[str, dict[str, str]]:
    rows = read_rows(path)
    result = {row["person_id"]: row for row in rows}
    if len(result) != len(rows):
        raise ValueError(f"Duplicate person_id in {path}")
    return result


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def first_alpha_is_lower(value: str) -> bool:
    char = next((c for c in value if c.isalpha()), "")
    return bool(char and char.islower())


def main() -> None:
    base = read_rows(BASE)
    sources = {
        "household": by_person(HOUSEHOLD),
        "notes": by_person(NOTES),
        "religion": by_person(RELIGION),
        "literacy": by_person(LITERACY),
        "item10": by_person(ITEM10),
        "sex": by_person(SEX),
        "legal_stage": by_person(LEGAL_STAGE),
    }
    base_ids = [row["person_id"] for row in base]
    for name, source in sources.items():
        if set(source) != set(base_ids):
            raise ValueError(f"Person-id mismatch in {name}")

    legal_rows = read_rows(LEGAL_MAPPING)
    legal_map = {row["legal_status"]: row["owner_legal_status_norm"] for row in legal_rows}
    for normalized_value in {row["owner_legal_status_norm"] for row in legal_rows if row["owner_legal_status_norm"]}:
        legal_map.setdefault(normalized_value, normalized_value)
    family_rows = read_rows(FAMILY_MAPPING)
    family_map = {row["family_status"]: row["owner_family_status_norm"] for row in family_rows}
    illness_rows = read_rows(ILLNESS_MAPPING)
    illness_map = {row["illness"]: row["owner_illness_norm"] for row in illness_rows}

    output = []
    for original in base:
        pid = original["person_id"]
        household = sources["household"][pid]
        religion = sources["religion"][pid]
        literacy = sources["literacy"][pid]
        notes = sources["notes"][pid]
        item10 = sources["item10"][pid]
        sex = sources["sex"][pid]
        legal_stage = sources["legal_stage"][pid]

        legal_status = item10["legal_status"]
        if sex["legal_status"] != original["legal_status"]:
            legal_status = sex["legal_status"]
        if legal_status not in legal_map:
            raise ValueError(f"Unmapped corrected legal_status for {pid}: {legal_status!r}")

        illness = legal_stage["illness"]
        if illness not in illness_map:
            raise ValueError(f"Unmapped illness for {pid}: {illness!r}")
        family_status = original["family_status"]
        if family_status not in family_map:
            raise ValueError(f"Unmapped family_status for {pid}: {family_status!r}")

        row = dict(original)
        row.pop("household_number", None)
        row.update(
            {
                "source_position_id": household["source_position_id"],
                "household_id": household["household_id"],
                "household_type": household["household_type"],
                "household_details": household["household_details"],
                "legal_status": legal_status,
                "legal_status_norm": legal_map[legal_status],
                "sex": sex["sex"],
                "sex_evidence": sex["sex_evidence"],
                "family_status_norm": family_map[family_status],
                "religion": religion["religion"],
                "literacy": literacy["literacy"],
                "illness": illness,
                "illness_norm": illness_map[illness],
                "comments": religion["comments"],
                "notes_raw": notes["notes_raw"],
            }
        )
        output.append({field: row.get(field, "") for field in FIELDS})

    write_csv(COMBINED, output, FIELDS)
    district_rows = {district: [row for row in output if row["district"] == district] for district in OUTPUTS}
    for district, path in OUTPUTS.items():
        write_csv(path, district_rows[district], FIELDS)

    # Ordered concatenation check.
    concatenated = [row for district in OUTPUTS for row in district_rows[district]]
    ordered_concat = concatenated == output

    base_fields = list(base[0])
    diff_rows = []
    field_change_counts = Counter()
    for before, after in zip(base, output):
        changed = []
        for field in set(base_fields) | set(FIELDS):
            old = before.get(field, "")
            new = after.get(field, "")
            if old != new:
                changed.append(field)
                field_change_counts[field] += 1
        if changed:
            diff_rows.append(
                {
                    "person_id": before["person_id"],
                    "old_source_position_id": before["source_position_id"],
                    "new_source_position_id": after["source_position_id"],
                    "changed_fields": "; ".join(sorted(changed)),
                    "changed_field_count": str(len(changed)),
                }
            )
    write_csv(QA / "canonical_v3_record_diff_summary.csv", diff_rows, list(diff_rows[0]))
    write_csv(
        QA / "canonical_v3_field_change_summary.csv",
        [{"field": field, "changed_records": str(count)} for field, count in sorted(field_change_counts.items())],
        ["field", "changed_records"],
    )
    write_csv(
        QA / "canonical_v3_schema_diff.csv",
        [
            {"change": "removed", "field": field} for field in base_fields if field not in FIELDS
        ] + [
            {"change": "added", "field": field} for field in FIELDS if field not in base_fields
        ],
        ["change", "field"],
    )

    normalized_fields = ["legal_status_norm", "sex", "family_status_norm", "religion", "literacy", "illness_norm"]
    lowercase = [
        {"person_id": row["person_id"], "field": field, "value": part.strip()}
        for row in output
        for field in normalized_fields
        for part in row[field].split(";")
        if part.strip() and first_alpha_is_lower(part.strip())
    ]
    write_csv(QA / "canonical_v3_lowercase_category_exceptions.csv", lowercase, ["person_id", "field", "value"])

    gender_conflicts = []
    female_tokens = ("Женщина", "Жена", "Дочь", "Поселка", "Ссыльнокаторжная", "Крестьянка", "Солдатка")
    male_tokens = ("Сын", "Поселенец", "Ссыльнокаторжный", "Крестьянин", "Рядовой", "Офицер")
    for row in output:
        status = row["legal_status_norm"]
        implied = "Женский" if any(token.lower() in status.lower() for token in female_tokens) else "Мужской" if any(token.lower() in status.lower() for token in male_tokens) else ""
        if implied and implied != row["sex"]:
            gender_conflicts.append({"person_id": row["person_id"], "sex": row["sex"], "legal_status_norm": status, "family_status": row["family_status"]})
    write_csv(QA / "canonical_v3_gender_conflicts.csv", gender_conflicts, ["person_id", "sex", "legal_status_norm", "family_status"])

    expected_counts = {"Александровский": 2884, "Тымовский": 3242, "Корсаковский": 1320}
    actual_counts = Counter(row["district"] for row in output)
    checks = {
        "record_count_7446": len(output) == 7446,
        "field_count_31": len(FIELDS) == 31,
        "person_ids_unique": len(set(row["person_id"] for row in output)) == len(output),
        "person_id_order_unchanged": [row["person_id"] for row in output] == base_ids,
        "source_position_ids_nonblank": all(row["source_position_id"] for row in output),
        "source_position_ids_unique": len(set(row["source_position_id"] for row in output)) == len(output),
        "district_counts_match": dict(actual_counts) == expected_counts,
        "ordered_district_concatenation": ordered_concat,
        "written_district_slices_match": all(read_rows(OUTPUTS[district]) == district_rows[district] for district in OUTPUTS),
        "no_blank_sex": all(row["sex"] for row in output),
        "owner_verified_blank_household_type_count_24": sum(not row["household_type"] for row in output) == 24,
        "no_invalid_normalized_case": not lowercase,
        "no_gender_conflicts": not gender_conflicts,
        "combined_matches_written_file": read_rows(COMBINED) == output,
    }
    report = {
        "release": "v3_20260712",
        "base": str(BASE),
        "record_count": len(output),
        "field_count": len(FIELDS),
        "district_counts": dict(actual_counts),
        "changed_records_vs_v2": len(diff_rows),
        "field_change_counts": dict(sorted(field_change_counts.items())),
        "checks": checks,
    }
    QA.mkdir(parents=True, exist_ok=True)
    (QA / "canonical_v3_qa_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(
        QA / "canonical_v3_hashes.csv",
        [{"path": str(path).replace("\\", "/"), "sha256": sha256(path)} for path in [*OUTPUTS.values(), COMBINED]],
        ["path", "sha256"],
    )
    if not all(checks.values()):
        raise SystemExit(f"QA failed: {[name for name, passed in checks.items() if not passed]}")


if __name__ == "__main__":
    main()
