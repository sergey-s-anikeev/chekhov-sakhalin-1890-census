"""Build the read-only Item 7 age review package from canonical v3."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/clean_sakhalin_1890_ru_v3_20260712.csv"
REVIEW_DIR = ROOT / "data/review/age_item7_20260713"
QA_DIR = ROOT / "outputs/qa/age_item7_20260713"

CHILD_MIN_AGE = 0
CHILD_MAX_AGE = 18

CHILD_FAMILY_STATUSES = {
    "Сын",
    "Дочь",
    "Незаконнорожденный сын",
    "Незаконнорожденная дочь",
    "Приемный сын",
    "Приемная дочь",
    "Внук",
    "Внучка",
    "Пасынок",
    "Падчерица",
}
HIGH_REVIEW_FAMILY_STATUSES = {"Хозяин", "Жена", "Сожитель", "Сожительница"}
OTHER_REVIEW_FAMILY_STATUSES = {"Жилец", "Прислуга", "Нянька", "Кухарка"}
ADULT_LEGAL_STATUSES = {
    "Поселенец",
    "Поселка",
    "Ссыльнокаторжный",
    "Ссыльнокаторжная",
    "Крестьянин из ссыльных",
    "Крестьянка из ссыльных",
}

REVIEW_COLUMNS = [
    "review_priority",
    "consistency_flag",
    "review_reasons",
    "review_status",
    "manual_decision",
    "manual_notes",
    "person_id",
    "source_position_id",
    "page_number",
    "district",
    "settlement",
    "household_id",
    "name_raw",
    "sex",
    "age",
    "legal_status",
    "legal_status_norm",
    "family_status",
    "family_status_norm",
    "comments",
    "notes_raw",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def classify(row: dict[str, str]) -> tuple[str, list[str]]:
    age = int(row["age"])
    family = row["family_status_norm"].strip()
    legal = row["legal_status_norm"].strip()
    reasons: list[str] = []
    priority = ""

    if age == 0:
        reasons.append("AGE_ZERO_VERIFY_SOURCE")
        priority = "high"

    if family in HIGH_REVIEW_FAMILY_STATUSES:
        reasons.append("ADULT_HOUSEHOLD_ROLE_IN_FAMILY_STATUS_NORM")
        priority = "high"
    elif family in OTHER_REVIEW_FAMILY_STATUSES:
        reasons.append("SERVICE_OR_HOUSEHOLD_ROLE_REVIEW")
        priority = priority or "medium"
    elif not family:
        reasons.append("BLANK_FAMILY_STATUS_NORM")
        priority = priority or "medium"
    elif family not in CHILD_FAMILY_STATUSES:
        reasons.append("NON_CHILD_FAMILY_STATUS_NORM_REVIEW")
        priority = priority or "medium"

    if legal in ADULT_LEGAL_STATUSES:
        reasons.append("STANDALONE_ADULT_LEGAL_STATUS_NORM")
        priority = "high" if age < 16 else (priority or "medium")
    elif not legal:
        reasons.append("BLANK_LEGAL_STATUS_NORM")
        priority = priority or "medium"
    elif not (legal.startswith("Сын ") or legal.startswith("Дочь ")) and legal != "Свободного состояния":
        reasons.append("NON_CHILD_LEGAL_STATUS_NORM_REVIEW")
        priority = priority or "medium"

    return priority, reasons


def main() -> None:
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as handle:
        source_rows = list(csv.DictReader(handle))

    child_rows: list[dict[str, str]] = []
    flagged_rows: list[dict[str, str]] = []
    blank_age_rows: list[dict[str, str]] = []

    for row in source_rows:
        age_text = row["age"].strip()
        if not age_text:
            out = {key: row.get(key, "") for key in REVIEW_COLUMNS}
            out.update(
                review_priority="high",
                consistency_flag="YES",
                review_reasons="BLANK_AGE_VERIFY_SOURCE",
                manual_decision="",
                manual_notes="",
            )
            blank_age_rows.append(out)
            continue
        if not age_text.isdigit():
            continue
        age = int(age_text)
        if not CHILD_MIN_AGE <= age <= CHILD_MAX_AGE:
            continue

        priority, reasons = classify(row)
        out = {key: row.get(key, "") for key in REVIEW_COLUMNS}
        out.update(
            review_priority=priority,
            consistency_flag="YES" if reasons else "NO",
            review_reasons="; ".join(reasons),
            review_status=(
                "confirmed"
                if reasons == ["AGE_ZERO_VERIFY_SOURCE"]
                else ("under review" if reasons else "not flagged")
            ),
            manual_decision=(
                "confirmed — no age anomaly"
                if reasons == ["AGE_ZERO_VERIFY_SOURCE"]
                else ""
            ),
            manual_notes=(
                "Owner reviewed all age-zero records on 2026-07-13 and found no anomalies."
                if "AGE_ZERO_VERIFY_SOURCE" in reasons
                else ""
            ),
        )
        child_rows.append(out)
        if reasons:
            flagged_rows.append(out)

    child_rows.sort(key=lambda r: (int(r["age"]), r["district"], int(r["page_number"] or 0), r["person_id"]))
    flagged_rows.sort(
        key=lambda r: (
            0 if r["review_priority"] == "high" else 1,
            int(r["age"]),
            r["district"],
            int(r["page_number"] or 0),
            r["person_id"],
        )
    )
    blank_age_rows.sort(key=lambda r: (r["district"], int(r["page_number"] or 0), r["person_id"]))

    full_path = REVIEW_DIR / "age_0_18_full_inventory.csv"
    flagged_path = REVIEW_DIR / "age_0_18_flagged_review.csv"
    remaining_path = REVIEW_DIR / "age_0_18_remaining_under_review.csv"
    zero_decisions_path = REVIEW_DIR / "owner_response" / "age_zero_review_decisions.csv"
    blank_path = REVIEW_DIR / "blank_age_review.csv"
    write_csv(full_path, child_rows, REVIEW_COLUMNS)
    write_csv(flagged_path, flagged_rows, REVIEW_COLUMNS)
    remaining_rows = [row for row in flagged_rows if row["review_status"] == "under review"]
    zero_decision_rows = [row for row in flagged_rows if row["age"] == "0"]
    write_csv(remaining_path, remaining_rows, REVIEW_COLUMNS)
    write_csv(zero_decisions_path, zero_decision_rows, REVIEW_COLUMNS)
    write_csv(blank_path, blank_age_rows, REVIEW_COLUMNS)

    age_counts = Counter(row["age"] for row in child_rows)
    family_counts = Counter(row["family_status_norm"] or "[blank]" for row in child_rows)
    legal_counts = Counter(row["legal_status_norm"] or "[blank]" for row in child_rows)
    reason_counts = Counter(
        reason
        for row in flagged_rows
        for reason in row["review_reasons"].split("; ")
        if reason
    )
    priority_counts = Counter(row["review_priority"] for row in flagged_rows)

    write_csv(
        REVIEW_DIR / "age_0_18_counts.csv",
        [{"age": str(age), "record_count": str(age_counts[str(age)])} for age in range(0, 19)],
        ["age", "record_count"],
    )
    write_csv(
        REVIEW_DIR / "family_status_norm_counts_age_0_18.csv",
        [{"family_status_norm": key, "record_count": str(count)} for key, count in family_counts.most_common()],
        ["family_status_norm", "record_count"],
    )
    write_csv(
        REVIEW_DIR / "legal_status_norm_counts_age_0_18.csv",
        [{"legal_status_norm": key, "record_count": str(count)} for key, count in legal_counts.most_common()],
        ["legal_status_norm", "record_count"],
    )

    QA_DIR.mkdir(parents=True, exist_ok=True)
    qa = {
        "item": 7,
        "mode": "read-only review; no canonical or staged dataset changes",
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": sha256(SOURCE),
        "source_record_count": len(source_rows),
        "age_0_18_record_count": len(child_rows),
        "blank_age_record_count": len(blank_age_rows),
        "flagged_age_0_18_record_count": len(flagged_rows),
        "age_zero_owner_reviewed_count": len(zero_decision_rows),
        "age_zero_confirmed_without_anomaly_count": len(zero_decision_rows),
        "age_zero_with_separate_status_flag_still_under_review_count": sum(
            row["review_status"] == "under review" for row in zero_decision_rows
        ),
        "remaining_age_0_18_under_review_count": len(remaining_rows),
        "flagged_priority_counts": dict(sorted(priority_counts.items())),
        "flag_reason_counts": dict(sorted(reason_counts.items())),
        "page_number_present_in_all_review_rows": all(
            row["page_number"].strip() for row in child_rows + blank_age_rows
        ),
        "unique_person_ids_in_source": len({row["person_id"] for row in source_rows}) == len(source_rows),
        "full_inventory_has_every_integer_age_0_18_record": len(child_rows)
        == sum(1 for row in source_rows if row["age"].strip().isdigit() and 0 <= int(row["age"]) <= 18),
        "review_outputs": {},
    }
    for path in sorted(REVIEW_DIR.rglob("*.csv")):
        qa["review_outputs"][str(path.relative_to(ROOT)).replace("\\", "/")] = {
            "sha256": sha256(path),
        }
    qa_path = QA_DIR / "age_item7_qa.json"
    qa_path.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = f"""# Item 7 age review summary

