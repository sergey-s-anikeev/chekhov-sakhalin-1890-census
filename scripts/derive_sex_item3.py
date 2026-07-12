from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


INPUT = Path("data/processed/clean_sakhalin_1890_ru_v2_20260711.csv")
LEGAL_MAPPING = Path("data/review/legal_status_item17_20260712/legal_status_norm_approved_mapping.csv")
REVIEW = Path("data/review/sex_item3_20260712")
STAGING = Path("data/staging/sex_item3_20260712")
QA = Path("outputs/qa/sex_item3_20260712")

OWNER_SEX = {
    "P000520": "Женский", "P000894": "Женский", "P000955": "Женский",
    "P001405": "Женский", "P002762": "Мужской", "P003653": "Женский",
    "P004323": "Женский", "P005266": "Женский", "P006213": "Мужской",
    "P006639": "Женский", "P006746": "Женский", "P007406": "Женский",
}

LEGAL_STATUS_CORRECTIONS = {
    "P000520": "Ссыльнокаторжная",
    "P000894": "Ссыльнокаторжная",
    "P000955": "Дочь поселенца",
    "P001405": "Крестьянка из ссыльных",
    "P003653": "Дочь ссыльнокаторжного",
    "P005266": "Дочь ссыльнокаторжного",
    "P006213": "Сын поселенца",
    "P006639": "Поселка",
    "P006746": "Крестьянка из ссыльных",
    "P007406": "Ссыльнокаторжная",
}

FEMALE_LEGAL = re.compile(r"\b(женщина|жена|дочь|поселка|поселенка|ссыльнокаторжная|крестьянка|солдатка|бабка)\b", re.I)
MALE_LEGAL = re.compile(r"\b(сын|поселенец|ссыльнокаторжный|крестьянин|рядовой|офицер|ефрейтор|фельдфебель|капитан|подполковник|подпоручик|мещанин|дворянин|врач|фельдшер|штейгер|надзиратель|советник|кузнец)\b", re.I)
FEMALE_FAMILY = re.compile(r"\b(жена|дочь|хозяйка|сожительница|совладелица|жилица|внучка|мать|сестра|невестка|падчерица|свекровь|теща|кухарка|нянька|служанка|работница)\b", re.I)
MALE_FAMILY = re.compile(r"\b(муж|сын|хозяин|сожитель|совладелец|жилец|внук|отец|брат|зять|пасынок|работник|сторож|повар)\b", re.I)
FEMALE_PATRONYMIC = re.compile(r"(?:овна|евна|ична|инична)$", re.I)
MALE_PATRONYMIC = re.compile(r"(?:ович|евич|ич)$", re.I)


def explicit_signal(value: str, female: re.Pattern[str], male: re.Pattern[str]) -> str:
    has_female = bool(female.search(value))
    has_male = bool(male.search(value))
    if has_female and not has_male:
        return "Женский"
    if has_male and not has_female:
        return "Мужской"
    return ""


def patronymic_signal(name: str) -> str:
    tokens = re.findall(r"[А-ЯЁа-яё-]+", name)
    female = any(FEMALE_PATRONYMIC.search(token) for token in tokens)
    male = any(MALE_PATRONYMIC.search(token) for token in tokens)
    if female and not male:
        return "Женский"
    if male and not female:
        return "Мужской"
    return ""


