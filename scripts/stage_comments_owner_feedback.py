from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/staging/comments_numeric_cleanup_20260717/clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_item18_comments_staged.csv"
REVIEW_VALUES = ROOT / "data/review/comments_numeric_cleanup_20260717/owner_review_comments_values.json"
ADDRESS_APPROVED = ROOT / "outputs/qa/comments_owner_feedback_20260717/address_normalization_diff.csv"
STAGING_DIR = ROOT / "data/staging/comments_owner_feedback_20260717"
QA_DIR = ROOT / "outputs/qa/comments_owner_feedback_20260717"
OUTPUT = STAGING_DIR / "clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_item18_comments_reviewed_staged.csv"

ADDRESS_START = re.compile(
    r"^(\d+)\s+(?=(?:Кирпичн|Касьянов|Касьян|Сизов|Мало-Российск|Набережн))",
    re.IGNORECASE,
)
ADDRESS_ORDINAL = re.compile(
    r"^(\d+)\s*(?:-|‑)?\s*я\s+(?=(?:Кирпичн|Касьянов|Касьян|Сизов|Мало-Российск|Набережн))",
    re.IGNORECASE,
)


def normalize_address(value: str) -> str:
    normalized = ADDRESS_ORDINAL.sub(r"\1-я ", value)
    normalized = ADDRESS_START.sub(r"\1-я ", normalized)
    normalized = re.sub(r"\.\s+Начало\b", " начало", normalized)
    return normalized


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    review_matrix = json.loads(REVIEW_VALUES.read_text(encoding="utf-8"))
    review_headers = review_matrix[0]
    expected_headers = ["person_id", "source_position_id", "page_number", "comments", "comments_norm", "name_alias"]
    if review_headers != expected_headers:
        raise ValueError(f"Unexpected review headers: {review_headers}")
    review_rows = [dict(zip(review_headers, row, strict=True)) for row in review_matrix[1:]]
    if len(review_rows) != 389:
        raise ValueError(f"Expected 389 reviewed rows, found {len(review_rows)}")
    review_by_id = {row["person_id"]: row for row in review_rows}
    if len(review_by_id) != len(review_rows):
        raise ValueError("Duplicate person_id values in owner review")

    approved_addresses: dict[str, dict[str, str]] = {}
    if ADDRESS_APPROVED.exists():
        with ADDRESS_APPROVED.open("r", encoding="utf-8-sig", newline="") as handle:
            approved_rows = list(csv.DictReader(handle))
        expected_address_headers = {"person_id", "comments_reviewed", "comments_address_normalized"}
        if set(approved_rows[0]) != expected_address_headers if approved_rows else False:
            raise ValueError("Unexpected approved address mapping headers")
        approved_addresses = {row["person_id"]: row for row in approved_rows}
        if len(approved_addresses) != len(approved_rows):
            raise ValueError("Duplicate person_id values in approved address mappings")

    with BASE.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        if not fieldnames or "comments" not in fieldnames or "name_alias" not in fieldnames:
            raise ValueError("Base file is missing comments or name_alias")
        source_rows = list(reader)

    source_by_id = {row["person_id"]: row for row in source_rows}
    missing_ids = sorted(set(review_by_id) - set(source_by_id))
    if missing_ids:
        raise ValueError(f"Reviewed person_id values missing from base: {missing_ids}")

    staged_rows: list[dict[str, str]] = []
    diff_rows: list[dict[str, str]] = []
    address_rows: list[dict[str, str]] = []
    source_match_exceptions: list[dict[str, str]] = []

    for source in source_rows:
        staged = source.copy()
        review = review_by_id.get(source["person_id"])
        if review is not None:
            if review["source_position_id"] != source["source_position_id"] or review["comments"] != source["comments"]:
                source_match_exceptions.append(
                    {
                        "person_id": source["person_id"],
                        "base_source_position_id": source["source_position_id"],
                        "review_source_position_id": str(review["source_position_id"] or ""),
                        "base_comments": source["comments"],
                        "review_comments": str(review["comments"] or ""),
                    }
                )
            reviewed_comment = str(review["comments_norm"] or "").strip()
            normalized_comment = normalize_address(reviewed_comment)
            approved_address = approved_addresses.get(source["person_id"])
            if approved_address is not None:
                if approved_address["comments_reviewed"] != reviewed_comment:
                    raise ValueError(f"Approved address source mismatch for {source['person_id']}")
                normalized_comment = approved_address["comments_address_normalized"].strip()
            if reviewed_comment != normalized_comment:
                address_rows.append(
                    {
                        "person_id": source["person_id"],
                        "comments_reviewed": reviewed_comment,
                        "comments_address_normalized": normalized_comment,
                    }
                )
            staged["comments"] = normalized_comment
            if review["name_alias"] is not None and str(review["name_alias"]).strip():
                staged["name_alias"] = str(review["name_alias"]).strip()

        changed_fields = [field for field in fieldnames if source[field] != staged[field]]
        if changed_fields:
            diff_rows.append(
                {
                    "person_id": source["person_id"],
                    "source_position_id": source["source_position_id"],
                    "page_number": source["page_number"],
                    "comments_before": source["comments"],
                    "comments_after": staged["comments"],
                    "name_alias_before": source["name_alias"],
                    "name_alias_after": staged["name_alias"],
                    "changed_fields": ";".join(changed_fields),
                }
            )
        staged_rows.append(staged)

    if source_match_exceptions:
        raise ValueError(f"Owner review does not match the staged base for {len(source_match_exceptions)} rows")

    write_csv(OUTPUT, fieldnames, staged_rows)
    diff_fields = [
        "person_id", "source_position_id", "page_number", "comments_before", "comments_after",
        "name_alias_before", "name_alias_after", "changed_fields",
    ]
    write_csv(QA_DIR / "comments_owner_feedback_diff.csv", diff_fields, diff_rows)
    write_csv(
        QA_DIR / "address_normalization_diff.csv",
        ["person_id", "comments_reviewed", "comments_address_normalized"],
        address_rows,
    )

    changed_fields = sorted(
        {
            field
            for before, after in zip(source_rows, staged_rows, strict=True)
            for field in fieldnames
            if before[field] != after[field]
        }
    )
    comments_changed = sum(before["comments"] != after["comments"] for before, after in zip(source_rows, staged_rows, strict=True))
    aliases_changed = sum(before["name_alias"] != after["name_alias"] for before, after in zip(source_rows, staged_rows, strict=True))
    qa = {
        "base_file": str(BASE.relative_to(ROOT)).replace("\\", "/"),
        "owner_feedback_file": "data/review/comments_numeric_cleanup_20260717/owner_review_comments.xlsx",
        "output_file": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"),
        "review_rows": len(review_rows),
        "reviewed_comments_nonblank": sum(bool(str(row["comments_norm"] or "").strip()) for row in review_rows),
        "reviewed_comments_blank": sum(not bool(str(row["comments_norm"] or "").strip()) for row in review_rows),
        "reviewed_name_alias_nonblank": sum(bool(str(row["name_alias"] or "").strip()) for row in review_rows),
        "rows_before": len(source_rows),
        "rows_after": len(staged_rows),
        "columns_before": len(fieldnames),
        "columns_after": len(fieldnames),
        "comments_changed": comments_changed,
        "name_alias_changed": aliases_changed,
        "address_values_normalized": len(address_rows),
        "approved_address_mappings_applied": len(approved_addresses),
        "changed_fields": changed_fields,
        "person_id_order_preserved": [row["person_id"] for row in source_rows] == [row["person_id"] for row in staged_rows],
        "source_position_id_order_preserved": [row["source_position_id"] for row in source_rows] == [row["source_position_id"] for row in staged_rows],
        "owner_source_matches": len(source_match_exceptions) == 0,
        "remaining_reviewed_digit_only_comments": sum(
            bool(re.fullmatch(r"\d+", row["comments"].strip()))
            for row in staged_rows
            if row["person_id"] in review_by_id and row["comments"].strip()
        ),
        "base_sha256": sha256(BASE),
        "output_sha256": sha256(OUTPUT),
        "owner_feedback_sha256": sha256(ROOT / "data/review/comments_numeric_cleanup_20260717/owner_review_comments.xlsx"),
    }
    QA_DIR.mkdir(parents=True, exist_ok=True)
    (QA_DIR / "comments_owner_feedback_qa.json").write_text(
        json.dumps(qa, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(qa, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
