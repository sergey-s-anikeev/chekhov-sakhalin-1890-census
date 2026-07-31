#!/usr/bin/env python3
"""Extract the book surname index and compare it with the staged dataset."""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

import pdfplumber

ORDER_RE = re.compile(r"^\((\d+)\)$")
INITIALS_RE = re.compile(r"(?:^|\s)((?:[А-ЯЁ]\.){1,5})$")

SETTLEMENT_ALIASES = {
    "александровский пост": "Пост Александровский",
    "корсаковский пост": "Пост Корсаковский",
    "дуэ": "Пост Дуэ",
    "армудан верхний": "Верхний Армудан",
    "армудан нижний": "Нижний Армудан",
    "березняки": "Березники",
    "первое арково": "Арково I",
    "второе арково": "Арково II",
    "третье арково": "Арково III",
}


def text_norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").casefold().replace("ё", "е")
    value = value.replace("–", "-").replace("—", "-")
    value = re.sub(r"[^\w-]+", " ", value, flags=re.UNICODE)
    return re.sub(r"\s+", " ", value).strip()


def name_norm(value: str) -> str:
    return text_norm(value).replace("-", " ")


def group_lines(words):
    lines = []
    for word in sorted(words, key=lambda item: (item["top"], item["x0"])):
        if not lines or abs(lines[-1][0] - word["top"]) > 1.0:
            lines.append([word["top"], [word]])
        else:
            lines[-1][1].append(word)
    return [(top, sorted(items, key=lambda item: item["x0"])) for top, items in lines]


def extract_reference_entries(pdf_path: Path):
    entries = []
    with pdfplumber.open(pdf_path) as pdf:
        for pdf_page, page in enumerate(pdf.pages, start=1):
            words = page.extract_words()
            page_number_candidates = [
                word["text"] for word in words
                if word["text"].isdigit() and word["top"] > page.height - 60
            ]
            source_page = page_number_candidates[-1] if page_number_candidates else ""
            lines = group_lines(words)
            for side, start, boundary, end, name_anchor in (
                ("left", 40, 160, 291, 51.0),
                ("right", 291, 412, page.width - 35, 302.4),
            ):
                buffer = []
                buffer_top = None
                for top, line_words in lines:
                    side_words = [
                        word for word in line_words
                        if start <= word["x0"] < end and word["height"] < 12
                    ]
                    if not side_words:
                        continue
                    name_words = [word["text"] for word in side_words if word["x0"] < boundary]
                    location_words = [word["text"] for word in side_words if word["x0"] >= boundary]
                    if not name_words and not location_words:
                        continue
                    order_match = ORDER_RE.match(location_words[-1]) if location_words else None
                    if order_match:
                        book_name = " ".join(buffer + name_words).strip()
                        settlement = " ".join(location_words[:-1]).strip()
                        if book_name and settlement:
                            entries.append({
                                "pdf_page": pdf_page,
                                "source_page": source_page,
                                "column": side,
                                "book_name_field": book_name,
                                "book_settlement": settlement,
                                "person_order_in_settlement": order_match.group(1),
                                "book_line_top": round(buffer_top if buffer_top is not None else top, 1),
                            })
                        buffer = []
                        buffer_top = None
                    elif (
                        name_words
                        and abs(min(word["x0"] for word in side_words) - name_anchor) <= 4
                    ):
                        if buffer_top is None:
                            buffer_top = top
                        buffer.extend(name_words)
    return entries


def map_settlement(book_value, staged_settlements):
    key = text_norm(book_value)
    if key in SETTLEMENT_ALIASES:
        return SETTLEMENT_ALIASES[key], "alias"
    exact = {text_norm(value): value for value in staged_settlements}
    if key in exact:
        return exact[key], "exact"
    ranked = sorted(
        (
            SequenceMatcher(None, key, text_norm(value)).ratio(),
            value,
        )
        for value in staged_settlements
    )
    score, value = ranked[-1]
    return (value, f"fuzzy:{score:.3f}") if score >= 0.72 else ("", f"unmapped:{score:.3f}")


def book_last_name(book_name, staged_first, staged_last):
    initials = INITIALS_RE.search(book_name)
    if initials:
        return book_name[:initials.start()].strip(), "initials_removed"
    if not staged_first and " " in staged_last:
        return book_name.strip(), "complete_name_field"
    last_tokens = staged_last.split()
    if staged_first and name_norm(book_name).endswith(name_norm(staged_first)):
        # Prefer the displayed prefix so spelling differences remain visible.
        prefix_tokens = book_name.split()[:-len(staged_first.split())]
        if prefix_tokens:
            return " ".join(prefix_tokens), "full_given_removed"
    if last_tokens:
        return " ".join(book_name.split()[:len(last_tokens)]), "leading_token_count"
    return book_name.strip(), "unparsed"


def review_category(book_last, staged_last, discrepancy_type):
    book_key = name_norm(book_last)
    staged_key = name_norm(staged_last)
    if discrepancy_type == "exact":
        return "exact", "none"
    if discrepancy_type == "normalized_variant":
        return "formatting_or_normalization_only", "low"
    if not staged_key and book_key:
        return "missing_staged_last_name", "high"
    if sorted(book_key.split()) == sorted(staged_key.split()) and book_key != staged_key:
        return "same_name_tokens_different_order", "medium"
    if staged_key and (
        book_last.startswith(f"{staged_last} (")
        or book_last.startswith(f"{staged_last}-")
    ):
        return "book_alias_or_compound_surname", "medium"
    if re.search(r"[\[\]?]|\b\d+\b|\bлет\b", book_last, flags=re.IGNORECASE):
        return "book_annotation_or_descriptor", "medium"
    if discrepancy_type == "probable_spelling_difference":
        return "probable_spelling_difference", "high"
    return "structural_or_major_difference", "high"


