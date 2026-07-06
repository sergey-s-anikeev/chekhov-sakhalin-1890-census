from __future__ import annotations

import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
CLEAN_CSV = BASE / "data_processed" / "clean_sample_500.csv"
MANUAL_DECISIONS_CSV = BASE / "outputs" / "qa" / "manual_review_decisions.csv"

UPDATES = {
    "P000452": {"origin_place": "Подольская губерния"},
    "P000143": {"origin_place": "Курляндская губерния"},
    "P000128": {"legal_status": "Ссыльнокаторжный"},
    "P000245": {
        "legal_status": "Дочь поселенца",
        "name_raw": "Анна Андреева Рудзит",
        "family_status": "Дочь",
        "age": "0",
        "religion": "Православное",
        "origin_place": "На Сахалине",
        "arrival_year": "",
        "occupation": "",
        "literacy": "",
        "marriage_status": "",
        "allowance_status": "FALSE",
        "illness": "",
        "comments": "4 месяца",
        "notes_raw": "РГБ № 4568",
    },
    "P000366": {
        "legal_status": "",
        "name_raw": "Аграфена Балаховская",
        "family_status": "Незаконнорожденная дочь",
        "age": "12",
        "religion": "Православное",
        "origin_place": "",
        "arrival_year": "",
        "occupation": "",
        "literacy": "неграмотен",
        "marriage_status": "",
        "allowance_status": "",
        "illness": "",
        "comments": "",
        "notes_raw": "РГБ № 5775",
    },
    "P000423": {"religion": "Православное"},
    "P000426": {
        "legal_status": "Поселенец",
        "name_raw": "Егор Васильев Зипов",
        "family_status": "Хозяин",
        "age": "53",
        "religion": "Православное",
        "origin_place": "Орловская губерния",
        "arrival_year": "",
        "occupation": "",
        "literacy": "неграмотен",
        "marriage_status": "холост",
        "allowance_status": "TRUE",
        "illness": "",
        "comments": "",
        "notes_raw": "РГБ № 6473",
    },
}

DECISIONS = [
    {
        "person_id": "P000128",
        "source_position_id": "3-29-037-0090",
        "page_number": "420",
        "settlement": "Пост Корсаковский",
        "name_raw": "Владимир Васильев Попов",
        "field": "legal_status",
        "source_value": "Сс[ылно]каторжный",
        "decision": "source typo / spelling variant",
        "action": "normalize to Ссыльнокаторжный",
        "status": "resolved",
        "notes": "Add this variant to legal_status normalization rules.",
    },
    {
        "person_id": "P000178",
        "source_position_id": "3-30-030-0040",
        "page_number": "425",
        "settlement": "Поро-ан-Томари",
        "name_raw": "Андрей Федоров Савельев",
        "field": "religion",
        "source_value": "1882",
        "decision": "confirmed source typo in original PDF",
        "action": "preserve printed value in religion; keep as confirmed source anomaly, not unresolved QA item",
        "status": "confirmed_source_anomaly",
        "notes": "Printed field 6 contains 1882; field 8 also contains 1882; РГБ № 5829.",
    },
    {
        "person_id": "P000245",
        "source_position_id": "3-33-013-0024",
        "page_number": "429",
        "settlement": "Третья Падь",
        "name_raw": "Анна Андреева Рудзит",
        "field": "category_code",
        "source_value": "name field printed as 5.; should be 4.",
        "decision": "confirmed source category-code typo",
        "action": "manually assign name/family_status/age/religion/origin/allowance to correct fields",
        "status": "resolved",
        "notes": "age set to 0 and comments set to 4 месяца.",
    },
    {
        "person_id": "P000366",
        "source_position_id": "3-35-027-0046",
        "page_number": "436",
        "settlement": "Лютога",
        "name_raw": "Аграфена Балаховская",
        "field": "category_code",
        "source_value": "field 3 contains name; legal_status is absent in original",
        "decision": "confirmed source category-code typo / missing legal_status",
        "action": "leave legal_status blank; manually assign name/family_status/age/religion/literacy to correct fields",
        "status": "resolved",
        "notes": "Do not infer legal_status.",
    },
    {
        "person_id": "P000423",
        "source_position_id": "3-38-001-0001",
        "page_number": "440",
        "settlement": "Лиственичное",
        "name_raw": "Захар Владимиров Владимиров",
        "field": "religion",
        "source_value": "Правосл авное",
        "decision": "spacing artifact / normalization variant",
        "action": "normalize to Православное",
        "status": "resolved",
        "notes": "Similar source text was normalized correctly in other records.",
    },
    {
        "person_id": "P000426",
        "source_position_id": "3-38-004-0004",
        "page_number": "440",
        "settlement": "Лиственичное",
        "name_raw": "Егор Васильев Зипов",
        "field": "category_code",
        "source_value": "field numbering shifted: name marked as 5., age as 6., religion as 7., origin as 8.",
        "decision": "confirmed source category-code shift",
        "action": "manually assign legal_status/name/family_status/age/religion/origin/literacy/marriage/allowance to correct fields",
        "status": "resolved",
        "notes": "arrival_year left blank because no source field 8 arrival year is present after correction.",
    },
    {
        "person_id": "P000143",
        "source_position_id": "3-30-003-0005",
        "page_number": "424",
        "settlement": "Поро-ан-Томари",
        "name_raw": "Екатерина Аузинг",
        "field": "origin_place",
        "source_value": "Курляндского",
        "decision": "source inflection / origin-place normalization",
        "action": "normalize to Курляндская губерния",
        "status": "resolved",
        "notes": "Mapped using MAIN_GUBERNIAS_1890 controlled reference list.",
    },
    {
        "person_id": "P000452",
        "source_position_id": "3-39-009-0015",
        "page_number": "441",
        "settlement": "Хомутовка",
        "name_raw": "Петр Иванов Побережнюк",
        "field": "origin_place",
        "source_value": "Каменецк-Подольская",
        "decision": "source variant / origin-place normalization",
        "action": "normalize to Подольская губерния",
        "status": "resolved",
        "notes": "Mapped using MAIN_GUBERNIAS_1890 controlled reference list.",
    },

]


def main() -> None:
    df = pd.read_csv(CLEAN_CSV, dtype=str, keep_default_na=False)

    for person_id, fields in UPDATES.items():
        mask = df["person_id"] == person_id
        if mask.sum() != 1:
            raise ValueError(f"Expected exactly one row for {person_id}, found {mask.sum()}")
        for column, value in fields.items():
            df.loc[mask, column] = value

    df.to_csv(CLEAN_CSV, index=False, encoding="utf-8")
    pd.DataFrame(DECISIONS).to_csv(MANUAL_DECISIONS_CSV, index=False, encoding="utf-8")


if __name__ == "__main__":
    main()
