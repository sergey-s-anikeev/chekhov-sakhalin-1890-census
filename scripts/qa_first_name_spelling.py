#!/usr/bin/env python3
"""Find probable first-name spelling errors without changing the dataset."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

CYRILLIC_RE = re.compile(r"^[А-ЯЁа-яё-]+$")
KNOWN_DISTINCT_VARIANTS = {
    "марфа", "даниил", "федот", "марианна", "моисей", "франциска",
    "ерофей", "игнат", "лазарь", "макрида", "мариана", "авдей", "галина",
    "георг", "марциана", "махмет", "мухамет", "ахмет", "нениль", "никола",
    "памфил", "лена", "трина",
}
REVIEWED_KEEP_IDS = {
    "P004583", "P004970", "P001959", "P000157", "P000672", "P002687",
    "P006166", "P000666", "P001002", "P001646", "P002191", "P007199",
    "P006493", "P005788", "P005773",
    "P004496",
    "P005626",  # Owner-confirmed historical first name: Рарица.
}


def norm(value: str) -> str:
    return (value or "").strip().casefold().replace("ё", "е")


def distance(a: str, b: str) -> int:
    """Optimal-string-alignment Damerau-Levenshtein distance."""
    a, b = norm(a), norm(b)
    matrix = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        matrix[i][0] = i
    for j in range(len(b) + 1):
        matrix[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            matrix[i][j] = min(
                matrix[i - 1][j] + 1,
                matrix[i][j - 1] + 1,
                matrix[i - 1][j - 1] + cost,
            )
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                matrix[i][j] = min(matrix[i][j], matrix[i - 2][j - 2] + 1)
    return matrix[-1][-1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument(
        "--lexicon", type=Path, default=Path(__file__).with_name("name_lexicon.csv")
    )
    args = parser.parse_args()

    with args.input.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    with args.lexicon.open(encoding="utf-8-sig", newline="") as handle:
        lexicon_rows = list(csv.DictReader(handle))

    accepted = [
        row for row in rows
        if row.get("parse_status") == "observed" and row.get("first_name")
    ]
    token_counts = Counter(
        norm(token)
        for row in accepted
        for token in row["first_name"].split()
    )

    tradition_by_model = {
        "russian_historical": {"russian_historical"},
        "catholic": {"catholic", "russian_historical"},
        "lutheran": {"lutheran", "russian_historical"},
        "muslim": {"muslim"},
        "other_documented": {"jewish", "russian_historical"},
        "unknown": {"russian_historical"},
    }
    lexicon = defaultdict(list)
    display = {}
    for entry in lexicon_rows:
        key = norm(entry["name"])
        lexicon[entry["sex"]].append((key, entry["tradition"]))
        display[key] = entry["name"].strip().title()

    candidates = []
    seen = set()
    for row in accepted:
        if row["person_id"] in REVIEWED_KEEP_IDS:
            continue
        model = row.get("naming_model", "unknown")
        sex = (
            "male" if row.get("sex") == "Мужской"
            else "female" if row.get("sex") == "Женский"
            else "unknown"
        )
        traditions = tradition_by_model.get(model, {"russian_historical"})
        allowed = [
            (key, tradition)
            for key, tradition in lexicon.get(sex, [])
            if tradition in traditions
        ] or lexicon.get(sex, [])

        tokens = row["first_name"].split()
        for token_index, token in enumerate(tokens):
            token_key = norm(token)
            if not token_key or token_key in display or token_key in KNOWN_DISTINCT_VARIANTS:
                continue

            base = {
                "review_decision": "Pending",
                "corrected_first_name": "",
                "review_notes": "",
                "person_id": row["person_id"],
                "name_raw": row["name_raw"],
                "first_name": row["first_name"],
                "suspect_token": token,
            }
            context = {
                "sex": row.get("sex", ""),
                "religion": row.get("religion", ""),
                "naming_model": model,
                "patronymic_name": row.get("patronymic_name", ""),
                "last_name": row.get("last_name", ""),
                "household_id": row.get("household_id", ""),
                "district": row.get("district", ""),
                "settlement": row.get("settlement", ""),
            }
            if not CYRILLIC_RE.fullmatch(token) or len(token_key) == 1 or "*" in token:
                candidates.append({
                    **base,
                    "proposed_first_name": "",
                    "proposed_token": "",
                    "edit_distance": "",
                    "priority": "high",
                    "suspect_frequency": token_counts[token_key],
                    "proposed_frequency": "",
                    "qa_reason": "placeholder, redacted, or non-name token in accepted first_name",
                    **context,
                })
                continue

            ranked = sorted(
                (distance(token_key, key), key, tradition)
                for key, tradition in allowed
            )
            if not ranked:
                continue
            best_distance, best_key, tradition = ranked[0]
            proposed_frequency = token_counts[best_key]
            likely = (
                best_distance == 1
                or (
                    best_distance == 2
                    and max(len(token_key), len(best_key)) >= 6
                    and (token_counts[token_key] >= 2 or proposed_frequency >= 20)
                )
                or token_key == "март"
            )
            if not likely:
                continue

            identity = (row["person_id"], token_index, best_key)
            if identity in seen:
                continue
            seen.add(identity)
            proposed_token = display[best_key]
            proposed_parts = list(tokens)
            proposed_parts[token_index] = proposed_token
            high = (
                token_key == "алексейандр"
                or (
                    best_distance == 1
                    and model == "russian_historical"
                    and proposed_frequency >= 20
                )
            )
            candidates.append({
                **base,
                "proposed_first_name": " ".join(proposed_parts),
                "proposed_token": proposed_token,
                "edit_distance": best_distance,
                "priority": "high" if high else "medium",
                "suspect_frequency": token_counts[token_key],
                "proposed_frequency": proposed_frequency,
                "qa_reason": (
                    f"unknown first-name token; nearest curated {tradition} form; "
                    f"edit_distance={best_distance}; "
                    f"dataset_frequency={token_counts[token_key]}"
                ),
                **context,
            })

    candidates.sort(
        key=lambda row: (
            0 if row["priority"] == "high" else 1,
            -int(row["suspect_frequency"]),
            row["suspect_token"],
            row["person_id"],
        )
    )
    fields = list(candidates[0]) if candidates else []
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(candidates)

    summary = {
        "input_records": len(rows),
        "accepted_first_name_records": len(accepted),
        "candidate_records": len(candidates),
        "candidate_unique_tokens": len({row["suspect_token"] for row in candidates}),
        "high_priority_records": sum(row["priority"] == "high" for row in candidates),
        "example_alekseiandr_records": [
            row["person_id"]
            for row in candidates
            if norm(row["suspect_token"]) == norm("Алексейандр")
        ],
    }
    args.summary.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