def write_csv(path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("staged", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    with args.staged.open(encoding="utf-8-sig", newline="") as handle:
        staged_rows = list(csv.DictReader(handle))
    staged_settlements = sorted({row["settlement"] for row in staged_rows})
    staged_by_key = {
        (row["settlement"], row["person_order_in_settlement"]): row
        for row in staged_rows
    }

    entries = extract_reference_entries(args.pdf)
    discrepancies = []
    all_comparisons = []
    matched_ids = set()
    unmatched_reference = []
    match_types = Counter()
    discrepancy_types = Counter()
    review_categories = Counter()
    settlement_methods = Counter()

    for entry in entries:
        mapped_settlement, settlement_method = map_settlement(
            entry["book_settlement"], staged_settlements
        )
        settlement_methods[settlement_method.split(":")[0]] += 1
        row = staged_by_key.get((mapped_settlement, entry["person_order_in_settlement"]))
        if not row:
            unmatched_reference.append({
                "review_decision": "",
                "review_notes": "",
                **entry,
                "mapped_settlement": mapped_settlement,
                "settlement_mapping": settlement_method,
                "issue": "book entry did not match settlement + person order",
            })
            continue

        matched_ids.add(row["person_id"])
        book_last, parsing_method = book_last_name(
            entry["book_name_field"], row["first_name"], row["last_name"]
        )
        staged_last = row["last_name"]
        if book_last == staged_last:
            discrepancy_type = "exact"
        elif name_norm(book_last) == name_norm(staged_last):
            discrepancy_type = "normalized_variant"
        else:
            similarity = SequenceMatcher(
                None, name_norm(book_last), name_norm(staged_last)
            ).ratio()
            discrepancy_type = (
                "probable_spelling_difference" if similarity >= 0.68
                else "structural_or_major_difference"
            )
        similarity = SequenceMatcher(
            None, name_norm(book_last), name_norm(staged_last)
        ).ratio()
        category, review_priority = review_category(
            book_last, staged_last, discrepancy_type
        )
        discrepancy_types[discrepancy_type] += 1
        review_categories[category] += 1
        match_types[parsing_method] += 1
        comparison = {
            "review_decision": "",
            "corrected_last_name": "",
            "review_notes": "",
            "person_id": row["person_id"],
            "name_raw": row["name_raw"],
            "staged_first_name": row["first_name"],
            "staged_patronymic_name": row["patronymic_name"],
            "staged_last_name": staged_last,
            "book_last_name": book_last,
            "book_name_field": entry["book_name_field"],
            "discrepancy_type": discrepancy_type,
            "review_category": category,
            "review_priority": review_priority,
            "similarity": round(similarity, 3),
            "book_name_parsing": parsing_method,
            "settlement": row["settlement"],
            "book_settlement": entry["book_settlement"],
            "settlement_mapping": settlement_method,
            "person_order_in_settlement": row["person_order_in_settlement"],
            "source_position_id": row["source_position_id"],
            "pdf_page": entry["pdf_page"],
            "source_page": entry["source_page"],
            "pdf_column": entry["column"],
            "sex": row["sex"],
            "religion": row["religion"],
            "family_status": row["family_status"],
            "parse_rule": row["parse_rule"],
        }
        all_comparisons.append(comparison)
        if discrepancy_type != "exact":
            discrepancies.append(comparison)

    missing_staged = [
        {
            "review_decision": "",
            "review_notes": "",
            "person_id": row["person_id"],
            "name_raw": row["name_raw"],
            "last_name": row["last_name"],
            "settlement": row["settlement"],
            "person_order_in_settlement": row["person_order_in_settlement"],
            "source_position_id": row["source_position_id"],
            "issue": "staged record not found in parsed book index",
        }
        for row in staged_rows
        if row["person_id"] not in matched_ids
    ]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "last_name_book_discrepancies.csv", discrepancies)
    write_csv(args.output_dir / "last_name_book_all_comparisons.csv", all_comparisons)
    write_csv(args.output_dir / "last_name_book_unmatched_reference.csv", unmatched_reference)
    write_csv(args.output_dir / "last_name_book_missing_staged.csv", missing_staged)
    write_csv(args.output_dir / "last_name_book_reference_entries.csv", entries)
    summary = {
        "pdf_pages": 58,
        "reference_entries_extracted": len(entries),
        "staged_records": len(staged_rows),
        "matched_records": len(matched_ids),
        "unmatched_reference_entries": len(unmatched_reference),
        "staged_records_missing_from_book": len(missing_staged),
        "discrepancy_records": len(discrepancies),
        "discrepancy_types": dict(sorted(discrepancy_types.items())),
        "review_categories": dict(sorted(review_categories.items())),
        "book_name_parsing_methods": dict(sorted(match_types.items())),
        "settlement_mapping_methods": dict(sorted(settlement_methods.items())),
    }
    (args.output_dir / "last_name_book_verification_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
