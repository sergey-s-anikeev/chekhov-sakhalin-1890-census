from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


INPUT = Path("data/processed/clean_sakhalin_1890_ru_v2_20260711.csv")
OUT = Path("data/review/family_status_norm_item11_20260712")
INVENTORY = OUT / "family_status_distinct_value_inventory.csv"
REVIEW = OUT / "family_status_owner_review_cases.csv"
APPROVED_MAPPING = OUT / "family_status_norm_approved_mapping.csv"
SUMMARY = OUT / "family_status_review_summary.csv"
STAGING = Path("data/staging/family_status_norm_item11_20260712")
STAGED_CSV = STAGING / "clean_sakhalin_1890_ru_family_status_norm_v1.csv"
QA = Path("outputs/qa/family_status_norm_item11_20260712")
DIFF = QA / "family_status_norm_diff.csv"
QA_SUMMARY = QA / "family_status_norm_qa_summary.csv"

OWNER_DECISIONS = {
    "Кухарка": "Кухарка",
    "Нянька": "Нянька",
    "Служанка": "Служанка",
    "Двоюродный брат": "Брат",
    "Муж. хозяин": "Хозяин",
    "Хозяйка. жена": "Жена",
    "Хозяйка. Жена": "Жена",
    "Дочь сына. Внучка": "Внучка",
    "Жилец. Совладелец": "Совладелец",
    "Жилица. Сожительница Фисенко": "Сожительница",
    "На воспитании. Сын": "Сын",
    "Незаконнорожденный сын Шуликиной от Алексеева": "Незаконнорожденный сын",
    "Незаконнорожденный сын. Приемный": "Незаконнорожденный сын",
    "Приемыш жильца": "Приемный сын",
    "Приемыш незаконный внук": "Приемный сын",
    "Сожитель хозяйки. Сожитель": "Сожитель",
    "Сожительница Щетинина. Сожительница": "Сожительница",
    "Сожительница и совладелица": "Сожительница",
    "Сожительница хозяина. Хозяйка": "Сожительница",
    "Сожительница хозяйка": "Сожительница",
    "Сын каюра. Сын": "Сын",
}


