"""Profile and propose source-faithful precise-age extraction for Item 8."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/staging/age_item7_20260713/clean_sakhalin_1890_ru_v3_20260712_age_item7_staged.csv"
REVIEW_DIR = ROOT / "data/review/infant_age_item8_20260713"
QA_DIR = ROOT / "outputs/qa/infant_age_item8_20260713"

AGE_PREFIX = re.compile(
    r"^\s*(?:"
    r"(?P<years>\d+)\s+(?:года|год|лет)(?:\s+(?P<year_months>\d+)\s+(?:месяцев|месяца|месяц))?"
    r"|(?P<months>\d+)\s+(?:месяцев|месяца|месяц)"
    r"|(?P<weeks>\d+)\s+(?:недель|недели|неделя)"
    r"|(?P<days>\d+)\s+(?:дней|дня|день)"
    r")(?P<separator>\s*;\s*)?(?P<residual>.*)$",
    re.IGNORECASE,
)

OUTPUT_COLUMNS = [
    "person_id",
    "source_position_id",
    "page_number",
    "district",
    "settlement",
    "name_raw",
    "age",
    "comments",
    "age_text_raw_proposed",
    "age_months_proposed",
    "age_weeks_proposed",
    "age_days_proposed",
    "comments_residual_preview",
    "parse_type",
    "review_required",
    "review_notes",
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


def main() -> None:
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as handle:
        source_rows = list(csv.DictReader(handle))

    proposals: list[dict[str, str]] = []
    for row in source_rows:
        comments = row["comments"].strip()
        match = AGE_PREFIX.match(comments)
        if not match:
            continue
        values = match.groupdict()
        if values["years"] is not None:
            years = int(values["years"])
            months = int(values["year_months"] or 0)
            age_months = str(years * 12 + months)
            parse_type = "years_and_months" if values["year_months"] is not None else "years_only"
        elif values["months"] is not None:
            age_months = values["months"]
            parse_type = "months"
        elif values["weeks"] is not None:
            age_months = ""
            parse_type = "weeks"
        else:
            age_months = ""
            parse_type = "days"

        residual = (values["residual"] or "").strip()
        if values["separator"]:
            age_text = comments[: match.start("separator")].strip()
        else:
            age_text = comments[: match.start("residual")].strip()
        expected_years = int(age_months) // 12 if age_months else 0
        review_notes = []
        if age_months and int(row["age"]) != expected_years:
            review_notes.append("AGE_YEARS_DOES_NOT_MATCH_COMPLETED_TOTAL_MONTHS")
        if parse_type in {"weeks", "days"} and row["age"] != "0":
            review_notes.append("SUBMONTH_AGE_WITH_NONZERO_AGE")

        proposals.append(
            {
                "person_id": row["person_id"],
                "source_position_id": row["source_position_id"],
                "page_number": row["page_number"],
                "district": row["district"],
                "settlement": row["settlement"],
                "name_raw": row["name_raw"],
                "age": row["age"],
                "comments": row["comments"],
                "age_text_raw_proposed": age_text,
                "age_months_proposed": age_months,
                "age_weeks_proposed": values["weeks"] or "",
                "age_days_proposed": values["days"] or "",
                "comments_residual_preview": residual,
                "parse_type": parse_type,
                "review_required": "YES" if review_notes else "NO",
                "review_notes": "; ".join(review_notes),
            }
        )

    proposals.sort(key=lambda row: (int(row["page_number"]), row["person_id"]))
    write_csv(REVIEW_DIR / "infant_age_extraction_proposal.csv", proposals, OUTPUT_COLUMNS)

    type_counts = Counter(row["parse_type"] for row in proposals)
    age_counts = Counter(row["age"] for row in proposals)
    residual_counts = Counter("nonblank" if row["comments_residual_preview"] else "blank" for row in proposals)
    write_csv(
        REVIEW_DIR / "infant_age_unit_summary.csv",
        [
            {"parse_type": key, "record_count": str(value)}
            for key, value in sorted(type_counts.items())
        ],
        ["parse_type", "record_count"],
    )
    write_csv(
        REVIEW_DIR / "infant_age_source_age_summary.csv",
        [
            {"current_age": key, "record_count": str(value)}
            for key, value in sorted(age_counts.items(), key=lambda item: int(item[0]))
        ],
        ["current_age", "record_count"],
    )

    qa = {
        "item": 8,
        "mode": "read-only extraction proposal; comments unchanged",
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": sha256(SOURCE),
        "source_record_count": len(source_rows),
        "explicit_precise_age_phrase_count": len(proposals),
        "parse_type_counts": dict(sorted(type_counts.items())),
        "current_age_counts": dict(sorted(age_counts.items(), key=lambda item: int(item[0]))),
        "residual_comment_counts": dict(sorted(residual_counts.items())),
        "manual_review_count": sum(row["review_required"] == "YES" for row in proposals),
        "page_number_present_count": sum(bool(row["page_number"]) for row in proposals),
        "unique_person_id_count": len({row["person_id"] for row in proposals}),
        "comments_modified": False,
        "canonical_files_modified": False,
    }
    QA_DIR.mkdir(parents=True, exist_ok=True)
    (QA_DIR / "infant_age_item8_profile.json").write_text(
        json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    recommendation = f"""# Item 8 precise infant/young-child age proposal

## Finding

The leading age phrase can be extracted deterministically from {len(proposals):,} `comments` values. The current `age` field remains completed years. No comment text is changed in this proposal.

## Recommended representation

Use `age_months` as the primary numeric precision field for expressions stated in months or in years plus months. Months are the dominant source unit and total completed months preserve the existing completed-year interpretation (`age == age_months // 12`). Do not convert weeks or days into fractional months because that would add an unsupported conversion assumption.

Also retain `age_text_raw` as the exact extracted source phrase. For the 17 explicit week/day expressions, leave `age_months` blank and preserve their exact wording in `age_text_raw`. Separate `age_weeks` and `age_days` columns are not recommended for the final minimal schema because the exact submonth values are already retained and the fields would be populated in only 15 and two records respectively.

## Comment handling

Copy only the leading age phrase into `age_text_raw`. Preserve `comments` unchanged during Item 8. `comments_residual_preview` shows what would remain if the age phrase were removed in a later, separately approved comment-cleanup item; it is evidence only and is not a proposed edit now.
"""
    (QA_DIR / "infant_age_item8_recommendation.md").write_text(recommendation, encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
