#!/usr/bin/env python3
"""Create an owner-review inventory for four-or-more-token canonical names."""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path


ORDINAL_RE = re.compile(r"^(?:\d+-(?:й|я|е)|\d+(?:й|я|е)|[IVX]+)$", re.IGNORECASE)


def patronymic_like(token: str, sex: str) -> bool:
    value = token.casefold()
    if sex == "Женский":
        return value.endswith(("овна", "евна", "ична", "инична", "ова", "ева", "ина"))
    if sex == "Мужской":
        return value.endswith(("ович", "евич", "ич", "ов", "ев", "ин"))
    return False


def classify(row):
    tokens = row["name_raw"].split()
    ordinal_tokens = [token for token in tokens if ORDINAL_RE.match(token)]
    semantic = [token for token in tokens if not ORDINAL_RE.match(token)]
    religion = row.get("religion", "")

    if len(semantic) == 3 and ordinal_tokens:
        return ("ordinal_marker_only", "high", row["name_raw"], row.get("name_alias", ""),
                "Three semantic name tokens plus an ordinal marker; preserve name_raw and do not create an alias.")
    if religion == "Магометанское":
        return ("complex_muslim_manual", "manual", "", "",
                "Complex Muslim/Mohammedan construction; no automatic normalization proposal.")
    if len(semantic) != 4:
        return ("complex_other_manual", "manual", "", "",
                "More than four semantic tokens or an unrecognized marker; manual classification required.")
    if patronymic_like(semantic[1], row.get("sex", "")):
        return ("fpl_alias_candidate", "medium", " ".join(semantic[:3]), semantic[3],
                "Second token has patronymic-like morphology; review whether the fourth token is an alias surname.")
    return ("double_given_or_other_manual", "manual", "", "",
            "Second token is not safely identifiable as a patronymic; may be a double given name or non-Russian structure.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()

    with args.input.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    output_rows = []
    for row in rows:
        tokens = row["name_raw"].split()
        if len(tokens) < 4:
            continue
        semantic = [token for token in tokens if not ORDINAL_RE.match(token)]
        category, confidence, proposed_name, proposed_alias, rationale = classify(row)
        output_rows.append({
            "person_id": row["person_id"],
            "source_position_id": row["source_position_id"],
            "district": row["district"],
            "settlement": row["settlement"],
            "page_number": row["page_number"],
            "household_id": row["household_id"],
            "sex": row["sex"],
            "religion": row["religion"],
            "family_status": row["family_status"],
            "current_name_raw": row["name_raw"],
            "current_name_alias": row.get("name_alias", ""),
            "raw_token_count": len(tokens),
            "semantic_token_count": len(semantic),
            "detected_ordinal_markers": " ".join(token for token in tokens if ORDINAL_RE.match(token)),
            "review_category": category,
            "proposal_confidence": confidence,
            "proposed_name_raw": proposed_name,
            "proposed_name_alias": proposed_alias,
            "proposal_rationale": rationale,
            "owner_decision": "Pending",
            "owner_name_raw": "",
            "owner_name_alias": "",
            "owner_notes": "",
        })

    fields = [
        "person_id", "source_position_id", "owner_decision", "owner_name_raw",
        "owner_name_alias", "owner_notes", "current_name_raw", "current_name_alias",
        "proposed_name_raw", "proposed_name_alias", "review_category",
        "proposal_confidence", "proposal_rationale", "detected_ordinal_markers",
        "raw_token_count", "semantic_token_count", "sex", "religion",
        "family_status", "district", "settlement", "page_number", "household_id",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output_rows)

    if args.summary:
        counts = Counter(row["review_category"] for row in output_rows)
        with args.summary.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["review_category", "record_count"])
            writer.writerows(sorted(counts.items()))


if __name__ == "__main__":
    main()