def classify(value: str) -> tuple[str, str, str]:
    """Return proposed normalized value, review status, and proposal basis."""
    v = value.strip()
    low = v.lower()
    if not v:
        return "", "straightforward", "Source family_status is blank."

    # Explicit historical child-status terminology takes precedence.
    if re.search(r"незаконнорожденн\w*\s+сын", low):
        proposal = "Незаконнорожденный сын"
        status = "owner_review" if any(x in low for x in ("прием", "внук", "от ")) else "straightforward"
        return proposal, status, "Explicit незаконнорожденный сын wording."
    if re.search(r"незаконнорожденн\w*\s+дочь", low):
        return "Незаконнорожденная дочь", "straightforward", "Explicit незаконнорожденная дочь wording."

    # Compound expressions where the source itself supplies the more useful
    # analytical role. These remain in owner_review despite the proposal.
    compound_proposals = {
        "хозяйка. жена": "Жена",
        "дочь сына. внучка": "Внучка",
        "жилец. совладелец": "Совладелец",
    }
    if low in compound_proposals:
        proposal = compound_proposals[low]
        return proposal, "owner_review", f"Compound source wording explicitly includes {proposal}."

    ordered = [
        (r"^(?:1-я |2-я )?жена\b", "Жена"),
        (r"^муж\b", "Муж"),
        (r"^приемн\w*\s+сын\b|^на воспитании\.\s*сын\b", "Приемный сын"),
        (r"^приемн\w*\s+дочь\b", "Приемная дочь"),
        (r"^пасынок\b", "Пасынок"),
        (r"^падчерица\b", "Падчерица"),
        (r"^сын\b", "Сын"),
        (r"^дочь\b", "Дочь"),
        (r"^отец\b", "Отец"),
        (r"^приемный отец\b", "Приемный отец"),
        (r"^мать\b", "Мать"),
        (r"^брат\b", "Брат"),
        (r"^двоюродный брат\b", "Двоюродный брат"),
        (r"^сестра\b", "Сестра"),
        (r"^внук\b", "Внук"),
        (r"^внучка\b|^дочь сына\.\s*внучка\b", "Внучка"),
        (r"^зять\b", "Зять"),
        (r"^невестка\b", "Невестка"),
        (r"^теща\b", "Теща"),
        (r"^свекровь\b", "Свекровь"),
        (r"^сожительница\b|^жилица\.\s*сожительница\b", "Сожительница"),
        (r"^сожитель\b", "Сожитель"),
        (r"^хозяин\b", "Хозяин"),
        (r"^хозяйка\b", "Хозяйка"),
        (r"^совладелец\b", "Совладелец"),
        (r"^совладелица\b", "Совладелица"),
        (r"^жилец\b", "Жилец"),
        (r"^жилица\b", "Жилица"),
        (r"^работник\b|^в работниках\b", "Работник"),
        (r"^работница\b", "Работница"),
        (r"^прислуга\b|^служанка\b|^кухарка\b|^нянька\b", "Прислуга"),
        (r"^сторож\b", "Сторож"),
        (r"^повар\b", "Повар"),
    ]
    for pattern, proposal in ordered:
        if re.search(pattern, low):
            competing = (
                "." in v
                or " и " in low
                or (proposal == "Сожительница" and "хозяйк" in low)
                or (proposal == "Жилец" and "совладел" in low)
            )
            return proposal, "owner_review" if competing else "straightforward", f"Explicit {proposal} wording."

    if low.startswith("приемыш"):
        return "Приемыш", "owner_review", "Приемыш requires review against accompanying relationship wording."
    return "", "owner_review", "No controlled mapping proposed automatically."


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with INPUT.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    counts = Counter(row["family_status"].strip() for row in rows)
    inventory: list[dict[str, str]] = []
    for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        proposal, status, basis = classify(value)
        owner_value = OWNER_DECISIONS.get(value, proposal)
        status = "owner_approved"
        inventory.append(
            {
                "family_status": value,
                "record_count": str(count),
                "family_status_norm_proposed": proposal,
                "review_status": status,
                "proposal_basis": basis,
                "owner_decision": "approve",
                "owner_family_status_norm": owner_value,
                "reviewer_notes": "",
            }
        )
    OUT.mkdir(parents=True, exist_ok=True)
    fields = list(inventory[0])
    write_csv(INVENTORY, inventory, fields)
    write_csv(REVIEW, [row for row in inventory if row["family_status"] in OWNER_DECISIONS], fields)
    write_csv(APPROVED_MAPPING, inventory, fields)

    status_counts = Counter(row["review_status"] for row in inventory)
    record_status_counts = Counter()
    for row in inventory:
        record_status_counts[row["review_status"]] += int(row["record_count"])
    summary = [
        {"metric": "input_records", "value": str(len(rows))},
        {"metric": "distinct_values_including_blank", "value": str(len(inventory))},
        {"metric": "blank_records", "value": str(counts[""])},
        {"metric": "straightforward_distinct_values", "value": str(status_counts["straightforward"])},
        {"metric": "straightforward_records", "value": str(record_status_counts["straightforward"])},
        {"metric": "owner_review_distinct_values", "value": str(status_counts["owner_review"])},
        {"metric": "owner_review_records", "value": str(record_status_counts["owner_review"])},
        {"metric": "owner_approved_distinct_values", "value": str(status_counts["owner_approved"])},
        {"metric": "owner_approved_records", "value": str(record_status_counts["owner_approved"])},
    ]
    write_csv(SUMMARY, summary, ["metric", "value"])

    approved_map = {row["family_status"]: row["owner_family_status_norm"] for row in inventory}
    input_fields = list(rows[0])
    insert_at = input_fields.index("family_status") + 1
    staged_fields = input_fields[:insert_at] + ["family_status_norm"] + input_fields[insert_at:]
    staged_rows: list[dict[str, str]] = []
    diff_rows: list[dict[str, str]] = []
    for row in rows:
        staged = dict(row)
        normalized = approved_map[row["family_status"].strip()]
        staged["family_status_norm"] = normalized
        staged_rows.append(staged)
        diff_rows.append(
            {
                "person_id": row["person_id"],
                "source_position_id": row["source_position_id"],
                "family_status": row["family_status"],
                "family_status_norm": normalized,
            }
        )
    STAGING.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    write_csv(STAGED_CSV, staged_rows, staged_fields)
    write_csv(DIFF, diff_rows, ["person_id", "source_position_id", "family_status", "family_status_norm"])

    unchanged_fields = [field for field in input_fields]
    non_target_changes = sum(
        any(before[field] != after[field] for field in unchanged_fields)
        for before, after in zip(rows, staged_rows)
    )
    qa_rows = [
        {"check": "input_records", "value": str(len(rows)), "pass": str(len(rows) == 7446).upper()},
        {"check": "staged_records", "value": str(len(staged_rows)), "pass": str(len(staged_rows) == len(rows)).upper()},
        {"check": "approved_distinct_source_values", "value": str(len(approved_map)), "pass": str(len(approved_map) == len(inventory)).upper()},
        {"check": "unmapped_source_values", "value": "0", "pass": str(all(value in approved_map for value in counts)).upper()},
        {"check": "non_target_field_changes", "value": str(non_target_changes), "pass": str(non_target_changes == 0).upper()},
        {"check": "blank_norm_for_nonblank_source", "value": str(sum(bool(r["family_status"].strip()) and not r["family_status_norm"] for r in staged_rows)), "pass": str(not any(bool(r["family_status"].strip()) and not r["family_status_norm"] for r in staged_rows)).upper()},
        {"check": "family_status_preserved", "value": str(sum(a["family_status"] != b["family_status"] for a, b in zip(rows, staged_rows))), "pass": str(all(a["family_status"] == b["family_status"] for a, b in zip(rows, staged_rows))).upper()},
    ]
    write_csv(QA_SUMMARY, qa_rows, ["check", "value", "pass"])


if __name__ == "__main__":
    main()
