#!/usr/bin/env python3
"""Generate the Item 1 name_raw review package without editing canonical data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


CANONICAL_COLUMNS = [
    "person_id",
    "source_position_id",
    "district_code",
    "district",
    "settlement_order",
    "settlement",
    "person_order_in_settlement",
    "page_number",
    "household_number",
    "legal_status",
    "name_raw",
    "family_status",
    "age",
    "religion",
    "origin_place",
    "arrival_year",
    "occupation",
    "literacy",
    "marriage_status",
    "allowance_status",
    "illness",
    "comments",
    "notes_raw",
]

INVENTORY_COLUMNS = [
    "person_id",
    "source_position_id",
    "district",
    "settlement",
    "page_number",
    "name_raw",
    "family_status",
    "legal_status",
    "age",
    "occupation",
    "comments",
    "notes_raw",
    "exception_types",
    "reason",
    "review_priority",
    "recommended_action",
]

CORRECTION_COLUMNS = [
    "person_id",
    "source_position_id",
    "current_name_raw",
    "proposed_name_raw",
    "proposed_name_alias",
    "proposed_name_note",
    "current_family_status",
    "proposed_family_status",
    "proposed_destination_field",
    "proposed_destination_value",
    "proposal_basis",
    "proposal_confidence",
    "owner_decision",
    "reviewer_notes",
]

DIFF_COLUMNS = [
    "person_id",
    "source_position_id",
    "field",
    "canonical_value",
    "proposed_value",
    "proposal_confidence",
    "owner_decision",
]

ROLE_OR_DESCRIPTION_PATTERN = re.compile(
    r"\b(?:жена|сын|дочь|хозяин|хозяйка|жилец|жилица|сожитель|"
    r"сожительница|совладелец|совладелица|работник|работница|"
    r"прислуга|внук|внучка|мать|отец|брат|сестра|пасынок|"
    r"падчерица|близнец|сменщик|незаконнорожденн(?:ый|ая))\b",
    re.IGNORECASE,
)
ALIAS_OR_NOTE_PATTERN = re.compile(
    r"\b(?:он\s+же|она\s+же|по\s+святому\s+крещению|"
    r"от\s+[А-ЯЁ][А-Яа-яЁё-]*)",
    re.IGNORECASE,
)
AGE_PHRASE_PATTERN = re.compile(r"\b\d{1,3}\s+лет\b", re.IGNORECASE)
ANONYMOUS_PATTERN = re.compile(
    r"^(?:Некрещеная|Человек\s+неизвестного\s+звания)$", re.IGNORECASE
)
ALLOWED_LOWERCASE_NAME_TOKENS = {"оглы", "кызы", "фон", "ван", "де", "дер"}


def proposal(
    name: str,
    *,
    alias: str = "",
    note: str = "",
    family_status: str | None = None,
    destination_field: str = "",
    destination_value: str = "",
    basis: str,
    confidence: str,
) -> dict[str, str | None]:
    return {
        "proposed_name_raw": name,
        "proposed_name_alias": alias,
        "proposed_name_note": note,
        "proposed_family_status": family_status,
        "proposed_destination_field": destination_field,
        "proposed_destination_value": destination_value,
        "proposal_basis": basis,
        "proposal_confidence": confidence,
    }


# These are proposals only. They are never applied to a canonical file by this script.
PROPOSALS: dict[str, dict[str, str | None]] = {
    "P000166": proposal(
        "Оглы Мула Шах Мамет Гаджи Зюльгуфар",
        basis="Long non-Russian multiword name; retain unchanged unless source evidence shows a parsing error.",
        confidence="medium",
    ),
    "P000512": proposal(
        "Карл Лангер",
        note="сменщик",
        destination_field="occupation",
        destination_value="Сменщик",
        basis="Trailing occupation-like description is not part of the personal name.",
        confidence="medium",
    ),
    "P000797": proposal(
        "Станислав Шмаус",
        note="близнец",
        destination_field="comments",
        destination_value="Близнец",
        basis="Trailing descriptive word is not part of the personal name.",
        confidence="high",
    ),
    "P001367": proposal(
        "Оглы Мамет Рагим Абдурахман Мешади Абдул Оглы",
        basis="Long non-Russian multiword name; retain unchanged unless source evidence shows a parsing error.",
        confidence="medium",
    ),
    "P002157": proposal(
        "Анна Шумилова",
        family_status="Жена",
        basis="Trailing role duplicates the populated family_status.",
        confidence="high",
    ),
    "P002567": proposal(
        "Анна",
        note="от Надежденко",
        basis="Parentage phrase should be retained separately from the personal name.",
        confidence="medium",
    ),
    "P002568": proposal(
        "Михаил",
        note="от Надежденко",
        basis="Parentage phrase should be retained separately from the personal name.",
        confidence="medium",
    ),
    "P002569": proposal(
        "Андрей",
        note="от Надежденко",
        basis="Parentage phrase should be retained separately from the personal name.",
        confidence="medium",
    ),
    "P002629": proposal(
        "Розалия Беренис",
        basis="Mechanical repair of a word split inside the surname; source verification required.",
        confidence="medium",
    ),
    "P002631": proposal(
        "Анисим Аникин",
        basis="Mechanical repair of a word split inside the surname; source verification required.",
        confidence="medium",
    ),
    "P003322": proposal(
        "Дарья Михайлова Печенкина - Познякова",
        basis="Double-surname form is preserved and deferred to Item 2.",
        confidence="low",
    ),
    "P003347": proposal(
        "Яков Игнатьев Наконечный",
        alias="Фурман",
        basis="Parenthetical surname is separated for Item 2 classification.",
        confidence="medium",
    ),
    "P003372": proposal(
        "Марфа Тарачова",
        alias="Киреева",
        basis="Parenthetical surname is separated for Item 2 classification.",
        confidence="medium",
    ),
    "P003375": proposal(
        "Ирина Попкова - Клюева",
        basis="Double-surname form is preserved and deferred to Item 2.",
        confidence="low",
    ),
    "P003380": proposal(
        "Некрещеная",
        note="Имя не указано",
        basis="The field contains a description rather than a recoverable personal name; preserve pending source review.",
        confidence="low",
    ),
    "P003396": proposal(
        "Марья Матвеева Зайцева - Аманова",
        basis="Double-surname form is preserved and deferred to Item 2.",
        confidence="low",
    ),
    "P003415": proposal(
        "Иван",
        note="Бродяга; в поле имени указано 35 лет",
        basis="Status and age text are not part of the personal name; age conflicts with age=48 and requires source review.",
        confidence="low",
    ),
    "P003556": proposal(
        "Иван Кандудин",
        alias="Дудаков",
        basis="Parenthetical surname is separated for Item 2 classification.",
        confidence="medium",
    ),
    "P003991": proposal(
        "Андрей Непомнящий - Заруба",
        basis="Double-surname form is preserved and deferred to Item 2.",
        confidence="low",
    ),
    "P004044": proposal(
        "Анна Павлова Биспаева",
        alias="Павлова",
        basis="Parenthetical surname is separated for Item 2 classification.",
        confidence="medium",
    ),
    "P004064": proposal(
        "Иван Филиппов Кулешов",
        note="некрещеный",
        basis="Parenthetical religious description is not part of the personal name.",
        confidence="high",
    ),
    "P004096": proposal(
        "Прасковья",
        alias="Марья",
        basis="The phrase 'она же' explicitly introduces an alternative given name.",
        confidence="high",
    ),
    "P004099": proposal(
        "Некрещеная",
        note="Имя не указано",
        basis="The field contains a description rather than a recoverable personal name; preserve pending source review.",
        confidence="low",
    ),
    "P004234": proposal(
        "Марья Александрова Филиппова",
        basis="Mechanical repair of a word split inside the given name; source verification required.",
        confidence="medium",
    ),
    "P004448": proposal(
        "Консультана Копкиева",
        alias="Пелагея; Васильева",
        note="Два значения в скобках требуют классификации в Item 2",
        basis="Parenthetical given name and surname require separate Item 2 classification.",
        confidence="low",
    ),
    "P004522": proposal(
        "Арсентий Иванов Бетлинский",
        basis="Mechanical repair of a word split inside the surname; source verification required.",
        confidence="medium",
    ),
    "P004657": proposal(
        "Иван Непомнящий",
        note="В поле имени указано 20 лет",
        basis="Age text is not part of the personal name; it conflicts with age=50 and requires source review.",
        confidence="low",
    ),
    "P004705": proposal(
        "Ульяна Лаврентьева Сулина",
        alias="Молодилова",
        basis="Parenthetical surname is separated for Item 2 classification.",
        confidence="medium",
    ),
    "P004791": proposal(
        "Надежда Прохорова Михеева",
        note="Прежняя фамилия обозначена, но не указана",
        basis="Empty parentheses are not part of the personal name; the existing comment preserves their meaning.",
        confidence="high",
    ),
    "P004898": proposal(
        "Варвара Харитонова Любомудрова",
        family_status="Жена",
        basis="Trailing role belongs in the currently blank family_status.",
        confidence="high",
    ),
    "P004979": proposal(
        "Волько Вилингер",
        alias="Дмитрий Иванов Иванов",
        note="по святому крещению",
        basis="The parenthetical phrase explicitly gives a baptismal name.",
        confidence="high",
    ),
    "P005023": proposal(
        "Аграфена Карпова Данилина",
        basis="Mechanical repair of a word split inside the given name; source verification required.",
        confidence="medium",
    ),
    "P005396": proposal(
        "Человек неизвестного звания",
        note="Имя не указано",
        basis="The field contains an anonymous description and no recoverable personal name; preserve pending source review.",
        confidence="low",
    ),
    "P005528": proposal(
        "Евгений Петров Крыцуль",
        basis="Mechanical repair of word splits in the given name and surname; source verification required.",
        confidence="medium",
    ),
    "P005638": proposal(
        "Михаил Федотов Лищенко",
        basis="Mechanical repair of a word split inside the surname; source verification required.",
        confidence="medium",
    ),
    "P005758": proposal(
        "Егор Махнев",
        alias="Красильников",
        basis="The phrase 'он же' explicitly introduces an alternative surname.",
        confidence="high",
    ),
    "P006007": proposal(
        "Индер - Хон",
        basis="Hyphen-separated name form is preserved and deferred to Item 2.",
        confidence="low",
    ),
    "P006021": proposal(
        "Павел Аргипопуло",
        basis="Mechanical repair of a probable word split inside the surname; source verification required.",
        confidence="low",
    ),
    "P006795": proposal(
        "Трофим Мосин",
        basis="Mechanical repair of a word split inside the surname; source verification required.",
        confidence="medium",
    ),
    "P006846": proposal(
        "Иван Наркизов",
        alias="Чубай",
        basis="Parenthetical surname is separated for Item 2 classification.",
        confidence="medium",
    ),
    "P006888": proposal(
        "Филипп Максимов Кривич",
        basis="Mechanical repair of a word split inside the given name; source verification required.",
        confidence="medium",
    ),
    "P007204": proposal(
        "Некрещеная",
        note="Имя не указано",
        basis="The field contains a description rather than a recoverable personal name; preserve pending source review.",
        confidence="low",
    ),
    "P007374": proposal(
        "Алексей Гаврилов",
        family_status="Незаконнорожденный сын",
        basis="Trailing role belongs in the currently blank family_status.",
        confidence="high",
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default="data/processed/clean_sakhalin_1890_ru.csv",
        help="Canonical combined CSV to inspect read-only.",
    )
    parser.add_argument(
        "--review-dir",
        default="data/review/name_raw_item1_20260710",
        help="Directory for reviewable CSV artifacts.",
    )
    parser.add_argument(
        "--qa-dir",
        default="outputs/qa/name_raw_item1_20260710",
        help="Directory for Item 1 QA artifacts.",
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return list(reader.fieldnames or []), rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def lowercase_tokens(name: str) -> list[str]:
    result: list[str] = []
    for raw_token in name.split():
        visible_token = raw_token.strip(".,;:()[]")
        token = visible_token.casefold()
        if (
            visible_token
            and visible_token[0].islower()
            and token not in ALLOWED_LOWERCASE_NAME_TOKENS
        ):
            result.append(token)
    return result


def classify_name(name: str) -> list[str]:
    flags: list[str] = []
    if ROLE_OR_DESCRIPTION_PATTERN.search(name):
        flags.append("role_or_description_text")
    if ALIAS_OR_NOTE_PATTERN.search(name):
        flags.append("alias_or_parentage_phrase")
    if AGE_PHRASE_PATTERN.search(name):
        flags.append("age_text")
    if ANONYMOUS_PATTERN.fullmatch(name.strip()):
        flags.append("no_explicit_personal_name")
    if "(" in name or ")" in name:
        flags.append("parenthetical_text_item2")
    if re.search(r"\s-\s", name):
        flags.append("double_surname_item2")
    if lowercase_tokens(name):
        flags.append("unexpected_lowercase_or_word_split")
    if len(name.split()) >= 6:
        flags.append("long_multiword_name")
    return flags


def exception_reason(flags: list[str], name: str) -> str:
    reasons: list[str] = []
    mapping = {
        "role_or_description_text": "Contains a household role or descriptive word.",
        "alias_or_parentage_phrase": "Contains an alias, baptismal-name, or parentage phrase.",
        "age_text": "Contains age text that does not belong in a personal name.",
        "no_explicit_personal_name": "Contains a description but no explicit personal name.",
        "parenthetical_text_item2": "Contains parenthetical text requiring Item 2 classification.",
        "double_surname_item2": "Contains a double-surname separator requiring Item 2 review.",
        "unexpected_lowercase_or_word_split": (
            "Contains unexpected lowercase tokens or probable PDF word splitting: "
            + ", ".join(lowercase_tokens(name))
            + "."
        ),
        "long_multiword_name": "Contains six or more tokens; review without assuming an error.",
    }
    for flag in flags:
        if flag in mapping:
            reasons.append(mapping[flag])
    return " ".join(reasons)


def priority(flags: list[str], proposal_data: dict[str, str | None] | None) -> str:
    if "no_explicit_personal_name" in flags or "age_text" in flags:
        return "high"
    if proposal_data and proposal_data.get("proposal_confidence") == "low":
        return "high"
    if "role_or_description_text" in flags or "unexpected_lowercase_or_word_split" in flags:
        return "medium"
    return "low"


def recommended_action(flags: list[str], person_id: str) -> str:
    if person_id in PROPOSALS:
        confidence = PROPOSALS[person_id]["proposal_confidence"]
        return f"Review the proposed separation/correction; confidence={confidence}."
    if "long_multiword_name" in flags:
        return "Verify against source; retain unchanged unless contrary evidence is found."
    if "double_surname_item2" in flags or "parenthetical_text_item2" in flags:
        return "Preserve name_raw and complete classification under Item 2."
    return "Manual source review required; no automatic correction proposed."


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    review_dir = Path(args.review_dir)
    qa_dir = Path(args.qa_dir)
    review_dir.mkdir(parents=True, exist_ok=True)
    qa_dir.mkdir(parents=True, exist_ok=True)

    canonical_hash_before = sha256(input_path)
    headers, rows = read_csv(input_path)
    if headers != CANONICAL_COLUMNS:
        raise SystemExit(f"Unexpected canonical schema: {headers}")

    row_by_id = {row["person_id"]: row for row in rows}
    missing_proposal_ids = sorted(set(PROPOSALS) - set(row_by_id))
    if missing_proposal_ids:
        raise SystemExit(f"Proposal IDs not found: {missing_proposal_ids}")

    inventory: list[dict[str, Any]] = []
    corrections: list[dict[str, Any]] = []
    preview_rows: list[dict[str, Any]] = []
    diff_rows: list[dict[str, Any]] = []
    exception_counts: Counter[str] = Counter()

    for row in rows:
        flags = classify_name(row["name_raw"])
        proposal_data = PROPOSALS.get(row["person_id"])

        # Explicit proposals are included even if their anomaly is not fully
        # represented by a generic heuristic.
        if proposal_data and not flags:
            flags = ["manually_identified_name_issue"]

        for flag in flags:
            exception_counts[flag] += 1

        if flags:
            inventory.append(
                {
                    **{column: row[column] for column in INVENTORY_COLUMNS if column in row},
                    "exception_types": "|".join(flags),
                    "reason": exception_reason(flags, row["name_raw"])
                    or "Manually identified during complete name review.",
                    "review_priority": priority(flags, proposal_data),
                    "recommended_action": recommended_action(flags, row["person_id"]),
                }
            )

        proposed_name = row["name_raw"]
        proposed_alias = ""
        proposed_note = ""
        proposed_family = row["family_status"]
        review_status = "not_flagged"
        if flags:
            review_status = "pending_owner_review"
        if proposal_data:
            proposed_name = str(proposal_data["proposed_name_raw"] or row["name_raw"])
            proposed_alias = str(proposal_data["proposed_name_alias"] or "")
            proposed_note = str(proposal_data["proposed_name_note"] or "")
            proposed_family_value = proposal_data["proposed_family_status"]
            if proposed_family_value is not None:
                proposed_family = str(proposed_family_value)
            corrections.append(
                {
                    "person_id": row["person_id"],
                    "source_position_id": row["source_position_id"],
                    "current_name_raw": row["name_raw"],
                    "proposed_name_raw": proposed_name,
                    "proposed_name_alias": proposed_alias,
                    "proposed_name_note": proposed_note,
                    "current_family_status": row["family_status"],
                    "proposed_family_status": proposed_family,
                    "proposed_destination_field": proposal_data["proposed_destination_field"],
                    "proposed_destination_value": proposal_data["proposed_destination_value"],
                    "proposal_basis": proposal_data["proposal_basis"],
                    "proposal_confidence": proposal_data["proposal_confidence"],
                    "owner_decision": "pending",
                    "reviewer_notes": "",
                }
            )

            proposed_fields = {
                "name_raw": proposed_name,
                "family_status": proposed_family,
                "name_alias": proposed_alias,
                "name_note": proposed_note,
            }
            canonical_fields = {
                "name_raw": row["name_raw"],
                "family_status": row["family_status"],
                "name_alias": "",
                "name_note": "",
            }
            for field, proposed_value in proposed_fields.items():
                if proposed_value != canonical_fields[field]:
                    diff_rows.append(
                        {
                            "person_id": row["person_id"],
                            "source_position_id": row["source_position_id"],
                            "field": field,
                            "canonical_value": canonical_fields[field],
                            "proposed_value": proposed_value,
                            "proposal_confidence": proposal_data["proposal_confidence"],
                            "owner_decision": "pending",
                        }
                    )

        preview_rows.append(
            {
                **row,
                "name_raw_item1_proposed": proposed_name,
                "name_alias_item1_proposed": proposed_alias,
                "name_note_item1_proposed": proposed_note,
                "family_status_item1_proposed": proposed_family,
                "name_item1_review_status": review_status,
                "name_item1_exception_types": "|".join(flags),
            }
        )

    inventory_path = review_dir / "name_raw_exception_inventory.csv"
    correction_path = review_dir / "name_raw_proposed_corrections.csv"
    preview_path = review_dir / "clean_sakhalin_1890_ru_name_item1_review_preview.csv"
    diff_path = qa_dir / "name_raw_item1_proposed_diff.csv"
    qa_json_path = qa_dir / "qa_name_raw_item1_report.json"
    qa_md_path = qa_dir / "qa_name_raw_item1_report.md"

    write_csv(inventory_path, INVENTORY_COLUMNS, inventory)
    write_csv(correction_path, CORRECTION_COLUMNS, corrections)
    preview_columns = CANONICAL_COLUMNS + [
        "name_raw_item1_proposed",
        "name_alias_item1_proposed",
        "name_note_item1_proposed",
        "family_status_item1_proposed",
        "name_item1_review_status",
        "name_item1_exception_types",
    ]
    write_csv(preview_path, preview_columns, preview_rows)
    write_csv(diff_path, DIFF_COLUMNS, diff_rows)

    canonical_hash_after = sha256(input_path)
    preview_original_columns_unchanged = all(
        all(source[column] == preview[column] for column in CANONICAL_COLUMNS)
        for source, preview in zip(rows, preview_rows, strict=True)
    )
    qa = {
        "item": "1. Verify name_raw",
        "status": "ready_for_owner_review",
        "canonical_input": str(input_path).replace("\\", "/"),
        "canonical_sha256_before": canonical_hash_before,
        "canonical_sha256_after": canonical_hash_after,
        "canonical_unchanged": canonical_hash_before == canonical_hash_after,
        "canonical_schema_matches": headers == CANONICAL_COLUMNS,
        "canonical_record_count": len(rows),
        "canonical_person_id_unique": len({row["person_id"] for row in rows}) == len(rows),
        "canonical_source_position_id_unique": len({row["source_position_id"] for row in rows}) == len(rows),
        "canonical_blank_name_raw": sum(not row["name_raw"].strip() for row in rows),
        "exception_record_count": len(inventory),
        "exception_counts": dict(sorted(exception_counts.items())),
        "proposed_correction_record_count": len(corrections),
        "proposed_field_diff_count": len(diff_rows),
        "pending_owner_decision_count": sum(
            correction["owner_decision"] == "pending" for correction in corrections
        ),
        "high_confidence_proposals": sum(
            correction["proposal_confidence"] == "high" for correction in corrections
        ),
        "medium_confidence_proposals": sum(
            correction["proposal_confidence"] == "medium" for correction in corrections
        ),
        "low_confidence_proposals": sum(
            correction["proposal_confidence"] == "low" for correction in corrections
        ),
        "preview_record_count": len(preview_rows),
        "preview_original_columns_unchanged": preview_original_columns_unchanged,
        "preview_person_id_order_unchanged": [row["person_id"] for row in rows]
        == [row["person_id"] for row in preview_rows],
        "preview_blank_proposed_name_count": sum(
            not row["name_raw_item1_proposed"].strip() for row in preview_rows
        ),
        "outputs": {},
        "limitations": [
            "The source PDFs are not present in the clean repository, so medium- and low-confidence proposals require source verification.",
            "Parenthetical and double-surname classifications remain provisional until Item 2.",
            "The exception inventory is exhaustive for the documented Item 1 heuristics, not a claim that every historical name can be linguistically validated without source review.",
        ],
    }
    for output_path in [inventory_path, correction_path, preview_path, diff_path]:
        qa["outputs"][str(output_path).replace("\\", "/")] = {
            "sha256": sha256(output_path),
            "bytes": output_path.stat().st_size,
        }

    qa_json_path.write_text(
        json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    qa["outputs"][str(qa_json_path).replace("\\", "/")] = {
        "sha256": sha256(qa_json_path),
        "bytes": qa_json_path.stat().st_size,
    }

    lines = [
        "# Item 1 QA Report: `name_raw` Verification",
        "",
        "## Status",
        "",
        "Ready for project-owner review. No canonical dataset was modified.",
        "",
        "## Input Integrity",
        "",
        f"- Canonical records: **{qa['canonical_record_count']:,}**",
        f"- Canonical SHA-256 unchanged: **{qa['canonical_unchanged']}**",
        f"- Canonical schema matches the approved 23 columns: **{qa['canonical_schema_matches']}**",
        f"- Unique `person_id`: **{qa['canonical_person_id_unique']}**",
        f"- Unique `source_position_id`: **{qa['canonical_source_position_id_unique']}**",
        f"- Blank canonical `name_raw`: **{qa['canonical_blank_name_raw']}**",
        "",
        "## Review Results",
        "",
        f"- Exception records: **{qa['exception_record_count']}**",
        f"- Records with proposed actions: **{qa['proposed_correction_record_count']}**",
        f"- Proposed field-level differences: **{qa['proposed_field_diff_count']}**",
        f"- Pending owner decisions: **{qa['pending_owner_decision_count']}**",
        f"- High-confidence proposals: **{qa['high_confidence_proposals']}**",
        f"- Medium-confidence proposals: **{qa['medium_confidence_proposals']}**",
        f"- Low-confidence proposals: **{qa['low_confidence_proposals']}**",
        "",
        "### Exception counts",
        "",
    ]
    for key, value in qa["exception_counts"].items():
        lines.append(f"- `{key}`: **{value}**")
    lines.extend(
        [
            "",
            "## Preview Validation",
            "",
            f"- Preview records: **{qa['preview_record_count']:,}**",
            f"- Original canonical columns unchanged in preview: **{qa['preview_original_columns_unchanged']}**",
            f"- `person_id` order unchanged: **{qa['preview_person_id_order_unchanged']}**",
            f"- Blank proposed names: **{qa['preview_blank_proposed_name_count']}**",
            "",
            "The preview contains proposal columns only. It is not a canonical replacement and none of its proposed values are approved yet.",
            "",
            "## Required Owner Decision",
            "",
            "Complete `owner_decision` in `name_raw_proposed_corrections.csv` with an approved decision for each row. Medium- and low-confidence proposals should be checked against source evidence before approval.",
            "",
            "Allowed decision values are `approve`, `reject`, `modify`, and `defer`. Add the replacement instruction to `reviewer_notes` for `modify`, and explain `reject` decisions where useful.",
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in qa["limitations"])
    qa_md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    manifest_path = qa_dir / "name_raw_item1_artifact_manifest.csv"
    manifest_rows = []
    manifest_inputs = [
        (input_path, "canonical_input"),
        (Path(__file__), "reproducible_review_script"),
        (inventory_path, "exception_inventory"),
        (correction_path, "proposed_correction_table"),
        (preview_path, "staged_review_preview"),
        (diff_path, "proposed_record_level_diff"),
        (qa_json_path, "machine_readable_qa_report"),
        (qa_md_path, "human_readable_qa_report"),
    ]
    for artifact_path, role in manifest_inputs:
        try:
            display_path = artifact_path.resolve().relative_to(Path.cwd().resolve())
        except ValueError:
            display_path = artifact_path
        manifest_rows.append(
            {
                "path": str(display_path).replace("\\", "/"),
                "role": role,
                "sha256": sha256(artifact_path),
                "bytes": artifact_path.stat().st_size,
            }
        )
    write_csv(manifest_path, ["path", "role", "sha256", "bytes"], manifest_rows)

    print(json.dumps(qa, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