def derive(row: dict[str, str], legal_status_norm: str) -> tuple[str, str, str]:
    legal_source = explicit_signal(row["legal_status"], FEMALE_LEGAL, MALE_LEGAL)
    legal_norm = explicit_signal(legal_status_norm, FEMALE_LEGAL, MALE_LEGAL)
    legal = legal_norm if legal_norm and legal_source and legal_norm != legal_source else (legal_source or legal_norm)
    legal_evidence = "approved legal_status_norm" if legal_norm and legal_norm != legal_source else "legal_status"
    family = explicit_signal(row["family_status"], FEMALE_FAMILY, MALE_FAMILY)
    if legal and family and legal != family:
        return "", "Conflict: legal_status vs family_status", "owner_review"
    if legal and family:
        return legal, f"{legal_evidence} + family_status", "proposed"
    if legal:
        return legal, legal_evidence, "proposed"
    if family:
        return family, "family_status", "proposed"
    patronymic = patronymic_signal(row["name_raw"])
    if patronymic:
        return patronymic, "name_raw patronymic morphology", "proposed_name_rule"
    return "", "Insufficient explicit evidence", "owner_review"


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with INPUT.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    with LEGAL_MAPPING.open(encoding="utf-8-sig", newline="") as handle:
        legal_map = {row["legal_status"]: row["owner_legal_status_norm"] for row in csv.DictReader(handle)}
    input_fields = list(rows[0])
    insert_at = input_fields.index("name_alias") + 1
    staged_fields = input_fields[:insert_at] + ["sex", "sex_evidence"] + input_fields[insert_at:]

    staged_rows = []
    review_rows = []
    for row in rows:
        sex, evidence, status = derive(row, legal_map[row["legal_status"].strip()])
        owner_sex = OWNER_SEX.get(row["person_id"], "")
        if owner_sex:
            sex = owner_sex
            evidence = "Owner-approved name and grammatical evidence"
            status = "owner_approved"
        legal_status_proposed = LEGAL_STATUS_CORRECTIONS.get(row["person_id"], row["legal_status"])
        staged = dict(row)
        staged["legal_status"] = legal_status_proposed
        staged["sex"] = sex
        staged["sex_evidence"] = evidence
        staged_rows.append(staged)
        review_rows.append(
            {
                "person_id": row["person_id"],
                "source_position_id": row["source_position_id"],
                "name_raw": row["name_raw"],
                "legal_status": row["legal_status"],
                "family_status": row["family_status"],
                "sex_proposed": sex,
                "sex_evidence": evidence,
                "review_status": status,
                "legal_status_proposed": legal_status_proposed,
                "family_status_proposed": row["family_status"],
                "owner_decision": "approve" if owner_sex else "",
                "owner_sex": owner_sex,
                "reviewer_notes": "",
            }
        )

    review_fields = list(review_rows[0])
    write_csv(REVIEW / "sex_complete_proposal.csv", review_rows, review_fields)
    write_csv(REVIEW / "sex_owner_review_cases.csv", [row for row in review_rows if row["person_id"] in OWNER_SEX], review_fields)
    evidence_summary = Counter((row["sex_proposed"], row["sex_evidence"], row["review_status"]) for row in review_rows)
    summary_rows = [
        {"sex_proposed": key[0], "sex_evidence": key[1], "review_status": key[2], "record_count": str(count)}
        for key, count in sorted(evidence_summary.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_csv(REVIEW / "sex_proposal_summary.csv", summary_rows, list(summary_rows[0]))
    write_csv(STAGING / "clean_sakhalin_1890_ru_sex_item3_v1.csv", staged_rows, staged_fields)
    diff_rows = [
        {
            "person_id": before["person_id"],
            "source_position_id": before["source_position_id"],
            "name_raw": before["name_raw"],
            "legal_status_before": before["legal_status"],
            "legal_status_after": after["legal_status"],
            "family_status_before": before["family_status"],
            "family_status_after": after["family_status"],
            "sex": after["sex"],
            "sex_evidence": after["sex_evidence"],
        }
        for before, after in zip(rows, staged_rows)
        if before["person_id"] in OWNER_SEX
    ]
    write_csv(QA / "sex_item3_owner_decision_diff.csv", diff_rows, list(diff_rows[0]))

    non_target_changes = sum(
        any(before[field] != after[field] for field in input_fields if field not in {"legal_status", "family_status"})
        for before, after in zip(rows, staged_rows)
    )
    legal_status_changes = sum(before["legal_status"] != after["legal_status"] for before, after in zip(rows, staged_rows))
    family_status_changes = sum(before["family_status"] != after["family_status"] for before, after in zip(rows, staged_rows))
    counts = Counter(row["sex"] for row in staged_rows)
    review_count = sum(row["review_status"] == "owner_review" for row in review_rows)
    qa = [
        {"check": "input_records", "value": str(len(rows)), "pass": str(len(rows) == 7446).upper()},
        {"check": "staged_records", "value": str(len(staged_rows)), "pass": str(len(staged_rows) == len(rows)).upper()},
        {"check": "male_proposed", "value": str(counts["Мужской"]), "pass": "TRUE"},
        {"check": "female_proposed", "value": str(counts["Женский"]), "pass": "TRUE"},
        {"check": "blank_sex_values", "value": str(counts[""]), "pass": str(counts[""] == 0).upper()},
        {"check": "owner_approved_records", "value": str(len(OWNER_SEX)), "pass": str(len(OWNER_SEX) == 12).upper()},
        {"check": "legal_status_changes", "value": str(legal_status_changes), "pass": str(legal_status_changes == 10).upper()},
        {"check": "family_status_changes", "value": str(family_status_changes), "pass": str(family_status_changes == 0).upper()},
        {"check": "invalid_sex_values", "value": str(len(set(counts) - {"", "Мужской", "Женский"})), "pass": str(not (set(counts) - {"", "Мужской", "Женский"})).upper()},
        {"check": "non_target_field_changes", "value": str(non_target_changes), "pass": str(non_target_changes == 0).upper()},
    ]
    write_csv(QA / "sex_item3_qa_summary.csv", qa, ["check", "value", "pass"])


if __name__ == "__main__":
    main()
