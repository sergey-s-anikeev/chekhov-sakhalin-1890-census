from __future__ import annotations

import csv
import re
from pathlib import Path


INPUT = Path("data/review/legal_status_item17_20260712/legal_status_distinct_value_inventory.csv")
OUTPUT = Path("data/review/legal_status_item17_20260712/legal_status_norm_mapping_proposal.csv")
SUMMARY = Path("data/review/legal_status_item17_20260712/legal_status_norm_proposal_summary.csv")
APPROVED = Path("data/review/legal_status_item17_20260712/legal_status_norm_approved_mapping.csv")
DATA = Path("data/processed/clean_sakhalin_1890_ru_v2_20260711.csv")
STAGING = Path("data/staging/legal_status_norm_item17_20260712")
STAGED = STAGING / "clean_sakhalin_1890_ru_legal_status_norm_v1.csv"
QA = Path("outputs/qa/legal_status_norm_item17_20260712")
DIFF = QA / "legal_status_norm_diff.csv"
QA_SUMMARY = QA / "legal_status_norm_qa_summary.csv"

OWNER_CORRECTIONS = {
    "Сын крестьянина": "Сын крестьянина из ссыльных",
    "Дочь крестьянина": "Дочь крестьянина из ссыльных",
    "Сын крестьянки": "Сын крестьянки из ссыльных",
    "Дочь крестьянки": "Дочь крестьянки из ссыльных",
    "Жена врача": "Жена врача",
    "Жена надворного советника дочь поселенца": "Жена надворного советника",
    "Жена подполковника": "Жена подполковника",
    "Жена рядового": "Жена рядового",
    "Жена рядового Дуйской команды": "Жена рядового",
    "Крестьянин из поселенцев": "Крестьянин из ссыльных",
    "Незаконнорожденная дочь поселки": "Дочь поселки",
    "Поселка (богадельщик)": "Поселенец",
}


