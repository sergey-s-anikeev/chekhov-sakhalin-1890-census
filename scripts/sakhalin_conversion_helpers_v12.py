from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


def normalize_pdf_artifacts(value: str) -> str:
    """Remove PDF extraction artifacts that split words or produce invisible separators."""
    value = value.replace("\u00ad", "")   # soft hyphen
    value = value.replace("\ufffe", "")   # artifact visible as ￾ in extracted text
    value = value.replace("\ufeff", "")   # BOM / zero-width no-break space
    value = value.replace("\xa0", " ")    # non-breaking space
    value = value.replace("\u200b", "")   # zero-width space
    value = value.replace("–", "-")
    return value


def base_text(value: Any) -> str:
    """Minimal string cleanup: null handling, PDF artifacts, whitespace."""
    if value is None:
        return ""

    value = str(value).strip()
    if value.lower() in {"nan", "none", "null"}:
        return ""

    value = normalize_pdf_artifacts(value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def remove_source_field_prefix(value: str) -> str:
    """Remove source field prefixes such as '3.', '6.', '7.', '10.', '14.'."""
    return re.sub(r"^\s*\d+\.\s*", "", value).strip()


def normalize_source_markup(value: str) -> str:
    """
    Source markup:
    - <angle brackets> = crossed-out words; remove them.
    - [square brackets] = restored parts of words; keep letters but remove brackets.

    If a PDF extraction artifact inserts a space before a restored word part,
    remove that space before bracket restoration:
    - Правосл [авного] -> Правосл[авного] -> Православного

    This is especially important for one-word fields such as religion and occupation.
    """
    value = re.sub(r"<[^>]*>", " ", value)
    value = re.sub(r"(?<=[А-Яа-яЁёA-Za-z])\s+(?=\[)", "", value)
    value = value.replace("[", "").replace("]", "")
    value = re.sub(r"\s+", " ", value).strip()
    return value




def ignore_inline_special_symbols(value: str) -> str:
    """Remove non-semantic uncertainty/separator symbols inside normalized field values.

    These symbols often come from editorial uncertainty marks or PDF extraction,
    and should not prevent normalization:
    - `/39?/` -> `39`
    - `холост (?)` -> `холост`

    Do not use this for comments or archive-note fields where punctuation may be
    meaningful.
    """
    value = re.sub(r"[/?,()]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def remove_trailing_footnote_digits(value: str) -> str:
    """
    Remove trailing bare footnote digits:
    - 'Вера Суменко2' -> 'Вера Суменко'
    - 'Дочь поселенца1' -> 'Дочь поселенца'
    - 'На Сахалине6' -> 'На Сахалине'

    Preserve ordinal markers:
    - 'Марья Алексеева Попова 2-я'
    - 'Андрей Иванов 1-й'
    """
    value = re.sub(r"\s*\d+$", "", value).strip()
    return value


def clean_text(
    value: Any,
    *,
    remove_trailing_footnotes: bool = True,
    ignore_special_symbols: bool = True,
) -> str:
    """
    General text-field cleanup.

    Use remove_trailing_footnotes=False for:
    - comments, because it may contain age notes such as '7 месяцев' or '1 год 5 месяцев';
    - notes_raw, because it must preserve archival numbers such as 'РГБ № 6810'.
    """
    value = base_text(value)
    if not value:
        return ""

    value = remove_source_field_prefix(value)
    value = normalize_source_markup(value)
    if ignore_special_symbols:
        value = ignore_inline_special_symbols(value)
    value = re.sub(r"\s+", " ", value).strip()

    if remove_trailing_footnotes:
        # Remove inline source footnote digits attached directly to words:
        #   Алексеев2 Самудоров3 -> Алексеев Самудоров
        # This does not affect ordinal markers written as separate tokens, e.g. 1-й or 2й.
        value = re.sub(r"(?<=[А-Яа-яЁё])\d+(?=\s|$|[.,;:])", "", value)
        value = remove_trailing_footnote_digits(value)

    return value


def clean_preserve_comments(value: Any) -> str:
    return clean_text(value, remove_trailing_footnotes=False, ignore_special_symbols=False)



SETTLEMENTS = {
    "Александровское": {"settlement_order": "01", "district_code": "1", "district": "Александровский", "type": "селение", "page_start": 27},
    "Пост Александровский": {"settlement_order": "02", "district_code": "1", "district": "Александровский", "type": "пост", "page_start": 33},
    "Корсаковское": {"settlement_order": "03", "district_code": "1", "district": "Александровский", "type": "селение", "page_start": 115},
    "Ново-Михайловское": {"settlement_order": "04", "district_code": "1", "district": "Александровский", "type": "селение", "page_start": 131},
    "Красный Яр": {"settlement_order": "05", "district_code": "1", "district": "Александровский", "type": "селение", "page_start": 158},
    "Бутаково": {"settlement_order": "06", "district_code": "1", "district": "Александровский", "type": "селение", "page_start": 164},
    "Арковский кордон": {"settlement_order": "07", "district_code": "1", "district": "Александровский", "type": "кордон", "page_start": 165},
    "Арково I": {"settlement_order": "08", "district_code": "1", "district": "Александровский", "type": "селение", "page_start": 165},
    "Арково II": {"settlement_order": "09", "district_code": "1", "district": "Александровский", "type": "селение", "page_start": 173},
    "Арковский станок": {"settlement_order": "10", "district_code": "1", "district": "Александровский", "type": "станок", "page_start": 178},
    "Арково III": {"settlement_order": "11", "district_code": "1", "district": "Александровский", "type": "селение", "page_start": 179},
    "Мгачи": {"settlement_order": "12", "district_code": "1", "district": "Александровский", "type": "селение", "page_start": 181},
    "Танги": {"settlement_order": "13", "district_code": "1", "district": "Александровский", "type": "селение", "page_start": 183},
    "Хоэ": {"settlement_order": "14", "district_code": "1", "district": "Александровский", "type": "селение", "page_start": 184},
    "Трамбаус": {"settlement_order": "15", "district_code": "1", "district": "Александровский", "type": "селение", "page_start": 185},
    "Виахты": {"settlement_order": "16", "district_code": "1", "district": "Александровский", "type": "селение", "page_start": 185},
    "Ванги": {"settlement_order": "17", "district_code": "1", "district": "Александровский", "type": "селение", "page_start": 186},
    "Пост Дуэ": {"settlement_order": "18", "district_code": "1", "district": "Александровский", "type": "пост", "page_start": 187},
    "Верхний Армудан": {"settlement_order": "19", "district_code": "2", "district": "Тымовский", "type": "селение", "page_start": 223},
    "Нижний Армудан": {"settlement_order": "20", "district_code": "2", "district": "Тымовский", "type": "селение", "page_start": 233},
    "Дербинское": {"settlement_order": "21", "district_code": "2", "district": "Тымовский", "type": "селение", "page_start": 238},
    "Воскресенское": {"settlement_order": "22", "district_code": "2", "district": "Тымовский", "type": "селение", "page_start": 273},
    "Усково": {"settlement_order": "23", "district_code": "2", "district": "Тымовский", "type": "селение", "page_start": 282},
    "Рыковское": {"settlement_order": "24", "district_code": "2", "district": "Тымовский", "type": "селение", "page_start": 285},
    "Палево": {"settlement_order": "25", "district_code": "2", "district": "Тымовский", "type": "селение", "page_start": 357},
    "Мало-Тымово": {"settlement_order": "26", "district_code": "2", "district": "Тымовский", "type": "селение", "page_start": 372},
    "Андрее-Ивановское": {"settlement_order": "27", "district_code": "2", "district": "Тымовский", "type": "селение", "page_start": 383},
    "Маука": {"settlement_order": "28", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 413},
    "Пост Корсаковский": {"settlement_order": "29", "district_code": "3", "district": "Корсаковский", "type": "пост", "page_start": 415},
    "Поро-ан-Томари": {"settlement_order": "30", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 423},
    "Первая Падь": {"settlement_order": "31", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 427},
    "Вторая Падь": {"settlement_order": "32", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 427},
    "Третья Падь": {"settlement_order": "33", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 428},
    "Соловьевка": {"settlement_order": "34", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 430},
    "Лютога": {"settlement_order": "35", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 434},
    "Голый Мыс": {"settlement_order": "36", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 437},
    "Мицулька": {"settlement_order": "37", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 438},
    "Лиственичное": {"settlement_order": "38", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 440},
    "Хомутовка": {"settlement_order": "39", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 440},
    "Большая Елань": {"settlement_order": "40", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 442},
    "Владимировка": {"settlement_order": "41", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 445},
    "Луговое": {"settlement_order": "42", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 449},
    "Поповские Юрты": {"settlement_order": "43", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 453},
    "Березники": {"settlement_order": "44", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 459},
    "Кресты": {"settlement_order": "45", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 468},
    "Большое Такоэ": {"settlement_order": "46", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 473},
    "Малое Такоэ": {"settlement_order": "47", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 476},
    "Сиянцы": {"settlement_order": "48", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 479},
    "Дубки": {"settlement_order": "49", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 483},
    "Сиска": {"settlement_order": "50", "district_code": "3", "district": "Корсаковский", "type": "селение", "page_start": 485},
    "Тарайское Зимовье": {"settlement_order": "51", "district_code": "3", "district": "Корсаковский", "type": "зимовье", "page_start": 485},
}


FINAL_FIELD_ORDER = [
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


# Apply trailing bare footnote digit cleanup to these text fields.
# Do not apply it to comments or notes_raw.
TEXT_COLUMNS_FOR_TRAILING_FOOTNOTE_CLEANUP = [
    "legal_status",
    "name_raw",
    "family_status",
    "religion",
    "origin_place",
    "occupation",
    "literacy",
    "marriage_status",
    "illness",
]


TEXT_COLUMNS_FOR_TRAILING_FOOTNOTE_QA = TEXT_COLUMNS_FOR_TRAILING_FOOTNOTE_CLEANUP



LEGAL_STATUS_CANONICAL_VALUES = {
    "Дочь крестьянина из ссыльных",
    "Дочь крестьянки из ссыльных",
    "Дочь поселенца",
    "Дочь поселенца. Дочь",
    "Дочь поселки",
    "Дочь солдатки",
    "Дочь ссыльнокаторжного",
    "Дочь ссыльнокаторжной",
    "Жена рядового",
    "Женщина свободного состояния",
    "Женщина свободного состояния. Жена",
    "Крестьянин",
    "Крестьянин из крестьян",
    "Крестьянин из ссыльных",
    "Крестьянка из ссыльных",
    "Отставной фельдфебель",
    "Поселенец",
    "Поселка",
    "Ссыльнокаторжный",
    "Свободного состояния",
    "Ссыльнокаторжная",
    "Старший надзиратель",
    "Сын крестьянина из ссыльных",
    "Сын крестьянки из ссыльных",
    "Сын поселенца",
    "Сын поселки",
    "Сын солдатки",
    "Сын ссыльнокаторжного",
    "Сын ссыльнокаторжной",
    "Административно сосланный",
    "Дочь каторжного",
    "Жена свободного состояния",
    "Запасный ефрейтор",
    "Запасный рядовой",
    "Запасный унтер-офицер",
    "Крестьянин из поселенцев",
    "Крестьянин из ссыльнопоселенцев",
    "Крестьянин свободного состояния",
    "Крестьянка",
    "Незаконнорожденная дочь поселки",
    "Отставной унтер-офицер",
    "Поселенец-богадельщик",
    "Поселка (богадельщик)",
    "Свободного состояния жена",
    "Свободного состояния жена поселенца",
    "Совладелец",
    "Сын каторжного",
    "Сын каторжной",
    "Сын крестьянки",
    "Уволенный в запас Армии Рядовой",
    "Унтер-офицер",
}


def _legal_status_key(value: str) -> str:
    value = base_text(value)

    # Fix mixed Latin/Cyrillic letters commonly produced during extraction or manual entry.
    # Example: "Сcыльнокаторжный" where the second "c" is Latin.
    value = value.replace("c", "с").replace("C", "С")

    value = value.replace("ё", "е")
    value = value.lower()
    value = re.sub(r"\s+", " ", value).strip(" .")
    value = re.sub(r"\s*\.\s*", ". ", value).strip()
    return value


def _build_legal_status_canonical_map() -> dict[str, str]:
    mapping: dict[str, str] = {}

    def add(canonical: str, *variants: str) -> None:
        mapping[_legal_status_key(canonical)] = canonical
        for variant in variants:
            mapping[_legal_status_key(variant)] = canonical

    add("Дочь крестьянина из ссыльных")
    add("Дочь крестьянки из ссыльных")
    add("Дочь поселенца", "Дочь поселенца.", "Дочь поселенца1")
    add("Дочь поселенца. Дочь", "Дочь поселенца дочь", "Дочь поселенца. дочь")
    add("Дочь поселки")
    add("Дочь солдатки")
    add("Дочь ссыльнокаторжного", "Дочь ссыльно каторжного", "Дочь сс. каторжного")
    add("Дочь ссыльнокаторжной", "Дочь ссыльно каторжной", "Дочь сс. каторжной", "Дочь ссыльноторжной", "Дочь сс[ыльно]торжной")

    add("Жена рядового")
    add("Женщина свободного состояния", "Ж свободного состояния", "Ж. свободного состояния", "Женщина св состояния", "Женщина св. состояния")
    add("Женщина свободного состояния. Жена", "Женщина свободного состояния жена", "Женщина св состояния жена", "Женщина св. состояния. Жена")

    add("Крестьянин")
    add("Крестьянин из крестьян", "Крестьянин из крестян")
    add("Крестьянин из ссыльных", "Крестьянин из сс", "Крестьянин из ссыл", "Крестьянин из ссыльн", "Крестьянин из ссыльных.", "крестьянин из ссыльных")
    add("Крестьянка из ссыльных", "Крестьянка из сс", "Крестьянка из ссыл", "Крестьянка из ссыльн")

    add("Отставной фельдфебель")
    add("Поселенец", "Поселенец.", "поселенец", "Поселеленец")
    add("Поселка", "Поселка.", "поселка")

    add("Ссыльнокаторжный", "Сcыльнокаторжный", "Сс каторжный", "Сс. каторжный", "Ссыльно каторжный", "Ссыльно-каторжный", "Ссылнокаторжный", "Сс[ылно]каторжный")
    add("Ссыльнокаторжная", "Сcыльнокаторжная", "Сс каторжная", "Сс. каторжная", "Ссыльно каторжная", "Ссыльно-каторжная", "Ссылнокаторжная", "Сс[ылно]каторжная", "Ссыльноъкаторжная", "Сс[ыльноъкаторжная", "Ссыльнокаторжная. Сожительница", "Сс[ыльно]каторжная. Сожительница")

    add("Свободного состояния")
    add("Старший надзиратель")

    add("Сын крестьянина из ссыльных")
    add("Сын крестьянки из ссыльных")
    add("Сын поселенца")
    add("Сын поселки")
    add("Сын солдатки")
    add("Сын ссыльнокаторжного", "Сын ссыльно каторжного", "Сын сс. каторжного")
    add("Сын ссыльнокаторжной", "Сын ссыльно каторжной", "Сын сс. каторжной")

    add("Унтер-офицер", "Унтер офицер")

    # Tymovsky District: additional legal-status values reviewed manually.
    add("Административно сосланный", "Административно-сосланный")
    add("Дочь каторжного")
    add("Дочь поселенца", "Дочь поселен ца")
    add("Дочь ссыльнокаторжного", "Дочь сыльнокаторжного")
    add("Дочь ссыльнокаторжной", "Дочь ссыльнокаторжная")
    add("Жена свободного состояния")
    add("Запасный ефрейтор")
    add("Запасный рядовой")
    add("Запасный унтер-офицер", "Запасной унтер-офицер")
    add("Крестьянин из поселенцев")
    add("Крестьянин из ссыльнопоселенцев")
    add("Крестьянин из ссыльных", "Крестьянин изссыльных", "Крестьянин из сыльных")
    add("Крестьянин свободного состояния")
    add("Крестьянка")
    add("Крестьянка из ссыльных", "Крестьянка из сыльных", "Крестьянка из сссыльных")
    add("Незаконнорожденная дочь поселки")
    add("Отставной унтер-офицер", "Отставной унтер офицер")
    add("Поселка", "Посел ка")
    add("Поселенец-богадельщик", "Поселенец богадельщик")
    add("Поселка (богадельщик)", "Поселка богадельщик")
    add("Свободного состояния", "Свобного состояния")
    add("Свободного состояния жена")
    add("Свободного состояния жена поселенца")
    add("Совладелец")
    add("Сын каторжного")
    add("Сын каторжной")
    add("Сын крестьянки")
    add("Сын поселенца", "Сын посенца")
    add("Сын ссыльнокаторжной", "Сын сыльнокаторжной", "Сын ссыльнокажной")
    add("Уволенный в запас Армии Рядовой")
    add("Ссыльнокаторжный", "Ссыльнокаторржный")
    add("Ссыльнокаторжная", "Ссылльнокаторжная", "Ссыльнокатожная")

    return mapping


LEGAL_STATUS_CANONICAL_MAP = _build_legal_status_canonical_map()


def normalize_legal_status(value: Any) -> str:
    """
    Normalize legal_status against an expandable controlled vocabulary.

    If a cleaned value is not in LEGAL_STATUS_CANONICAL_MAP, preserve it.
    QA will report it for manual review instead of silently changing it.
    """
    value = clean_text(value, remove_trailing_footnotes=True)
    if not value:
        return ""

    # Fix mixed Latin/Cyrillic letters before lookup.
    value = value.replace("c", "с").replace("C", "С")

    # Common post-cleanup source expansions after square-bracket restoration.
    value = re.sub(r"\bСсыльно\s*каторжн", "Ссыльнокаторжн", value)
    value = re.sub(r"\bСсыльно[-\s]+каторжн", "Ссыльнокаторжн", value)
    value = re.sub(r"\bссыльно[-\s]+каторжн", "ссыльнокаторжн", value)
    value = re.sub(r"\bсс\.?\s*каторжн", "ссыльнокаторжн", value, flags=re.IGNORECASE)
    value = re.sub(r"\bс\s*сыльн", "ссыльн", value, flags=re.IGNORECASE)

    value = re.sub(r"\bЖ\.?\s*св\.?\s*состояния\b", "Женщина свободного состояния", value, flags=re.IGNORECASE)
    value = re.sub(r"\bсв\.?\s*состояния\b", "свободного состояния", value, flags=re.IGNORECASE)
    value = re.sub(r"\s+", " ", value).strip(" .")

    key = _legal_status_key(value)
    if key in LEGAL_STATUS_CANONICAL_MAP:
        return LEGAL_STATUS_CANONICAL_MAP[key]

    # Try with sentence-like capitalization normalized.
    candidate = value[:1].upper() + value[1:] if value else value
    key = _legal_status_key(candidate)
    if key in LEGAL_STATUS_CANONICAL_MAP:
        return LEGAL_STATUS_CANONICAL_MAP[key]

    return candidate



FAMILY_STATUS_CANONICAL_VALUES = {
    "Совладелица",
    "Приемыш незаконный внук",
    "Сожительница № 1",
    "Сожительница № 2",
    "Брат",
    "Дочь",
    "Жена",
    "Жена жильца",
    "Жилец",
    "Жилица",
    "Мать",
    "Незаконнорожденная дочь",
    "Незаконнорожденная дочь сожительницы",
    "Незаконнорожденный сын",
    "Незаконнорожденный сын жилицы",
    "Незаконнорожденный сын сожительницы",
    "Отец",
    "Приемная дочь",
    "Работник",
    "Совладелец",
    "Сожитель",
    "Сожительница",
    "Сожительница жильца",
    "Сын",
    "Хозяин",
    "Хозяйка",
    "Брат совладельца",
    "Брат сожительницы",
    "В работниках",
    "Внучка",
    "Дочь жильца",
    "Дочь работника",
    "Дочь совладельца",
    "Дочь сожительницы",
    "Жена отца",
    "Жена работника",
    "Жена совладельца",
    "Жилец. Совладелец",
    "Зять",
    "Мать сожительницы",
    "На воспитании. Сын",
    "Невестка",
    "Незаконнорожденная дочь жены",
    "Незаконнорожденная дочь совладелицы",
    "Незаконнорожденная дочь совладельца",
    "Незаконнорожденный сын жены",
    "Незаконнорожденный сын жильца",
    "Незаконнорожденный сын совладелицы",
    "Незаконнорожденный сын совладельца",
    "Незаконнорожденный сын. Приемный",
    "Падчерица",
    "Приемная дочь жильца",
    "Приемный отец",
    "Приемный сын",
    "Прислуга",
    "Свекровь сожительницы",
    "Сожительница совладельца",
    "Сын жильца",
    "Сын работника",
    "Сын совладельца",
    "Сын сожительницы",
}


def _family_status_key(value: str) -> str:
    value = base_text(value)
    # Fix mixed Latin/Cyrillic letters in family-status values.
    value = value.replace("c", "с").replace("C", "С")
    value = value.replace("ё", "е")
    value = value.lower()
    value = re.sub(r"\s+", " ", value).strip(" .")
    value = re.sub(r"\s*\.\s*", ". ", value).strip()
    return value


def _build_family_status_canonical_map() -> dict[str, str]:
    mapping: dict[str, str] = {}

    def add(canonical: str, *variants: str) -> None:
        mapping[_family_status_key(canonical)] = canonical
        for variant in variants:
            mapping[_family_status_key(variant)] = canonical

    add("Брат")
    add("Дочь")
    add("Жена")
    add("Жена жильца")
    add("Жилец")
    add("Жилица")
    add("Мать")

    add("Незаконнорожденная дочь", "Незаконнорожденная дочка", "Незаконно рожденная дочь", "Незаконно-рожденная дочь", "Незак. дочь")
    add("Незаконнорожденная дочь сожительницы", "Незаконно рожденная дочь сожительницы", "Незаконно-рожденная дочь сожительницы", "Незаконнорожденный дочь сожительницы")
    add("Незаконнорожденный сын", "Незаконно рожденный сын", "Незаконно-рожденный сын", "Незак. сын")
    add("Незаконнорожденный сын жилицы", "Незаконно рожденный сын жилицы", "Незаконно-рожденный сын жилицы")
    add("Незаконнорожденный сын сожительницы", "Незаконно рожденный сын сожительницы", "Незаконно-рожденный сын сожительницы")

    add("Отец")
    add("Приемная дочь", "Приёмная дочь")
    add("Работник")
    add("Совладелец")
    add("Сожитель")
    add("Сожительница", "Сожител ьница", "Сожителььница")
    add("Сожительница жильца")
    add("Сын")
    add("Хозяин")
    add("Хозяйка")

    # Tymovsky District: additional household/family roles reviewed manually.
    add("Брат совладельца")
    add("Брат сожительницы")
    add("В работниках")
    add("Внучка")
    add("Дочь жильца")
    add("Дочь работника")
    add("Дочь совладельца")
    add("Дочь сожительницы")
    add("Жена отца")
    add("Жена работника")
    add("Жена совладельца", "Жена совл1адельца")
    add("Жилец. Совладелец", "Жилец совладелец")
    add("Зять")
    add("Мать сожительницы")
    add("На воспитании. Сын", "На воспитании сын")
    add("Невестка")
    add("Незаконнорожденная дочь жены")
    add("Незаконнорожденная дочь совладелицы")
    add("Незаконнорожденная дочь совладельца")
    add("Незаконнорожденный сын жены")
    add("Незаконнорожденный сын жильца")
    add("Незаконнорожденный сын совладелицы")
    add("Незаконнорожденный сын совладельца", "Незаконорожденный сын совладельца")
    add("Незаконнорожденный сын. Приемный", "Незаконнорожденный сын приемный")
    add("Падчерица")
    add("Приемная дочь жильца", "Приёмная дочь жильца")
    add("Приемный отец", "Приёмный отец")
    add("Приемный сын", "Приёмный сын")
    add("Прислуга")
    add("Свекровь сожительницы")
    add("Сожительница совладельца", "Сожитильница совладельца")
    add("Сын жильца")
    add("Сын работника")
    add("Сын совладельца")
    add("Сын сожительницы")


    add("Совладелица", "Совладелица.", "Со владелица")
    add("Приемыш незаконный внук", "/Приемыш незакон/ный внук", "Приемыш незаконный внук")
    add("Сожительница № 1")
    add("Сожительница № 2")

    return mapping


FAMILY_STATUS_CANONICAL_MAP = _build_family_status_canonical_map()


def normalize_family_status(value: Any) -> str:
    """
    Normalize family_status against an expandable controlled vocabulary.

    If a cleaned value is not in FAMILY_STATUS_CANONICAL_MAP, preserve it.
    QA will report it for manual review instead of silently changing it.
    """
    value = clean_text(value, remove_trailing_footnotes=True)
    if not value:
        return ""

    # Normalize common source/restoration variants.
    value = value.replace("c", "с").replace("C", "С")
    value = value.replace("ё", "е")
    value = re.sub(r"\bНезаконно\s*рожденн", "Незаконнорожденн", value, flags=re.IGNORECASE)
    value = re.sub(r"\bНезаконно[-\s]+рожденн", "Незаконнорожденн", value, flags=re.IGNORECASE)
    value = re.sub(r"\bНезак\.\s*сын\b", "Незаконнорожденный сын", value, flags=re.IGNORECASE)
    value = re.sub(r"\bНезак\.\s*дочь\b", "Незаконнорожденная дочь", value, flags=re.IGNORECASE)
    value = re.sub(r"\s+", " ", value).strip(" .")

    key = _family_status_key(value)
    if key in FAMILY_STATUS_CANONICAL_MAP:
        return FAMILY_STATUS_CANONICAL_MAP[key]

    candidate = value[:1].upper() + value[1:] if value else value
    key = _family_status_key(candidate)
    if key in FAMILY_STATUS_CANONICAL_MAP:
        return FAMILY_STATUS_CANONICAL_MAP[key]

    return candidate


# Canonical 1890 administrative units for origin_place.
# Source: administrative_units_russian_empire_1890.md.
# Gubernias are normalized to their full official form, e.g. "Тверская губерния".
# Oblasts are normalized to their full official form, e.g. "Терская область".
MAIN_GUBERNIAS_1890 = {
    "Архангельская губерния",
    "Астраханская губерния",
    "Бакинская губерния",
    "Бессарабская губерния",
    "Виленская губерния",
    "Витебская губерния",
    "Владимирская губерния",
    "Вологодская губерния",
    "Волынская губерния",
    "Воронежская губерния",
    "Вятская губерния",
    "Гродненская губерния",
    "Екатеринославская губерния",
    "Елисаветпольская губерния",
    "Енисейская губерния",
    "Иркутская губерния",
    "Казанская губерния",
    "Калужская губерния",
    "Киевская губерния",
    "Ковенская губерния",
    "Костромская губерния",
    "Курляндская губерния",
    "Курская губерния",
    "Кутаисская губерния",
    "Лифляндская губерния",
    "Минская губерния",
    "Могилёвская губерния",
    "Московская губерния",
    "Нижегородская губерния",
    "Новгородская губерния",
    "Олонецкая губерния",
    "Оренбургская губерния",
    "Орловская губерния",
    "Пензенская губерния",
    "Пермская губерния",
    "Подольская губерния",
    "Полтавская губерния",
    "Псковская губерния",
    "Рязанская губерния",
    "Самарская губерния",
    "Санкт-Петербургская губерния",
    "Саратовская губерния",
    "Симбирская губерния",
    "Смоленская губерния",
    "Ставропольская губерния",
    "Таврическая губерния",
    "Тамбовская губерния",
    "Тверская губерния",
    "Тифлисская губерния",
    "Тобольская губерния",
    "Томская губерния",
    "Тульская губерния",
    "Уфимская губерния",
    "Харьковская губерния",
    "Херсонская губерния",
    "Черниговская губерния",
    "Эриванская губерния",
    "Эстляндская губерния",
    "Ярославская губерния",
}

POLISH_GUBERNIAS_1890 = {
    "Варшавская губерния",
    "Калишская губерния",
    "Келецкая губерния",
    "Ломжинская губерния",
    "Люблинская губерния",
    "Петроковская губерния",
    "Плоцкая губерния",
    "Радомская губерния",
    "Седлецкая губерния",
    "Сувалкская губерния",
}

FINNISH_GUBERNIAS_1890 = {
    "Абоско-Бьёрнеборгская губерния",
    "Вазаская губерния",
    "Выборгская губерния",
    "Куопиоская губерния",
    "Нюландская губерния",
    "Санкт-Михельская губерния",
    "Тавастгусская губерния",
    "Улеаборгская губерния",
}

OBLASTS_1890 = {
    "Акмолинская область",
    "Амурская область",
    "Дагестанская область",
    "Забайкальская область",
    "Закаспийская область",
    "Карсская область",
    "Кубанская область",
    "Приморская область",
    "Самаркандская область",
    "Семипалатинская область",
    "Семиреченская область",
    "Сыр-Дарьинская область",
    "Терская область",
    "Тургайская область",
    "Уральская область",
    "Ферганская область",
    "Якутская область",
    "Область Войска Донского",
}

SPECIAL_ORIGIN_UNITS_1890 = {
    "Сухумский округ",
    "Сахалинский отдел",
    "Черноморский округ Кубанской области",
    "Батумский округ",
    "Артвинский округ",
    "Закатальский округ",
    "Великое княжество Финляндское",
    "Бухарский эмират",
    "Хивинское ханство",
}

SUPPLEMENTAL_ORIGIN_VALUES = {
    "Усть-Кара",
    "Царство Польское",
    "не помнит",
    "На Сахалине",
    "По пути",
    "Прусскоподданная",
    "Прусскоподданный",
    "из Чибисани",
    "Австрийский подданный",
    "Бродяга",
    "В пути следования",
    "На пути",
    "Прусско-подданный",
    "Румынское королевство",
    "Турецко-подданный",
}


def _origin_key(value: str) -> str:
    value = base_text(value).lower().replace("ё", "е")
    value = re.sub(r"\s*-\s*", "-", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    value = re.sub(r"\bгуб\.\b", "губерния", value)
    value = re.sub(r"\bобл\.\b", "область", value)
    return value


def _genitive_feminine_adjective(value: str) -> str:
    if value.endswith("ская"):
        return value[:-4] + "ской"
    if value.endswith("цкая"):
        return value[:-4] + "цкой"
    if value.endswith("ая"):
        return value[:-2] + "ой"
    return value


def _add_origin_variants(mapping: dict[str, str], canonical: str, *variants: str) -> None:
    for variant in variants:
        if variant:
            mapping[_origin_key(variant)] = canonical


def _build_origin_place_canonical_map() -> dict[str, str]:
    mapping: dict[str, str] = {}

    for unit in sorted(MAIN_GUBERNIAS_1890 | POLISH_GUBERNIAS_1890 | FINNISH_GUBERNIAS_1890):
        stem = unit.removesuffix(" губерния")
        genitive_stem = _genitive_feminine_adjective(stem)

        _add_origin_variants(
            mapping,
            unit,
            unit,
            stem,
            genitive_stem,
            f"{stem} губерния",
            f"{genitive_stem} губерния",
            f"{genitive_stem} губернии",
        )

    for unit in sorted(OBLASTS_1890):
        if unit == "Область Войска Донского":
            _add_origin_variants(
                mapping,
                unit,
                unit,
                "Область Войска Донского",
                "Области Войска Донского",
                "Донская",
                "Донской",
                "Донская область",
                "Донской области",
                "Донской область",
            )
            continue

        stem = unit.removesuffix(" область")
        genitive_stem = _genitive_feminine_adjective(stem)

        _add_origin_variants(
            mapping,
            unit,
            unit,
            stem,
            genitive_stem,
            f"{stem} область",
            f"{genitive_stem} область",
            f"{genitive_stem} области",
            f"{genitive_stem} обл.",
            f"{genitive_stem} обл",
        )

    # Special units and non-administrative source markers.
    for unit in SPECIAL_ORIGIN_UNITS_1890 | SUPPLEMENTAL_ORIGIN_VALUES:
        _add_origin_variants(mapping, unit, unit)


    # Tymovsky District: reviewed non-administrative origin/status markers.
    _add_origin_variants(mapping, "Румынское королевство", "Румынского королевства")
    _add_origin_variants(mapping, "Прусско-подданный", "Прусскоподданный", "Прусскоподданного", "Прусско-подданного")
    _add_origin_variants(mapping, "Турецко-подданный", "Турецко подданный", "Турецкоподданный", "Турецко-подданного")

    # Explicit historical/source spelling variants and duplicate spellings.
    _add_origin_variants(mapping, "Санкт-Петербургская губерния", "Петербургская", "Петербургской", "Петербургская губерния", "Петербургской губернии", "Петербугская", "Петербугской")
    _add_origin_variants(mapping, "Петроковская губерния", "Петраковская", "Петраковской", "Петраковская губерния", "Петраковской губернии")
    _add_origin_variants(mapping, "Подольская губерния", "Каменец-Подольская", "Каменец-Подольской", "Каменецк-Подольская", "Каменецк-Подольской", "Каменец - Подольская", "Каменец - Подольской", "Каменецк - Подольская", "Каменецк - Подольской")
    _add_origin_variants(mapping, "Астраханская губерния", "Астроханская", "Астроханской")
    _add_origin_variants(mapping, "Курляндская губерния", "Курлядская", "Курлядской", "Курляндского", "Митавская", "Митавской")
    _add_origin_variants(mapping, "Елисаветпольская губерния", "Елизаветпольская", "Елизаветпольской")
    _add_origin_variants(mapping, "Вологодская губерния", "Волгоградская", "Волгоградской")
    _add_origin_variants(mapping, "Полтавская губерния", "Полтавcкая", "Полтавcкой")

    _add_origin_variants(mapping, "Великое княжество Финляндское", "Финляндская", "Финляндской", "Финлядская", "Финлядской", "Великого княжества Финляндская", "Великого княжества Финляндской", "Великого княжества Финляндского", "Великое княжество Финляндское")


    _add_origin_variants(mapping, "Царство Польское", "Царство Польское", "Царства Польского", "Царства Польск", "Цар[ства] Польск[ого]", "Цар[ства] Польского", "Царства Польского")
    _add_origin_variants(mapping, "Усть-Кара", "Усть-Кара", "В Усть-Каре", "в Усть-Каре", "Усть-Каре")
    _add_origin_variants(mapping, "не помнит", "/Не помнит/", "Не помнит", "не помнит")

    return mapping


ORIGIN_PLACE_CANONICAL_MAP = _build_origin_place_canonical_map()

KNOWN_ORIGIN_PLACES = (
    MAIN_GUBERNIAS_1890
    | POLISH_GUBERNIAS_1890
    | FINNISH_GUBERNIAS_1890
    | OBLASTS_1890
    | SPECIAL_ORIGIN_UNITS_1890
    | SUPPLEMENTAL_ORIGIN_VALUES
)


ORIGIN_PLACE_OVERRIDES = {
    # OCR / over-expansion artifacts and source variants.
    "терская областьасти": "Терская область",
    "донская областьасти": "Область Войска Донского",
    "бессарабская область": "Бессарабская губерния",
    "бессарабской область": "Бессарабская губерния",
    "бессарабской области": "Бессарабская губерния",
    "каменецк-подольская": "Подольская губерния",
    "каменецк-подольской": "Подольская губерния",
    "курляндского": "Курляндская губерния",
}


# Values that look like occupations rather than places.
# If such a value appears in origin_place, preserve the source value and flag it for manual review.
# This is a soft QA signal because the book may contain misprints.
OCCUPATION_LIKE_VALUES = {
    "Бондарь",
    "Булочник",
    "Горшечник",
    "Землемер",
    "Кожевник",
    "Колбасник",
    "Колесник",
    "Кузнец",
    "Маляр",
    "Мясник",
    "Парикмахер",
    "Пастух",
    "Печник",
    "Пильщик",
    "Писарь",
    "Плотник",
    "Повар",
    "Портной",
    "Сапожник",
    "Слесарь",
    "Столяр",
    "Торговля",
    "Фельдшер",
}


def normalize_notes_raw(value: Any) -> str:
    """
    Normalize archive/source note references.

    Known archive prefixes in the source include:
    - РГБ № <number>
    - РГАЛИ № <number>

    PDF extraction may insert spaces inside the abbreviation:
    - РГ Б № 4568 -> РГБ № 4568
    - РГ АЛИ № 146 -> РГАЛИ № 146
    """
    value = clean_text(value, remove_trailing_footnotes=False)
    if not value:
        return ""

    value = re.sub(r"РГ\s*Б", "РГБ", value, flags=re.IGNORECASE)
    value = re.sub(r"РГ\s*АЛИ", "РГАЛИ", value, flags=re.IGNORECASE)
    value = re.sub(r"\s+", " ", value).strip().rstrip(".")

    match = re.search(r"\b(РГБ|РГАЛИ)\.?\s*№?\.?\s*(\d+)(?:\s*[-–—]?\s*([А-Яа-яA-Za-z]))?\b", value, flags=re.IGNORECASE)
    if match:
        archive = match.group(1).upper()
        suffix = match.group(3)
        if suffix:
            return f"{archive} № {match.group(2)}-{suffix.lower()}"
        return f"{archive} № {match.group(2)}"

    return value


def normalize_bool(value: Any) -> str:
    value = clean_text(value, remove_trailing_footnotes=True).lower().strip(". ")
    if not value:
        return ""

    value = value.replace("ё", "е")
    value = re.sub(r"\s+", " ", value).strip(". ")
    true_values = {"да", "yes", "true", "1"}
    false_values = {"нет", "no", "false", "0"}

    if value in true_values:
        return "TRUE"
    if value in false_values:
        return "FALSE"

    # Some parser/source anomalies attach comment markers or archive-number fragments
    # to field 12, e.g. `Нет. 14.?`, `Нет. 4`, `Нет.7 №`.
    # Preserve the yes/no meaning and leave the trailing fragment for manual/source notes.
    if re.match(r"^да(?:\b|[\s\.\d№?])", value):
        return "TRUE"
    if re.match(r"^нет(?:\b|[\s\.\d№?])", value):
        return "FALSE"

    return value


def normalize_literacy(value: Any) -> str:
    value = clean_text(value, remove_trailing_footnotes=True).lower().strip(". ")
    if not value:
        return ""

    value = value.replace("c", "с").replace("C", "С")
    value = value.replace("ё", "е")
    value = re.sub(r"\s+", " ", value).strip()

    if value in {"грамотен", "грамотная", "грамотный"}:
        return "грамотен"
    if value in {"неграмотен", "не грамотен", "неграмотная", "не грамотная", "неграмотный", "не грамотный"}:
        return "неграмотен"
    if value in {"образован", "образованная", "образованный"}:
        return "образован"

    return value


def normalize_marriage_status(value: Any) -> str:
    value = clean_text(value, remove_trailing_footnotes=True).lower().strip(". ")
    if not value:
        return ""

    value = value.replace("ё", "е")

    # Extended source values reviewed in Tymovsky district.
    value = value.replace("c", "с").replace("C", "С")
    value = re.sub(r"\s+", " ", value).strip()

    extended_map = {
        "на сахалине": "женат на Сахалине",
        "на сахалине, вдов": "женат на Сахалине. вдов",
        "на сахалине вдов": "женат на Сахалине. вдов",
        "на сахалине. вдов": "женат на Сахалине. вдов",
        "на сахалине. холост": "женат на Сахалине. холост",
        "на сахалине холост": "женат на Сахалине. холост",
        "на родине. холост": "женат на родине. холост",
        "на родине холост": "женат на родине. холост",
        "холост (?)": "холост",
        "вдов. одинок": "вдов. одинок",
        "холост. одинок": "холост. одинок",
        "женат на родине. одинок": "женат на родине. одинок",
        "женат на родине и на сахалине": "женат на родине и на сахалине",
        "женат на родине. жена на родине": "женат на родине. жена на родине",
        "женат в николаевске": "женат в николаевске",
        "женат во владивостоке": "женат во владивостоке",
        "женат на каре": "женат на каре",
        "девица": "девица",
    }
    if value in extended_map:
        return extended_map[value]


    if value in {"женат на родине", "женат не родине", "на родине"}:
        return "женат на родине"
    if value in {"женат на сахалине", "на сахалине"}:
        return "женат на Сахалине"
    if value in {"вдов", "вдова"}:
        return "вдов"
    if value in {"холост", "холоста"}:
        return "холост"

    return value



RELIGION_CANONICAL_VALUES = {
    "Армяно-григорианское",
    "Иудейское",
    "Католическое",
    "Лютеранское",
    "Магометанское",
    "Молоканское",
    "Мусульманское",
    "Православное",
    "Православное (выкрест)",
    "Раскольничество",
    "Римско-католическое",
    "Старообрядчество",
}


def _religion_key(value: str) -> str:
    value = base_text(value)
    # Normalize common mixed Latin/Cyrillic letters before lookup.
    # Example: Лютеранcкое, where `c` is Latin, should match Лютеранское.
    value = value.replace("c", "с").replace("C", "С")
    value = value.replace("ё", "е")
    value = value.lower()
    value = re.sub(r"^\d+\s+(?=[а-яё])", "", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value


def _build_religion_canonical_map() -> dict[str, str]:
    mapping: dict[str, str] = {}

    def add(canonical: str, *variants: str) -> None:
        mapping[_religion_key(canonical)] = canonical
        for variant in variants:
            mapping[_religion_key(variant)] = canonical

    add(
        "Армяно-григорианское",
        "Армяно-григорианского",
        "Армяно григорианское",
        "Армяно григорианского",
    )
    add("Иудейское", "Иудейского", "Иудейский")
    add("Католическое", "Католического", "Католический", "Католик", "Католической")
    add("Лютеранское", "Лютеранского", "Лютеранский", "Лютеранcкое", "Лютеранcкого")
    add("Магометанское", "Магометанского", "Магометанский", "Магометанской")
    add("Молоканское", "Молоканского", "Молоканин", "Молоканка")
    add("Мусульманское", "Мусульманского", "Мусульманский")
    add("Православное", "Православного", "Православный", "Православого", "Правослвного", "Православое", "Правослвное", "Православной", "Православная", "Православно й", "Прравославное", "Прравославного")
    add("Православное (выкрест)", "Православного (выкрест)", "Православное выкрест", "Православного выкрест")
    add("Раскольничество", "Раскольник", "Раскольника", "Раскольница", "Раскольницы", "Раскольническое", "Раскольнического")
    add("Римско-католическое", "Римско-католического", "Римско-католический", "Римско католическое", "Римско католического")
    add("Старообрядчество", "Старообрядец", "Старообрядца", "Старообрядка", "Старообрядки", "Старовер", "Староверка", "Староверческого", "Староверческое", "Старообрядческое", "Старообрядческого")

    return mapping


RELIGION_CANONICAL_MAP = _build_religion_canonical_map()


def normalize_religion(value: Any) -> str:
    """
    Religion is normalized as a confession label (`вероисповедание`), not as a person's adjective.

    Canonical adjective values use Russian neuter form:
    - '6. Православного' -> 'Православное'
    - '6. Католического' -> 'Католическое'
    - '6. Лютеранского' -> 'Лютеранское'

    Some source nouns are normalized to confession/community labels:
    - 'Раскольник' / 'Раскольница' -> 'Раскольничество'
    - 'Старовер' / 'Староверка' -> 'Старообрядчество'

    If the printed source contains a year-like value in religion, preserve it and let QA flag it.
    """
    value = clean_text(value, remove_trailing_footnotes=True).strip(". ")
    if not value:
        return ""

    value = value.replace("c", "с").replace("C", "С")
    value = value.replace("ё", "е")
    value = re.sub(r"^\d+\s+(?=[А-Яа-яЁё])", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"\s*-\s*", "-", value)

    key = _religion_key(value)
    if key in RELIGION_CANONICAL_MAP:
        return RELIGION_CANONICAL_MAP[key]

    # Generic fallback: genitive masculine/neuter adjective -> nominative neuter.
    # This covers rare variants while preserving known nouns through the explicit map above.
    lowered = value.lower()
    if lowered.endswith("ского"):
        return value[:-5] + "ское"
    if lowered.endswith("цкого"):
        return value[:-5] + "цкое"
    if lowered.endswith("ного"):
        return value[:-4] + "ное"
    if lowered.endswith("ого"):
        return value[:-3] + "ое"

    # Masculine adjective -> neuter adjective fallback.
    if lowered.endswith("ский"):
        return value[:-4] + "ское"
    if lowered.endswith("цкий"):
        return value[:-4] + "цкое"
    if lowered.endswith("ный"):
        return value[:-2] + "ое"

    return value


def normalize_origin_place(value: Any) -> str:
    """
    Origin place is normalized against the 1890 administrative-unit library.

    Main cleanup order:
    1. Remove source field prefix, e.g. '7.'
    2. Remove <crossed-out> text
    3. Restore [square-bracketed] parts
    4. Remove trailing footnote digits
    5. Normalize administrative abbreviations, e.g. 'обл.' -> 'область', 'губ.' -> 'губерния'
    6. Apply explicit overrides for known artifacts and historical variants
    7. Map to canonical 1890 administrative units when possible
    8. Preserve meaningful non-administrative values such as 'На Сахалине' and 'По пути'
    9. If unresolved, preserve cleaned source value and let QA report it for manual review
    """
    value = clean_text(value, remove_trailing_footnotes=True).strip(". ")
    if not value:
        return ""

    value = value.replace("ё", "е")
    # Fix mixed Latin/Cyrillic letters commonly produced during extraction or manual entry.
    value = value.replace("c", "с").replace("C", "С")
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"\s*-\s*", "-", value)

    # Normalize administrative abbreviations and inflected administrative nouns.
    # Use complete-word replacements only.
    value = re.sub(r"\bобл\.?\b", "область", value, flags=re.IGNORECASE)
    value = re.sub(r"\bобласти\b", "область", value, flags=re.IGNORECASE)
    value = re.sub(r"\bгуб\.?\b", "губерния", value, flags=re.IGNORECASE)
    value = re.sub(r"\bгубернии\b", "губерния", value, flags=re.IGNORECASE)

    # Fix over-expansion artifact: 'областьасти' -> 'область'
    value = re.sub(r"\bобластьасти\b", "область", value, flags=re.IGNORECASE)

    key = _origin_key(value)

    # Explicit artifact and duplicate-spelling overrides first.
    if key in ORIGIN_PLACE_OVERRIDES:
        return ORIGIN_PLACE_OVERRIDES[key]

    if key in ORIGIN_PLACE_CANONICAL_MAP:
        return ORIGIN_PLACE_CANONICAL_MAP[key]

    # As a fallback, convert adjectival genitive feminine to nominative feminine
    # and try the canonical map again.
    candidate = re.sub(r"\b([А-ЯЁA-Z][а-яёa-z-]*?)ской\b", r"\1ская", value)
    candidate = re.sub(r"\b([А-ЯЁA-Z][а-яёa-z-]*?)цкой\b", r"\1цкая", candidate)

    key = _origin_key(candidate)
    if key in ORIGIN_PLACE_OVERRIDES:
        return ORIGIN_PLACE_OVERRIDES[key]
    if key in ORIGIN_PLACE_CANONICAL_MAP:
        return ORIGIN_PLACE_CANONICAL_MAP[key]

    return candidate


def normalize_year(value: Any) -> str:
    """
    Normalize source year fields such as arrival_year.

    Important: do not use generic trailing-footnote cleanup here. A year may be
    the entire value (`1887`), so removing trailing digits would erase valid data.
    """
    value = base_text(value)
    if not value:
        return ""

    value = remove_source_field_prefix(value)
    value = normalize_source_markup(value)
    value = ignore_inline_special_symbols(value)
    value = re.sub(r"\s+", " ", value).strip(" .")

    match = re.search(r"\d{4}", value)
    if match:
        return match.group(0)

    # PDF text extraction sometimes inserts a space inside a year, e.g. `187 0`.
    compact_digits = re.sub(r"\D", "", value)
    match = re.search(r"1[5-9]\d{2}|20\d{2}", compact_digits)
    return match.group(0) if match else ""


def normalize_page_number(value: Any) -> str:
    value = base_text(value)
    if not value:
        return ""

    match = re.search(r"\d+", value)
    return str(int(match.group(0))) if match else value


def plural_months(n: int) -> str:
    if n % 10 == 1 and n % 100 != 11:
        return "месяц"
    if n % 10 in {2, 3, 4} and n % 100 not in {12, 13, 14}:
        return "месяца"
    return "месяцев"


def plural_years(n: int) -> str:
    if n % 10 == 1 and n % 100 != 11:
        return "год"
    if n % 10 in {2, 3, 4} and n % 100 not in {12, 13, 14}:
        return "года"
    return "лет"


def append_comment(existing: str, addition: str) -> str:
    existing = clean_preserve_comments(existing)
    addition = clean_preserve_comments(addition)

    if existing and addition:
        return f"{addition}; {existing}"
    if addition:
        return addition
    return existing



def split_age_with_embedded_religion(age_value: Any) -> tuple[Any, str]:
    """Split rare field-shift cases where source field 5 contains age plus religion.

    Example:
    - `5. 44. Раскольн[ица]. 7. Самарск[ой].`

    The source omitted explicit field `6.`. Keep `44` as age and pass
    `Раскольница` to religion normalization.
    """
    age_text = clean_text(age_value, remove_trailing_footnotes=False).strip(". ")
    if not age_text:
        return age_value, ""

    m = re.match(r"^(\d+)\.\s+(.+)$", age_text)
    if not m:
        return age_value, ""

    possible_religion = m.group(2).strip(". ")
    if re.search(r"Расколь|Православ|Катол|Лютер|Магомет|Мусульман|Молокан|Старовер|Иудей|Армяно", possible_religion, flags=re.IGNORECASE):
        return m.group(1), possible_religion

    return age_value, ""

def normalize_age_and_comments(age_value: Any, comments_value: Any) -> tuple[str, str]:
    age_text = clean_text(age_value, remove_trailing_footnotes=False).strip(". ")
    comments = clean_preserve_comments(comments_value)

    if not age_text:
        return "", comments

    lowered = age_text.lower().replace("ё", "е")
    year_match = re.search(r"(\d+)\s*(?:г|год|года|лет)\b", lowered)
    month_match = re.search(r"(\d+)\s*(?:м|мес|месяц|месяца|месяцев)\b", lowered)
    week_match = re.search(r"(\d+)\s*(?:нед|неделя|недели|недель)\b", lowered)
    day_match = re.search(r"(\d+)\s*(?:д|день|дня|дней|сутки|суток)\b", lowered)

    if month_match:
        months = int(month_match.group(1))
        years = int(year_match.group(1)) if year_match else 0

        if years:
            age_note = f"{years} {plural_years(years)} {months} {plural_months(months)}"
        else:
            age_note = f"{months} {plural_months(months)}"

        comments = append_comment(comments, age_note)
        return str(years), comments

    # Infants younger than one month/year may be written in weeks or days.
    # Store age as 0 years and preserve the precise value in comments.
    if week_match or day_match:
        comments = append_comment(comments, age_text)
        return "0", comments

    year_number = re.search(r"\d+", age_text)
    if year_number:
        return str(int(year_number.group(0))), comments

    return age_text, comments


def normalize_settlement_name(value: Any) -> str:
    value = clean_text(value, remove_trailing_footnotes=False)
    value = re.sub(r"\s+", " ", value).strip()

    special_names = {
        "пост александровский": "Пост Александровский",
        "александровский пост": "Пост Александровский",
        "арковский кордон": "Арковский кордон",
        "арковский станок": "Арковский станок",
        "пост дуэ": "Пост Дуэ",
        "дуэ пост": "Пост Дуэ",
        "пост корсаковский": "Пост Корсаковский",
        "корсаковский пост": "Пост Корсаковский",
        "тарайское зимовье": "Тарайское Зимовье",
    }

    lowered = value.lower().replace("ё", "е")
    if lowered in special_names:
        return special_names[lowered]

    value = re.sub(r"^Селение\s+", "", value, flags=re.IGNORECASE)
    return value.strip()


def normalize_household_number(value: Any) -> str:
    """
    Normalize the source household number from field `2.`.

    Important: do not remove trailing digits here. A household number may be
    the entire value, e.g. `26`, so generic trailing-footnote cleanup would
    incorrectly turn it into an empty string.
    """
    value = base_text(value)
    if not value:
        return ""

    value = remove_source_field_prefix(value)
    value = normalize_source_markup(value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value


def household_for_source_position_id(value: str) -> str:
    value = normalize_household_number(value)
    if not value:
        return ""

    if re.fullmatch(r"\d+", value):
        return str(int(value)).zfill(3)

    # For a normalized household range, use its first household number in the
    # third source-position segment (for example, 292-293 -> 292 and
    # 80-81 -> 080).
    range_match = re.fullmatch(r"(\d+)\s*-\s*\d+", value)
    if range_match:
        return str(int(range_match.group(1))).zfill(3)

    # Preserve non-numeric household identifiers, but make the ID safer.
    return re.sub(r"\s+", "_", value)


def transform_records_csv(
    input_csv_path: str | Path,
    output_csv_path: str | Path,
    *,
    default_settlement: str | None = None,
    global_person_start: int = 1,
) -> list[dict[str, str]]:
    """
    Transform a raw split-record CSV into the final flat CSV.

    The input CSV may contain either:
    - a `settlement` column for each row; or
    - one locality only, passed as default_settlement.

    Expected input columns are the source-derived fields:
    page_number, household_number, legal_status, name_raw, family_status, age,
    religion, origin_place, arrival_year, occupation, literacy, marriage_status,
    allowance_status, illness, comments, notes_raw.
    """
    input_csv_path = Path(input_csv_path)
    output_csv_path = Path(output_csv_path)

    with input_csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    settlement_counters: dict[str, int] = defaultdict(int)
    output_rows: list[dict[str, str]] = []

    for file_index, row in enumerate(rows, start=1):
        person_global_number = global_person_start + file_index - 1
        person_id = f"P{str(person_global_number).zfill(6)}"

        settlement_raw = row.get("settlement") or default_settlement
        if not settlement_raw:
            raise ValueError(f"Missing settlement in row {file_index}")

        settlement = normalize_settlement_name(settlement_raw)

        if settlement not in SETTLEMENTS:
            raise ValueError(f"Locality not found in SETTLEMENTS: {settlement!r}")

        meta = SETTLEMENTS[settlement]
        settlement_counters[settlement] += 1
        person_order = settlement_counters[settlement]

        household_number = normalize_household_number(row.get("household_number"))
        household_part = household_for_source_position_id(household_number)
        person_order_part = str(person_order).zfill(4)

        source_position_id = (
            f"{meta['district_code']}-"
            f"{meta['settlement_order']}-"
            f"{household_part}-"
            f"{person_order_part}"
        )

        age_input, embedded_religion = split_age_with_embedded_religion(row.get("age"))
        age, comments = normalize_age_and_comments(age_input, row.get("comments"))
        religion_input = row.get("religion") or embedded_religion

        out = {
            "person_id": person_id,
            "source_position_id": source_position_id,
            "district_code": meta["district_code"],
            "district": meta["district"],
            "settlement_order": meta["settlement_order"],
            "settlement": settlement,
            "person_order_in_settlement": str(person_order),
            "page_number": normalize_page_number(row.get("page_number")),
            "household_number": household_number,
            "legal_status": normalize_legal_status(row.get("legal_status")),
            "name_raw": clean_text(row.get("name_raw"), remove_trailing_footnotes=True),
            "family_status": normalize_family_status(row.get("family_status")),
            "age": age,
            "religion": normalize_religion(religion_input),
            "origin_place": normalize_origin_place(row.get("origin_place")),
            "arrival_year": normalize_year(row.get("arrival_year")),
            "occupation": clean_text(row.get("occupation"), remove_trailing_footnotes=True),
            "literacy": normalize_literacy(row.get("literacy")),
            "marriage_status": normalize_marriage_status(row.get("marriage_status")),
            "allowance_status": normalize_bool(row.get("allowance_status")),
            "illness": clean_text(row.get("illness"), remove_trailing_footnotes=True),
            "comments": comments,
            "notes_raw": normalize_notes_raw(row.get("notes_raw")),
        }

        output_rows.append(out)

    with output_csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FINAL_FIELD_ORDER)
        writer.writeheader()
        writer.writerows(output_rows)

    return output_rows


def extract_pdf_text_pages(pdf_path: str | Path, output_dir: str | Path) -> None:
    """
    Extract text page by page from a readable/searchable PDF.
    Requires: pip install pdfplumber

    This function creates one .txt file per PDF page.
    It does not perform person-record parsing.
    """
    import pdfplumber

    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with pdfplumber.open(pdf_path) as pdf:
        for pdf_page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
            text = normalize_pdf_artifacts(text)
            out_path = output_dir / f"pdf_page_{pdf_page_number:04}.txt"
            out_path.write_text(text, encoding="utf-8")


def is_year_like_value(value: str) -> bool:
    """Return True if a text value is a bare year-like number, e.g. '1882'."""
    value = base_text(value).strip(". ")
    return bool(re.fullmatch(r"1[5-9]\d{2}|20\d{2}", value))


def is_occupation_like_value(value: str) -> bool:
    """Return True if a value looks like an occupation rather than an origin place."""
    value = base_text(value).strip(". ")
    return value in OCCUPATION_LIKE_VALUES


def validate_output_csv(csv_path: str | Path) -> dict[str, Any]:
    """
    Run QA checks on the final CSV.
    Returns a report dictionary. Raises AssertionError only on structural failures; field-value issues are reported for manual review.
    """
    csv_path = Path(csv_path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    report: dict[str, Any] = {
        "row_count": len(rows),
        "unknown_origin_places": [],
        "unknown_legal_statuses": [],
        "unknown_family_statuses": [],
        "unknown_religions": [],
        "source_anomalies": [],
    }

    assert rows, "CSV is empty"

    person_ids = [r["person_id"] for r in rows]
    source_ids = [r["source_position_id"] for r in rows]

    assert len(person_ids) == len(set(person_ids)), "Duplicate person_id"
    assert len(source_ids) == len(set(source_ids)), "Duplicate source_position_id"

    allowed_literacy = {"", "неграмотен", "грамотен", "образован"}
    allowed_marriage = {'', 'женат на родине', 'женат на Сахалине', 'вдов', 'холост', 'вдов. одинок', 'девица', 'женат в николаевске', 'женат во владивостоке', 'женат на каре', 'женат на родине и на сахалине', 'женат на родине. жена на родине', 'женат на родине. одинок', 'холост. одинок', 'женат на родине. холост', 'женат на Сахалине. вдов', 'женат на Сахалине. холост'}
    allowed_allowance = {"", "TRUE", "FALSE"}

    for i, row in enumerate(rows, start=2):  # CSV line number, including header
        for field in FINAL_FIELD_ORDER:
            assert field in row, f"Missing field {field!r}"

        assert row["settlement"] in SETTLEMENTS, f"Unknown settlement at line {i}: {row['settlement']}"
        meta = SETTLEMENTS[row["settlement"]]
        assert row["district_code"] == meta["district_code"], f"Wrong district_code at line {i}"
        assert row["district"] == meta["district"], f"Wrong district at line {i}"
        assert row["settlement_order"] == meta["settlement_order"], f"Wrong settlement_order at line {i}"

        if row["page_number"]:
            assert re.fullmatch(r"\d+", row["page_number"]), f"Bad page_number at line {i}: {row['page_number']}"
        if row["age"]:
            if not re.fullmatch(r"\d+", row["age"]):
                report["source_anomalies"].append({
                    "person_id": row["person_id"],
                    "source_position_id": row["source_position_id"],
                    "page_number": row["page_number"],
                    "settlement": row["settlement"],
                    "name_raw": row["name_raw"],
                    "field": "age",
                    "value": row["age"],
                    "reason": "age is not a clean numeric value; review source field 5 or possible field-shift issue",
                })
            elif int(row["age"]) > 100:
                report["source_anomalies"].append({
                    "person_id": row["person_id"],
                    "source_position_id": row["source_position_id"],
                    "page_number": row["page_number"],
                    "settlement": row["settlement"],
                    "name_raw": row["name_raw"],
                    "field": "age",
                    "value": row["age"],
                    "reason": "age numeric value exceeds 100; review possible footnote digit attached to source field 5",
                })
        if row["arrival_year"]:
            if not re.fullmatch(r"\d{4}", row["arrival_year"]):
                report["source_anomalies"].append({
                    "person_id": row["person_id"],
                    "source_position_id": row["source_position_id"],
                    "page_number": row["page_number"],
                    "settlement": row["settlement"],
                    "name_raw": row["name_raw"],
                    "field": "arrival_year",
                    "value": row["arrival_year"],
                    "reason": "arrival_year is not a four-digit year; review source field 8 or possible field-shift issue",
                })
            elif not (1860 <= int(row["arrival_year"]) <= 1891):
                report["source_anomalies"].append({
                    "person_id": row["person_id"],
                    "source_position_id": row["source_position_id"],
                    "page_number": row["page_number"],
                    "settlement": row["settlement"],
                    "name_raw": row["name_raw"],
                    "field": "arrival_year",
                    "value": row["arrival_year"],
                    "reason": "arrival_year is outside expected range 1860-1891; review possible source typo or extraction error",
                })

        if row["literacy"] not in allowed_literacy:
            report["source_anomalies"].append({
                "person_id": row["person_id"],
                "source_position_id": row["source_position_id"],
                "page_number": row["page_number"],
                "settlement": row["settlement"],
                "name_raw": row["name_raw"],
                "field": "literacy",
                "value": row["literacy"],
                "reason": "literacy is not in the controlled vocabulary; review as possible source/category-code issue",
            })
        if row["marriage_status"] not in allowed_marriage:
            report["source_anomalies"].append({
                "person_id": row["person_id"],
                "source_position_id": row["source_position_id"],
                "page_number": row["page_number"],
                "settlement": row["settlement"],
                "name_raw": row["name_raw"],
                "field": "marriage_status",
                "value": row["marriage_status"],
                "reason": "marriage_status is not in the controlled vocabulary; review as possible source/category-code issue or new value",
            })
        if row["allowance_status"] not in allowed_allowance:
            report["source_anomalies"].append({
                "person_id": row["person_id"],
                "source_position_id": row["source_position_id"],
                "page_number": row["page_number"],
                "settlement": row["settlement"],
                "name_raw": row["name_raw"],
                "field": "allowance_status",
                "value": row["allowance_status"],
                "reason": "allowance_status is not TRUE/FALSE/blank; review source field 12 or possible field-shift issue",
            })

        # No remaining source markup in converted fields.
        for col in [
            "legal_status", "name_raw", "family_status", "religion", "origin_place",
            "occupation", "literacy", "marriage_status", "allowance_status",
            "illness", "comments", "notes_raw",
        ]:
            assert not re.search(r"<[^>]*>", row[col]), f"Angle markup remains at line {i}, {col}: {row[col]}"
            assert "[" not in row[col] and "]" not in row[col], f"Square bracket remains at line {i}, {col}: {row[col]}"

        # Trailing bare footnote digits are forbidden in these fields only.
        # comments and notes_raw are intentionally excluded.
        for col in TEXT_COLUMNS_FOR_TRAILING_FOOTNOTE_QA:
            # Preserve confirmed source anomalies where the printed religion field contains a year-like value.
            if col == "religion" and is_year_like_value(row[col]):
                continue
            # Reviewed Tymovsky family-status values can contain meaningful numbering.
            # Example: "Сожительница № 1" / "Сожительница № 2".
            if col == "family_status" and re.search(r"№\s*\d+$", row[col]):
                continue
            if re.search(r"\d+$", row[col]):
                report["source_anomalies"].append({
                    "person_id": row["person_id"],
                    "source_position_id": row["source_position_id"],
                    "page_number": row["page_number"],
                    "settlement": row["settlement"],
                    "name_raw": row["name_raw"],
                    "field": col,
                    "value": row[col],
                    "reason": "field ends with trailing digits; review possible footnote marker or meaningful source value",
                })

        # notes_raw should preserve archive numbers.
        if row["notes_raw"]:
            assert re.fullmatch(r"(?:РГБ|РГАЛИ) № \d+(?:-[А-Яа-яA-Za-z])?", row["notes_raw"]), f"Bad notes_raw at line {i}: {row['notes_raw']}"

        if row["legal_status"] and row["legal_status"] not in LEGAL_STATUS_CANONICAL_VALUES:
            report["source_anomalies"].append({
                "person_id": row["person_id"],
                "source_position_id": row["source_position_id"],
                "page_number": row["page_number"],
                "settlement": row["settlement"],
                "name_raw": row["name_raw"],
                "field": "legal_status",
                "value": row["legal_status"],
                "reason": "legal_status is not in the controlled vocabulary; review as possible typo or new value",
            })

        if row["family_status"] and row["family_status"] not in FAMILY_STATUS_CANONICAL_VALUES:
            report["source_anomalies"].append({
                "person_id": row["person_id"],
                "source_position_id": row["source_position_id"],
                "page_number": row["page_number"],
                "settlement": row["settlement"],
                "name_raw": row["name_raw"],
                "field": "family_status",
                "value": row["family_status"],
                "reason": "family_status is not in the controlled vocabulary; review as possible typo or new value",
            })

        # Religion should not retain source prefix or unnormalized source cases.
        # If the printed source contains a year-like value in religion, preserve it and flag softly.
        if row["religion"]:
            assert not re.match(r"^\s*6\.", row["religion"]), f"Field prefix remains in religion at line {i}"

            if is_year_like_value(row["religion"]):
                report["source_anomalies"].append({
                    "person_id": row["person_id"],
                    "source_position_id": row["source_position_id"],
                    "page_number": row["page_number"],
                    "settlement": row["settlement"],
                    "name_raw": row["name_raw"],
                    "field": "religion",
                    "value": row["religion"],
                    "reason": "religion field contains a year-like value; probable source misprint",
                })
            elif row["religion"] not in RELIGION_CANONICAL_VALUES:
                report["source_anomalies"].append({
                    "person_id": row["person_id"],
                    "source_position_id": row["source_position_id"],
                    "page_number": row["page_number"],
                    "settlement": row["settlement"],
                    "name_raw": row["name_raw"],
                    "field": "religion",
                    "value": row["religion"],
                    "reason": "religion is not in the controlled confession vocabulary; review as possible typo or new value",
                })

        if row["origin_place"] and is_occupation_like_value(row["origin_place"]):
            report["source_anomalies"].append({
                "person_id": row["person_id"],
                "source_position_id": row["source_position_id"],
                "page_number": row["page_number"],
                "settlement": row["settlement"],
                "name_raw": row["name_raw"],
                "field": "origin_place",
                "value": row["origin_place"],
                "reason": "origin_place field contains an occupation-like value; probable source misprint",
            })

    origin_values = {r["origin_place"].strip() for r in rows if r["origin_place"].strip()}
    unknown_origin_places = sorted(origin_values - KNOWN_ORIGIN_PLACES)
    report["unknown_origin_places"] = unknown_origin_places

    legal_status_values = {r["legal_status"].strip() for r in rows if r["legal_status"].strip()}
    unknown_legal_statuses = sorted(legal_status_values - LEGAL_STATUS_CANONICAL_VALUES)
    report["unknown_legal_statuses"] = unknown_legal_statuses

    family_status_values = {r["family_status"].strip() for r in rows if r["family_status"].strip()}
    unknown_family_statuses = sorted(family_status_values - FAMILY_STATUS_CANONICAL_VALUES)
    report["unknown_family_statuses"] = unknown_family_statuses

    religion_values = {
        r["religion"].strip()
        for r in rows
        if r["religion"].strip() and not is_year_like_value(r["religion"].strip())
    }
    unknown_religions = sorted(religion_values - RELIGION_CANONICAL_VALUES)
    report["unknown_religions"] = unknown_religions

    return report


# ---------------------------------------------------------------------------
# v12 project-level updates after full three-district manual review
# ---------------------------------------------------------------------------
# The values below are accepted after manual review of Alexandrovsky, Tymovsky,
# and Korsakovsky districts. They are intentionally broad: final cross-district
# grouping/normalization can be performed later without flagging reviewed source
# values as extraction errors at the district-clean-file stage.

PROJECT_REVIEWED_CANONICAL_VALUES = {
    "legal_status": [
        "Административно сосланный",
        "Административный ссыльный",
        "Врач",
        "Дворянин",
        "Дочь каторжного",
        "Дочь каторжной",
        "Дочь крестьянина",
        "Дочь крестьянина из ссыльных",
        "Дочь крестьянки",
        "Дочь крестьянки из ссыльных",
        "Дочь надворного советника",
        "Дочь отставного рядового",
        "Дочь подполковника",
        "Дочь поселенеца Тымовского округа",
        "Дочь поселенца",
        "Дочь поселенца. Дочь",
        "Дочь поселки",
        "Дочь рядового",
        "Дочь солдатки",
        "Дочь ссыльнокаторжного",
        "Дочь ссыльнокаторжной",
        "Жена врача",
        "Жена надворного советника дочь поселенца",
        "Жена подполковника",
        "Жена рядового",
        "Жена рядового Дуйской команды",
        "Жена свободного состояния",
        "Женщина свободного состояния",
        "Женщина свободного состояния. Жена",
        "Запасной рядовой",
        "Запасной унтер-офицер",
        "Запасный ефрейтор",
        "Запасный рядовой",
        "Запасный унтер-офицер",
        "Канцелярский служащий",
        "Капитан",
        "Крестьянин",
        "Крестьянин из крестьян",
        "Крестьянин из поселенцев",
        "Крестьянин из ссыльнопоселенцев",
        "Крестьянин из ссыльных",
        "Крестьянин свободного состояния",
        "Крестьянка",
        "Крестьянка из ссыльных",
        "Крестьянка свободного состояния",
        "Кузнец",
        "Мещанин",
        "Мещанин г. Николаевска",
        "Надворный советник",
        "Незаконнорожденная дочь поселки",
        "Отставной рядовой",
        "Отставной унтер-офицер",
        "Отставной фельдфебель",
        "Повивальная бабка",
        "Подполковник",
        "Подпоручик",
        "Поселенец",
        "Поселенец Александровского округа",
        "Поселенец Тымовского округа",
        "Поселенец временно уволенный",
        "Поселенец-богадельщик",
        "Поселенка",
        "Поселка",
        "Поселка (богадельщик)",
        "Поселка Тымовского округа",
        "Почетный гражданин административный ссыльный",
        "Рядовой",
        "Рядовой Дуйской команды",
        "Рядовой запаса",
        "Свободного состояния",
        "Свободного состояния Тымовского округа",
        "Свободного состояния жена",
        "Свободного состояния жена поселенца",
        "Свободного состояния мещанин",
        "Свободного состояния солдатка",
        "Совладелец",
        "Ссыльнокаторжная",
        "Ссыльнокаторжный",
        "Старший надзиратель",
        "Сын каторжного",
        "Сын каторжной",
        "Сын крестьянина",
        "Сын крестьянина из ссыльных",
        "Сын крестьянки",
        "Сын крестьянки из ссыльных",
        "Сын надворного советника",
        "Сын подполковника",
        "Сын поселенки",
        "Сын поселенца",
        "Сын поселки",
        "Сын поселки Тымовского округа",
        "Сын рядового",
        "Сын солдатки",
        "Сын ссыльнокаторжного",
        "Сын ссыльнокаторжной",
        "Уволенный в запас Армии Рядовой",
        "Унтер-офицер",
        "Фельдшер",
        "Штейгер"
    ],
    "family_status": [
        "1-я жена",
        "2-я жена",
        "Брат",
        "Брат совладельца",
        "Брат сожительницы",
        "Брат сожителя",
        "В работниках",
        "Внук",
        "Внучка",
        "Двоюродный брат",
        "Дочь",
        "Дочь Стрельцова",
        "Дочь жилицы",
        "Дочь жильца",
        "Дочь работника",
        "Дочь совладельца",
        "Дочь сожительницы",
        "Дочь сына. Внучка",
        "Дочь хозяина",
        "Жена",
        "Жена Ефима",
        "Жена Мухортова",
        "Жена Непомнящего",
        "Жена жильца",
        "Жена отца",
        "Жена работника",
        "Жена совладельца",
        "Жена сторожа",
        "Жена сына",
        "Жена хозяина",
        "Жилец",
        "Жилец. Совладелец",
        "Жилица",
        "Жилица. Сожительница Фисенко",
        "Зять",
        "Кухарка",
        "Мать",
        "Мать Жуковой",
        "Мать жильца",
        "Мать сожительницы",
        "Мать сожителя",
        "Муж",
        "Муж. хозяин",
        "На воспитании. Сын",
        "Невестка",
        "Незаконнорожденная дочь",
        "Незаконнорожденная дочь Вертушенковой",
        "Незаконнорожденная дочь Зайцевой",
        "Незаконнорожденная дочь Кирилкиной",
        "Незаконнорожденная дочь Марченковой",
        "Незаконнорожденная дочь Фединой",
        "Незаконнорожденная дочь жены",
        "Незаконнорожденная дочь жилицы",
        "Незаконнорожденная дочь совладелицы",
        "Незаконнорожденная дочь совладельца",
        "Незаконнорожденная дочь сожительницы",
        "Незаконнорожденная дочь хозяина",
        "Незаконнорожденный сын",
        "Незаконнорожденный сын Бондаренковой",
        "Незаконнорожденный сын Жуковой",
        "Незаконнорожденный сын Кирилкиной",
        "Незаконнорожденный сын Кириловой",
        "Незаконнорожденный сын Малафеевой",
        "Незаконнорожденный сын Митряевой",
        "Незаконнорожденный сын Шуликиной от Алексеева",
        "Незаконнорожденный сын Щетинина",
        "Незаконнорожденный сын Юдиной",
        "Незаконнорожденный сын Ягодкиной",
        "Незаконнорожденный сын жены",
        "Незаконнорожденный сын жилицы",
        "Незаконнорожденный сын жильца",
        "Незаконнорожденный сын совладелицы",
        "Незаконнорожденный сын совладельца",
        "Незаконнорожденный сын сожительницы",
        "Незаконнорожденный сын. Приемный",
        "Нянька",
        "Отец",
        "Падчерица",
        "Пасынок",
        "Пасынок жильца",
        "Повар аудитора",
        "Приемная дочь",
        "Приемная дочь жильца",
        "Приемный отец",
        "Приемный сын",
        "Приемыш жильца",
        "Приемыш незаконный внук",
        "Прислуга",
        "Работник",
        "Работница",
        "Свекровь сожительницы",
        "Сестра",
        "Сестра жены",
        "Служанка",
        "Совладелец",
        "Совладелица",
        "Сожитель",
        "Сожитель матери",
        "Сожитель хозяйки",
        "Сожитель хозяйки. Сожитель",
        "Сожительница",
        "Сожительница Афонина",
        "Сожительница Безпалова",
        "Сожительница Волошина",
        "Сожительница Ефимова",
        "Сожительница Зайцева",
        "Сожительница Запорожца",
        "Сожительница Звонкова",
        "Сожительница Знайдовского",
        "Сожительница Исакова",
        "Сожительница Каширина",
        "Сожительница Каштыкевича",
        "Сожительница Кондратьева",
        "Сожительница Коновалова",
        "Сожительница Корнеева Сожительница жильца",
        "Сожительница Ксенофонтова",
        "Сожительница Лангера",
        "Сожительница Лочь",
        "Сожительница Матвеева",
        "Сожительница Миллера",
        "Сожительница Митькина",
        "Сожительница Муромского",
        "Сожительница Наволочки",
        "Сожительница Петрова",
        "Сожительница Питерского",
        "Сожительница Родова",
        "Сожительница Семенова",
        "Сожительница Тамбовского",
        "Сожительница Тимофеева",
        "Сожительница Тихонова",
        "Сожительница Фельда",
        "Сожительница Щетинина. Сожительница",
        "Сожительница жильца",
        "Сожительница жильца Боутова",
        "Сожительница жильца Брегора",
        "Сожительница жильца Волкова",
        "Сожительница жильца Михайлова",
        "Сожительница жильца Фомина",
        "Сожительница и совладелица",
        "Сожительница надзирателя",
        "Сожительница совладельца",
        "Сожительница хозяина",
        "Сожительница хозяина сожительница",
        "Сожительница хозяина. Хозяйка",
        "Сожительница хозяйка",
        "Сожительница № 1",
        "Сожительница № 2",
        "Сторож",
        "Сын",
        "Сын Михеева",
        "Сын жилицы",
        "Сын жильца",
        "Сын каюра. Сын",
        "Сын крестьянина",
        "Сын писаря",
        "Сын работника",
        "Сын совладельца",
        "Сын сожительницы",
        "Сын хозяина",
        "Теща",
        "Хозяин",
        "Хозяин из киргиз",
        "Хозяин квартиры",
        "Хозяин квартиры №",
        "Хозяин-писарь",
        "Хозяйка",
        "Хозяйка. Жена",
        "Хозяйка. жена",
        "дочь",
        "жена",
        "жена Каспера Егорова",
        "жена писаря",
        "жилец",
        "жилица",
        "незаконнорожденная дочь",
        "незаконнорожденная дочь поселенца",
        "незаконнорожденная дочь сожительницы сына",
        "незаконнорожденный сын сожительницы Дубеля",
        "работник",
        "совладелец",
        "сожительница",
        "сожительница Дергачева",
        "сожительница жильца",
        "сожительница жильца Драпникова",
        "сожительница приемного сына",
        "сын",
        "сын жильца",
        "сын сожительницы",
        "хозяин"
    ],
    "religion": [
        "Армяно-григорианское",
        "Иудейское",
        "Католическое",
        "Лютеранское",
        "Магометанское",
        "Молоканское",
        "Мусульманское",
        "Православное",
        "Православное (выкрест)",
        "Раскольник",
        "Раскольничество",
        "Римско-католическое",
        "Старообрядчество"
    ],
    "origin_place": [
        "Абоско-Бьёрнеборгская губерния",
        "Австрийский подданный",
        "Акмолинская область",
        "Амурская область",
        "Архангельская губерния",
        "Астраханская губерния",
        "Бакинская губерния",
        "Бессарабская губерния",
        "Бродяга",
        "Бухарский эмират",
        "В пути следования",
        "Варшавская губерния",
        "Великое княжество Финляндское",
        "Виленская губерния",
        "Витебская губерния",
        "Владимирская губерния",
        "Вологодская губерния",
        "Волынская губерния",
        "Воронежская губерния",
        "Выборгская губерния",
        "Вятская губерния",
        "Гродненская губерния",
        "Дагестанская область",
        "Екатеринославская губерния",
        "Елисаветпольская губерния",
        "Енисейская губерния",
        "Забайкальская область",
        "Иркутская губерния",
        "Казанская губерния",
        "Калишская губерния",
        "Калужская губерния",
        "Келецкая губерния",
        "Киевская губерния",
        "Китай",
        "Ковенская губерния",
        "Костромская губерния",
        "Кубанская область",
        "Курляндская губерния",
        "Курская губерния",
        "Кутаисская губерния",
        "Лифляндская губерния",
        "Ломжинская губерния",
        "Люблинская губерния",
        "Минская губерния",
        "Могилёвская губерния",
        "Московская губерния",
        "На Сахалине",
        "На пути",
        "Нижегородская губерния",
        "Новгородская губерния",
        "Область Войска Донского",
        "Олонецкая губерния",
        "Оренбургская губерния",
        "Орловская губерния",
        "Пензенская губерния",
        "Пермская губерния",
        "Персидский подданный",
        "Петроковская губерния",
        "Плоцкая губерния",
        "По пути",
        "Подольская губерния",
        "Полтавская губерния",
        "Приморская область",
        "Прусско-подданный",
        "Прусскоподданная",
        "Прусскоподданный",
        "Прусскоподданый",
        "Псковская губерния",
        "Радомская губерния",
        "Румынское королевство",
        "Рязанская губерния",
        "Самаркандская область",
        "Самарская губерния",
        "Санкт-Петербургская губерния",
        "Санкт‑Петербургская губерния",
        "Саратовская губерния",
        "Седлецкая губерния",
        "Семипалатинская область",
        "Сибирь",
        "Симбирская губерния",
        "Смоленская губерния",
        "Ставропольская губерния",
        "Сувалкская губерния",
        "Сыр-Дарьинская область",
        "Таврическая губерния",
        "Тамбовская губерния",
        "Тверская губерния",
        "Терская область",
        "Тифлисская губерния",
        "Тобольская губерния",
        "Томская губерния",
        "Тульская губерния",
        "Турецко-подданный",
        "Усть-Кара",
        "Уфимская губерния",
        "Харьковская губерния",
        "Херсонская губерния",
        "Царство Польское",
        "Черниговская губерния",
        "Эриванская губерния",
        "Эстляндская губерния",
        "Якутская область",
        "Ярославская губерния",
        "из Чибисани",
        "не помнит",
        "по пути"
    ],
    "marriage_status": [
        "вдов",
        "вдов. одинок",
        "вдов. одинока",
        "девица",
        "женат в другом месте",
        "женат в николаевске",
        "женат во владивостоке",
        "женат на Сахалине",
        "женат на Сахалине. вдов",
        "женат на Сахалине. холост",
        "женат на каре",
        "женат на родине",
        "женат на родине и на Сахалине",
        "женат на родине и на сахалине",
        "женат на родине. одинок",
        "женат на родине. одинока",
        "женат на родине. одинокий",
        "женат на родине. холост",
        "одинок",
        "холост",
        "холост. одинок",
        "холост. одинока"
    ],
    "literacy": [
        "грамотен",
        "грамотен неграмотен",
        "неграмотен",
        "образован"
    ],
    "allowance_status": [
        "FALSE",
        "TRUE"
    ]
}

PROJECT_REVIEWED_VARIANT_MAPS = {
    "legal_status": {
        "Сынссыльнокаторжного": "Сын ссыльнокаторжного",
        "Дочьссыльнокаторжного": "Дочь ссыльнокаторжного",
        "Сынкаторжного": "Сын каторжного",
        "Дочь посел ки": "Дочь поселки",
        "Крестьнин из ссыльных": "Крестьянин из ссыльных",
        "Запасный рядовой": "Запасной рядовой",
        "Запасный унтер-офицер": "Запасной унтер-офицер",
        "Поселенка": "Поселенка",
        "Отставной рядовой": "Отставной рядовой"
    },
    "family_status": {
        "жена": "Жена",
        "сын": "Сын",
        "дочь": "Дочь",
        "хозяин": "Хозяин",
        "работник": "Работник",
        "сожительница": "Сожительница",
        "жилец": "Жилец",
        "жилица": "Жилица",
        "незаконнорожденная дочь": "Незаконнорожденная дочь",
        "незаконнорожденный сын": "Незаконнорожденный сын"
    },
    "religion": {
        "Католичка": "Католическое",
        "Катотолик": "Католическое",
        "Католик": "Католическое",
        "Армяногригорианское": "Армяно-григорианское",
        "Римскокатолическое": "Римско-католическое",
        "Старообрядцкой": "Старообрядчество",
        "Старообрядец": "Старообрядчество",
        "Старовер": "Старообрядчество",
        "Староверка": "Старообрядчество",
        "Мусульманин": "Мусульманское"
    },
    "origin_place": {
        "В Николаевске": "Приморская область",
        "В Хабаровке": "Приморская область",
        "В г. Хабаровке": "Приморская область",
        "В Софийске": "Приморская область",
        "Ташкент": "Сыр-Дарьинская область",
        "Бухара": "Бухарский эмират",
        "В Риге": "Лифляндская губерния",
        "В Сибири": "Сибирь",
        "Каменец Подольская": "Подольская губерния",
        "Каменец-Подольская": "Подольская губерния",
        "Каменец-Подольской": "Подольская губерния",
        "Санкт-Петербургская": "Санкт-Петербургская губерния",
        "Петербургская": "Санкт-Петербургская губерния",
        "Ставропольская": "Ставропольская губерния",
        "Смоленская": "Смоленская губерния",
        "Киевская": "Киевская губерния",
        "Нижегородская": "Нижегородская губерния",
        "Курская": "Курская губерния"
    },
    "marriage_status": {
        "женат на родине. пришла за мужем": "женат на родине",
        "женат на родине. пришел за женой": "женат на родине",
        "вдов. жена умерла на сахалине": "вдов",
        "холост. сожительствует с ссыльнокаторжной комаровой": "холост",
        "холост (?)": "холост",
        "на cахалине": "женат на Сахалине",
        "на сахалине": "женат на Сахалине"
    },
    "illness": {
        "Сифилисом": "Сифилис",
        "Бронх. катарр": "Бронхиальный катар",
        "Женская болезнь.": "Женская болезнь",
        "Псих": "Психическое расстройство"
    }
}

PROJECT_ALLOWED_LITERACY_VALUES = set(PROJECT_REVIEWED_CANONICAL_VALUES.get("literacy", [])) | {"", "неграмотен", "грамотен", "образован"}
PROJECT_ALLOWED_MARRIAGE_STATUS_VALUES = set(PROJECT_REVIEWED_CANONICAL_VALUES.get("marriage_status", [])) | {""}
PROJECT_ALLOWED_ALLOWANCE_STATUS_VALUES = set(PROJECT_REVIEWED_CANONICAL_VALUES.get("allowance_status", [])) | {"", "TRUE", "FALSE"}


def _project_key(value: Any) -> str:
    value = base_text(value).replace("ё", "е")
    value = value.replace("c", "с").replace("C", "С")
    value = value.lower()
    value = re.sub(r"[/?,()]+", " ", value)
    value = re.sub(r"\s*[-–—]\s*", "-", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value


def _register_project_reviewed_values() -> None:
    """Extend validation/normalization dictionaries with reviewed district values."""
    # Update accepted-value sets used by validation.
    LEGAL_STATUS_CANONICAL_VALUES.update(PROJECT_REVIEWED_CANONICAL_VALUES.get("legal_status", []))
    FAMILY_STATUS_CANONICAL_VALUES.update(PROJECT_REVIEWED_CANONICAL_VALUES.get("family_status", []))
    RELIGION_CANONICAL_VALUES.update(PROJECT_REVIEWED_CANONICAL_VALUES.get("religion", []))
    SUPPLEMENTAL_ORIGIN_VALUES.update(PROJECT_REVIEWED_CANONICAL_VALUES.get("origin_place", []))
    globals()["KNOWN_ORIGIN_PLACES"] = (
        MAIN_GUBERNIAS_1890
        | POLISH_GUBERNIAS_1890
        | FINNISH_GUBERNIAS_1890
        | OBLASTS_1890
        | SPECIAL_ORIGIN_UNITS_1890
        | SUPPLEMENTAL_ORIGIN_VALUES
    )

    # Update canonical maps used by normalization. Canonical self-maps allow
    # reviewed values to pass through without being treated as unknowns.
    for v in PROJECT_REVIEWED_CANONICAL_VALUES.get("legal_status", []):
        LEGAL_STATUS_CANONICAL_MAP[_legal_status_key(v)] = v
    for v in PROJECT_REVIEWED_CANONICAL_VALUES.get("family_status", []):
        FAMILY_STATUS_CANONICAL_MAP[_family_status_key(v)] = v
    for v in PROJECT_REVIEWED_CANONICAL_VALUES.get("religion", []):
        RELIGION_CANONICAL_MAP[_religion_key(v)] = v
    for v in PROJECT_REVIEWED_CANONICAL_VALUES.get("origin_place", []):
        ORIGIN_PLACE_CANONICAL_MAP[_origin_key(v)] = v

    # High-confidence reusable variants from manual review.
    for raw, canon in PROJECT_REVIEWED_VARIANT_MAPS.get("legal_status", {}).items():
        LEGAL_STATUS_CANONICAL_MAP[_legal_status_key(raw)] = canon
    for raw, canon in PROJECT_REVIEWED_VARIANT_MAPS.get("family_status", {}).items():
        FAMILY_STATUS_CANONICAL_MAP[_family_status_key(raw)] = canon
    for raw, canon in PROJECT_REVIEWED_VARIANT_MAPS.get("religion", {}).items():
        RELIGION_CANONICAL_MAP[_religion_key(raw)] = canon
    for raw, canon in PROJECT_REVIEWED_VARIANT_MAPS.get("origin_place", {}).items():
        ORIGIN_PLACE_CANONICAL_MAP[_origin_key(raw)] = canon


_register_project_reviewed_values()


_ORIGINAL_NORMALIZE_LEGAL_STATUS = normalize_legal_status
_ORIGINAL_NORMALIZE_FAMILY_STATUS = normalize_family_status
_ORIGINAL_NORMALIZE_RELIGION = normalize_religion
_ORIGINAL_NORMALIZE_ORIGIN_PLACE = normalize_origin_place
_ORIGINAL_NORMALIZE_MARRIAGE_STATUS = normalize_marriage_status
_ORIGINAL_VALIDATE_OUTPUT_CSV = validate_output_csv
_ORIGINAL_TRANSFORM_RECORDS_CSV = transform_records_csv


def _map_reviewed_variant(field: str, value: str) -> str:
    if not value:
        return ""
    maps = PROJECT_REVIEWED_VARIANT_MAPS.get(field, {})
    key = _project_key(value)
    for raw, canon in maps.items():
        if _project_key(raw) == key:
            return canon
    return value


def normalize_legal_status(value: Any) -> str:  # type: ignore[override]
    return _map_reviewed_variant("legal_status", _ORIGINAL_NORMALIZE_LEGAL_STATUS(value))


def normalize_family_status(value: Any) -> str:  # type: ignore[override]
    return _map_reviewed_variant("family_status", _ORIGINAL_NORMALIZE_FAMILY_STATUS(value))


def normalize_religion(value: Any) -> str:  # type: ignore[override]
    return _map_reviewed_variant("religion", _ORIGINAL_NORMALIZE_RELIGION(value))


def normalize_origin_place(value: Any) -> str:  # type: ignore[override]
    return _map_reviewed_variant("origin_place", _ORIGINAL_NORMALIZE_ORIGIN_PLACE(value))


def normalize_marriage_status(value: Any) -> str:  # type: ignore[override]
    return _map_reviewed_variant("marriage_status", _ORIGINAL_NORMALIZE_MARRIAGE_STATUS(value))


def append_comment(existing: Any, extra: Any) -> str:
    existing_s = clean_preserve_comments(existing).strip()
    extra_s = clean_preserve_comments(extra).strip()
    if not extra_s:
        return existing_s
    if not existing_s:
        return extra_s
    if extra_s.lower() in existing_s.lower():
        return existing_s
    return f"{existing_s}. {extra_s}"


def split_name_role_to_family_status(row: dict[str, str]) -> dict[str, str]:
    """Move trailing household role leakage from name_raw into family_status."""
    name = base_text(row.get("name_raw", ""))
    if not name:
        return row

    # Use reviewed roles, longest first, case-insensitive. Avoid extremely long
    # one-off roles that can overfit whole source notes.
    role_values = sorted(
        [v for v in FAMILY_STATUS_CANONICAL_VALUES if 2 <= len(v) <= 80],
        key=len,
        reverse=True,
    )
    name_key = _project_key(name)
    for role in role_values:
        role_key = _project_key(role)
        if not role_key:
            continue
        suffix = " " + role_key
        if name_key.endswith(suffix):
            # Remove the visible suffix by token length from the original string.
            parts = name.split()
            role_parts = role.split()
            if len(parts) <= len(role_parts):
                continue
            candidate_name = " ".join(parts[:-len(role_parts)]).strip(" .")
            if candidate_name:
                row["name_raw"] = candidate_name
                if not row.get("family_status"):
                    row["family_status"] = normalize_family_status(role)
                return row
    return row


def split_marriage_status_extras_to_comments(row: dict[str, str]) -> dict[str, str]:
    """Keep reviewed canonical marital phrase and move explanatory suffix to comments."""
    value = base_text(row.get("marriage_status", ""))
    if not value or "." not in value:
        return row
    lower = value.lower().replace("ё", "е")
    canonical_options = [
        "женат на родине", "женат на сахалине", "холост", "вдов", "одинок",
    ]
    for canonical_lower in canonical_options:
        if lower.startswith(canonical_lower + "."):
            extra = value[len(canonical_lower):].strip(" .")
            if canonical_lower == "женат на сахалине":
                row["marriage_status"] = "женат на Сахалине"
            else:
                row["marriage_status"] = canonical_lower
            row["comments"] = append_comment(row.get("comments", ""), extra)
            return row
    return row


def split_occupation_extras_to_comments(row: dict[str, str]) -> dict[str, str]:
    """Move descriptive suffixes from occupation to comments when source has 'Occupation. Note'."""
    value = base_text(row.get("occupation", ""))
    if not value or "." not in value:
        return row
    parts = [p.strip() for p in value.split(".") if p.strip()]
    if len(parts) < 2:
        return row
    # Conservative: only split when first part is short and occupational.
    if len(parts[0]) <= 40:
        row["occupation"] = parts[0]
        row["comments"] = append_comment(row.get("comments", ""), ". ".join(parts[1:]))
    return row


def normalize_row_postprocess(row: dict[str, str]) -> dict[str, str]:
    """Final row-level cleanup after field normalization."""
    row = dict(row)
    row = split_name_role_to_family_status(row)
    row = split_marriage_status_extras_to_comments(row)
    row = split_occupation_extras_to_comments(row)

    # Keep reviewed values as canonical, but normalize high-confidence variants.
    for field, func in [
        ("legal_status", normalize_legal_status),
        ("family_status", normalize_family_status),
        ("religion", normalize_religion),
        ("origin_place", normalize_origin_place),
        ("marriage_status", normalize_marriage_status),
    ]:
        row[field] = func(row.get(field, ""))

    row["settlement_order"] = str(row.get("settlement_order", "")).zfill(2) if row.get("settlement_order") else ""
    return row


def read_csv_dicts_auto(csv_path: str | Path) -> tuple[list[dict[str, str]], list[str], str]:
    """Read comma- or semicolon-delimited CSV with UTF-8/UTF-8-BOM support."""
    csv_path = Path(csv_path)
    text = csv_path.read_text(encoding="utf-8-sig")
    sample = text[:8192]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;")
        delimiter = dialect.delimiter
    except csv.Error:
        delimiter = ";" if sample.count(";") > sample.count(",") else ","
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = [{k: (v or "") for k, v in row.items()} for row in reader]
        fieldnames = reader.fieldnames or []
    return rows, fieldnames, delimiter


def write_project_csv(csv_path: str | Path, rows: list[dict[str, str]], fieldnames: list[str] | None = None) -> None:
    """Write project-standard CSV: UTF-8, comma-delimited, schema order when available."""
    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = FINAL_FIELD_ORDER if all(f in rows[0] for f in FINAL_FIELD_ORDER) else list(rows[0].keys()) if rows else FINAL_FIELD_ORDER
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def source_order_key(row: dict[str, str]) -> tuple[int, int, int]:
    def to_int(v: Any, default: int = 10**9) -> int:
        s = str(v or "").strip()
        return int(s) if re.fullmatch(r"\d+", s) else default
    return (
        to_int(row.get("district_code")),
        to_int(row.get("settlement_order")),
        to_int(row.get("person_order_in_settlement")),
    )


def standardize_clean_csv(input_csv_path: str | Path, output_csv_path: str | Path) -> list[dict[str, str]]:
    """Standardize a manually reviewed clean CSV for project use.

    - reads comma or semicolon delimiters;
    - accepts UTF-8 with or without BOM;
    - restores two-digit settlement_order;
    - applies conservative post-review cleanup;
    - sorts by district/settlement/person order;
    - writes comma-delimited UTF-8.
    """
    rows, fieldnames, _delimiter = read_csv_dicts_auto(input_csv_path)
    standardized = []
    for row in rows:
        fixed = {f: row.get(f, "") for f in FINAL_FIELD_ORDER}
        fixed = normalize_row_postprocess(fixed)
        standardized.append(fixed)
    standardized.sort(key=source_order_key)
    write_project_csv(output_csv_path, standardized, FINAL_FIELD_ORDER)
    return standardized


def transform_records_csv(  # type: ignore[override]
    input_csv_path: str | Path,
    output_csv_path: str | Path,
    *,
    default_settlement: str | None = None,
    global_person_start: int = 1,
) -> list[dict[str, str]]:
    """Transform raw records, then apply reviewed post-processing rules."""
    rows = _ORIGINAL_TRANSFORM_RECORDS_CSV(
        input_csv_path,
        output_csv_path,
        default_settlement=default_settlement,
        global_person_start=global_person_start,
    )
    processed = [normalize_row_postprocess(r) for r in rows]
    processed.sort(key=source_order_key)
    write_project_csv(output_csv_path, processed, FINAL_FIELD_ORDER)
    return processed


def validate_output_csv(csv_path: str | Path) -> dict[str, Any]:  # type: ignore[override]
    """Validate with full three-district reviewed canonical values accepted."""
    # Standard project CSVs are comma-delimited; for manually exported CSVs,
    # standardize to a temporary in-memory-compatible file first.
    rows, fieldnames, delimiter = read_csv_dicts_auto(csv_path)
    temp_path: Path | None = None
    path_for_validation = Path(csv_path)
    if delimiter != "," or any(str(r.get("settlement_order", "")).isdigit() and len(str(r.get("settlement_order", ""))) == 1 for r in rows):
        import tempfile
        tmp = tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv", encoding="utf-8", newline="")
        tmp.close()
        temp_path = Path(tmp.name)
        standardized = []
        for row in rows:
            fixed = {f: row.get(f, "") for f in FINAL_FIELD_ORDER}
            fixed = normalize_row_postprocess(fixed)
            standardized.append(fixed)
        standardized.sort(key=source_order_key)
        write_project_csv(temp_path, standardized, FINAL_FIELD_ORDER)
        path_for_validation = temp_path

    report = _ORIGINAL_VALIDATE_OUTPUT_CSV(path_for_validation)

    # Filter source-anomaly warnings for reviewed canonical values accepted after manual review.
    filtered = []
    for item in report.get("source_anomalies", []):
        field = item.get("field")
        value = item.get("value", "")
        if field == "literacy" and value in PROJECT_ALLOWED_LITERACY_VALUES:
            continue
        if field == "marriage_status" and value in PROJECT_ALLOWED_MARRIAGE_STATUS_VALUES:
            continue
        if field == "allowance_status" and value in PROJECT_ALLOWED_ALLOWANCE_STATUS_VALUES:
            continue
        if field == "legal_status" and value in LEGAL_STATUS_CANONICAL_VALUES:
            continue
        if field == "family_status" and value in FAMILY_STATUS_CANONICAL_VALUES:
            continue
        if field == "religion" and value in RELIGION_CANONICAL_VALUES:
            continue
        if field == "origin_place" and value in KNOWN_ORIGIN_PLACES:
            continue
        filtered.append(item)
    report["source_anomalies"] = filtered

    # Recompute unknown lists against reviewed sets.
    report["unknown_origin_places"] = sorted({r["origin_place"].strip() for r in rows if r.get("origin_place", "").strip()} - KNOWN_ORIGIN_PLACES)
    report["unknown_legal_statuses"] = sorted({r["legal_status"].strip() for r in rows if r.get("legal_status", "").strip()} - LEGAL_STATUS_CANONICAL_VALUES)
    report["unknown_family_statuses"] = sorted({r["family_status"].strip() for r in rows if r.get("family_status", "").strip()} - FAMILY_STATUS_CANONICAL_VALUES)
    report["unknown_religions"] = sorted({r["religion"].strip() for r in rows if r.get("religion", "").strip() and not is_year_like_value(r.get("religion", "").strip())} - RELIGION_CANONICAL_VALUES)

    if temp_path:
        try:
            temp_path.unlink()
        except OSError:
            pass
    return report