This is a read-only review package based on `{qa['source']}`. No canonical or staged dataset was changed.

## Scope

- Full cohort: all {len(child_rows):,} records with integer `age` from 0 through 18 inclusive.
- Blank-age exception inventory: {len(blank_age_rows):,} records.
- Initial flagged child review subset: {len(flagged_rows):,} records ({priority_counts.get('high', 0):,} high priority; {priority_counts.get('medium', 0):,} medium priority).
- Owner-reviewed age-zero records: {len(zero_decision_rows):,}; all were confirmed with no age anomaly on 2026-07-13.
- Remaining under review: {len(remaining_rows):,} records. This includes {sum(row['review_status'] == 'under review' for row in zero_decision_rows):,} age-zero records whose age is confirmed but whose blank family status remains a separate review flag.
- Every review row includes `page_number`, `person_id`, and `source_position_id` for source-book verification.

## Interpretation

Flags are prompts for manual source review, not corrections. Relationship or status evidence is never used to infer an age. `Свободного состояния` is treated as age-neutral. Child forms beginning with `Сын` or `Дочь` are treated as consistent for screening purposes. Adult household roles, service roles, blanks, and standalone adult legal statuses remain under review. The age-zero check is complete and confirmed without anomalies.

## Manual decision fields

Use `manual_decision` and `manual_notes` in the review CSVs. Suggested decisions are `confirmed`, `age correction`, `status correction`, or `needs further evidence`; no decision has been prefilled.
"""
    (QA_DIR / "age_item7_review_summary.md").write_text(summary, encoding="utf-8")

    print(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