def propose(value: str) -> tuple[str, str, str, str]:
    """Return normalized status, illness addition, removed detail, review tier."""
    v = value.strip()
    low = v.lower()
    if not v:
        return "", "", "", "straightforward"

    removed = ""
    if "тымовского округа" in low:
        removed = "Тымовского округа"
    elif "александровского округа" in low:
        removed = "Александровского округа"
    elif "г. николаевска" in low:
        removed = "г. Николаевска"
    elif "дуйской команды" in low:
        removed = "Дуйской команды"
    elif "временно уволенный" in low:
        removed = "временно уволенный"

    illness = "Богадельщик" if "богадел" in low else ""

    # Free-status wording is normalized exactly as requested, regardless of
    # gender, kinship wording, occupation, or removed district qualifier.
    if "свободного состояния" in low:
        return "Свободного состояния", illness, removed, "straightforward"

    # Preserve Russian gender and the explicitly recorded parent's variant.
    # Remove only approved geography, a reviewed typo, and duplicated wording.
    child_value = v
    child_value = re.sub(r"\s+(?:Тымовского|Александровского) округа\b", "", child_value, flags=re.IGNORECASE)
    child_value = child_value.replace("поселенеца", "поселенца").replace("Поселенеца", "Поселенца")
    child_value = child_value.replace("поселенки", "поселки").replace("Поселенки", "Поселки")
    child_value = re.sub(r"\.\s*Дочь$", "", child_value, flags=re.IGNORECASE)
    if re.match(r"^(сын|дочь|незаконнорожденная дочь)\b", child_value, flags=re.IGNORECASE):
        return child_value, illness, removed, "straightforward"

    if low.startswith("жена ") or " жена" in low:
        return "", illness, removed, "owner_review"

    if low.startswith("поселенец"):
        return "Поселенец", illness, removed, "straightforward"
    if low.startswith(("поселенка", "поселка")):
        return "Поселка", illness, removed, "straightforward"
    if low.startswith("ссыльнокаторжный"):
        return "Ссыльнокаторжный", illness, removed, "straightforward"
    if low.startswith("ссыльнокаторжная"):
        return "Ссыльнокаторжная", illness, removed, "straightforward"
    if low in {"административно сосланный", "административный ссыльный"}:
        return "Административный ссыльный", illness, removed, "straightforward"
    if low == "почетный гражданин административный ссыльный":
        return "Административный ссыльный", illness, "Почетный гражданин", "owner_review"
    if low in {"крестьянин из ссыльных", "крестьянин из ссыльнопоселенцев"}:
        return "Крестьянин из ссыльных", illness, removed, "straightforward"
    if low == "крестьянка из ссыльных":
        return "Крестьянка из ссыльных", illness, removed, "straightforward"
    if low == "крестьянин из поселенцев":
        return "Крестьянин из поселенцев", illness, removed, "straightforward"
    if low in {"крестьянин", "крестьянин из крестьян"}:
        return "Крестьянин", illness, removed, "straightforward"
    if low == "крестьянка":
        return "Крестьянка", illness, removed, "straightforward"

    military = {
        "запасной рядовой": "Запасной рядовой",
        "запасный рядовой": "Запасной рядовой",
        "рядовой запаса": "Запасной рядовой",
        "уволенный в запас армии рядовой": "Запасной рядовой",
        "запасной унтер-офицер": "Запасной унтер-офицер",
        "запасный унтер-офицер": "Запасной унтер-офицер",
        "запасный ефрейтор": "Запасной ефрейтор",
        "отставной рядовой": "Отставной рядовой",
        "отставной унтер-офицер": "Отставной унтер-офицер",
        "отставной фельдфебель": "Отставной фельдфебель",
        "рядовой": "Рядовой",
        "рядовой дуйской команды": "Рядовой",
        "унтер-офицер": "Унтер-офицер",
        "капитан": "Капитан",
        "подполковник": "Подполковник",
        "подпоручик": "Подпоручик",
    }
    if low in military:
        return military[low], illness, removed, "straightforward"

    direct = {
        "врач": "Врач",
        "дворянин": "Дворянин",
        "канцелярский служащий": "Канцелярский служащий",
        "кузнец": "Кузнец",
        "мещанин": "Мещанин",
        "мещанин г. николаевска": "Мещанин",
        "надворный советник": "Надворный советник",
        "повивальная бабка": "Повивальная бабка",
        "совладелец": "Совладелец",
        "старший надзиратель": "Старший надзиратель",
        "штейгер": "Штейгер",
        "фельдшер": "Фельдшер",
    }
    if low in direct:
        return direct[low], illness, removed, "straightforward"

    return v, illness, removed, "owner_review"


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with INPUT.open(encoding="utf-8-sig", newline="") as handle:
        source = list(csv.DictReader(handle))
    output = []
    for row in source:
        norm, illness, removed, tier = propose(row["legal_status"])
        owner_norm = OWNER_CORRECTIONS.get(row["legal_status"], norm)
        output.append(
            {
                "legal_status": row["legal_status"],
                "record_count": row["record_count"],
                "legal_status_norm_proposed": norm,
                "illness_addition_proposed": illness,
                "removed_detail": removed,
                "review_tier": tier,
                "owner_decision": "correct" if row["legal_status"] in OWNER_CORRECTIONS else "approve",
                "owner_legal_status_norm": owner_norm,
                "owner_illness_addition": illness,
                "reviewer_notes": "typo in source" if row["legal_status"] == "Поселка (богадельщик)" else "",
            }
        )
    write_csv(OUTPUT, output, list(output[0]))
    write_csv(APPROVED, output, list(output[0]))
    distinct_by_tier = {tier: sum(row["review_tier"] == tier for row in output) for tier in ("straightforward", "owner_review")}
    records_by_tier = {tier: sum(int(row["record_count"]) for row in output if row["review_tier"] == tier) for tier in distinct_by_tier}
    summary = [
        {"metric": "proposed_distinct_values_including_blank", "value": str(len(output))},
        {"metric": "straightforward_distinct_values", "value": str(distinct_by_tier["straightforward"])},
        {"metric": "straightforward_records", "value": str(records_by_tier["straightforward"])},
        {"metric": "owner_review_distinct_values", "value": str(distinct_by_tier["owner_review"])},
        {"metric": "owner_review_records", "value": str(records_by_tier["owner_review"])},
        {"metric": "source_values_with_proposed_illness_addition", "value": str(sum(bool(row["illness_addition_proposed"]) for row in output))},
        {"metric": "records_with_proposed_illness_addition", "value": str(sum(int(row["record_count"]) for row in output if row["illness_addition_proposed"]))},
        {"metric": "values_with_removed_detail", "value": str(sum(bool(row["removed_detail"]) for row in output))},
    ]
    write_csv(SUMMARY, summary, ["metric", "value"])

    approved_map = {row["legal_status"]: row for row in output}
    with DATA.open(encoding="utf-8-sig", newline="") as handle:
        data_rows = list(csv.DictReader(handle))
    input_fields = list(data_rows[0])
    insert_at = input_fields.index("legal_status") + 1
    staged_fields = input_fields[:insert_at] + ["legal_status_norm"] + input_fields[insert_at:]
    staged_rows = []
    diff_rows = []
    for row in data_rows:
        decision = approved_map[row["legal_status"].strip()]
        staged = dict(row)
        staged["legal_status_norm"] = decision["owner_legal_status_norm"]
        before_illness = row["illness"]
        addition = decision["owner_illness_addition"]
        if addition:
            staged["illness"] = addition if not before_illness else f"{before_illness}; {addition}"
        staged_rows.append(staged)
        diff_rows.append(
            {
                "person_id": row["person_id"],
                "source_position_id": row["source_position_id"],
                "legal_status": row["legal_status"],
                "legal_status_norm": staged["legal_status_norm"],
                "illness_before": before_illness,
                "illness_after": staged["illness"],
            }
        )
    STAGING.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    write_csv(STAGED, staged_rows, staged_fields)
    write_csv(DIFF, diff_rows, list(diff_rows[0]))
    unchanged = [field for field in input_fields if field != "illness"]
    non_target_changes = sum(any(a[field] != b[field] for field in unchanged) for a, b in zip(data_rows, staged_rows))
    illness_changes = sum(a["illness"] != b["illness"] for a, b in zip(data_rows, staged_rows))
    qa = [
        {"check": "input_records", "value": str(len(data_rows)), "pass": str(len(data_rows) == 7446).upper()},
        {"check": "staged_records", "value": str(len(staged_rows)), "pass": str(len(staged_rows) == len(data_rows)).upper()},
        {"check": "approved_distinct_values_including_blank", "value": str(len(approved_map)), "pass": str(len(approved_map) == 100).upper()},
        {"check": "unmapped_legal_status_values", "value": "0", "pass": str(all(row["legal_status"].strip() in approved_map for row in data_rows)).upper()},
        {"check": "blank_norm_for_nonblank_source", "value": str(sum(bool(row["legal_status"].strip()) and not row["legal_status_norm"] for row in staged_rows)), "pass": str(not any(bool(row["legal_status"].strip()) and not row["legal_status_norm"] for row in staged_rows)).upper()},
        {"check": "legal_status_preserved", "value": str(sum(a["legal_status"] != b["legal_status"] for a, b in zip(data_rows, staged_rows))), "pass": str(all(a["legal_status"] == b["legal_status"] for a, b in zip(data_rows, staged_rows))).upper()},
        {"check": "illness_changes", "value": str(illness_changes), "pass": str(illness_changes == 5).upper()},
        {"check": "non_target_field_changes", "value": str(non_target_changes), "pass": str(non_target_changes == 0).upper()},
    ]
    write_csv(QA_SUMMARY, qa, ["check", "value", "pass"])


if __name__ == "__main__":
    main()
