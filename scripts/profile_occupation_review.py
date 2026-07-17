import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/staging/marriage_status_item16_20260716_v2/clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_staged.csv"
REVIEW = ROOT / "data/review/occupation_review_20260716"
QA = ROOT / "outputs/qa/occupation_review_20260716"

EXPLICIT_NONE = {"никакого", "ничего", "ничем"}
DEPENDENT = {"при муже", "при матери", "при отце"}


def family(value):
    s = value.casefold()
    if value == "" or s in EXPLICIT_NONE:
        return "No occupation recorded"
    if s in DEPENDENT:
        return "Dependent / supported by family"
    if s == "богадельщик":
        return "Non-occupational status / exceptional"
    if " и " in s:
        return "Compound occupations"
    groups = [
        ("Agriculture and animal husbandry", ("землед", "хлебопаш", "огород", "садов", "пастух", "покос", "сено", "коновал")),
        ("General and manual labor", ("чернораб", "рабоч", "работник", "работница", "в работниках", "дрово", "каменный уголь", "смольной яме", "моет полы")),
        ("Construction and building trades", ("плотник", "столяр", "печник", "каменщик", "штукатур", "маляр", "кровель", "кирпич", "стеколь", "обойщик")),
        ("Footwear and leather trades", ("сапож", "шорник", "кожев")),
        ("Metalworking and machinery", ("слесар", "кузнец", "механик", "токарь", "медник", "котель", "литей", "машинист", "штейгер", "смазчик")),
        ("Clothing and textile trades", ("портн", "шве", "прач", "ткач", "закрой", "красиль", "шляпоч")),
        ("Food production and service", ("хлебопек", "булочник", "кухар", "повар", "кондитер", "мясник", "колбас", "квас", "баня", "банщик", "мельник", "мельнице")),
        ("Fishing and hunting", ("рыбак", "рыбал", "рыболов", "шримс", "охотник")),
        ("Transport and animal transport", ("каюр", "кучер", "перевоз", "конюх", "катер", "возит хлеб")),
        ("Trade, clerical and communications", ("писарь", "контор", "приказчик", "торгов", "землемер", "телеграф", "печатник", "наборщик", "переплетчик", "рассыл", "раcсыл")),
        ("Administration and supervision", ("надзиратель", "смотритель", "сторож", "заведующий станцией", "фельдегерь")),
        ("Education, religion and medicine", ("учител", "фельдшер", "мулла", "псалом", "певч", "регент", "ветеринар")),
        ("Woodworking and manufactured crafts", ("пильщик", "бондар", "колесник", "тележник", "ложечник", "гребенщик", "щеточник", "инкрустац", "скульптор")),
        ("Specialized crafts and personal services", ("гравер", "золотых дел", "часовых дел", "цирюль", "парикмах", "горшеч", "гончар", "дегт", "дёг", "папирос", "щеточник")),
        ("Domestic service", ("служан", "прислугой")),
    ]
    for label, needles in groups:
        if any(n in s for n in needles):
            return label
    return "Other / requires classification"


def canonical_component(text):
    raw = text.strip()
    corrections = {
        "раcсыльный": "Рассыльный",
        "горшечник": "Гончар",
        "гонит деготь": "Дегтярь",
        "рыбак": "Рыболов",
        "рыбалка": "Рыболов",
        "дровонос": "Дровотаск",
    }
    lower = raw.casefold()
    if lower in corrections:
        return corrections[lower]
    return raw[:1].upper() + raw[1:] if raw else ""


def proposal(value):
    lower = value.casefold()
    if value == "":
        return "blank", "", "No", "Blank source value; do not infer an occupation"
    if lower in EXPLICIT_NONE:
        return "explicit_no_occupation", "Нет занятия", "Yes", "Explicitly states no occupation; approve shared analytical category"
    if lower in DEPENDENT:
        return "dependent_status", canonical_component(value), "Yes", "Support/dependency statement rather than a trade"
    if " и " in lower:
        components = [canonical_component(v) for v in re.split(r"\s+и\s+", value, flags=re.IGNORECASE)]
        return "compound", "; ".join(components), "Yes", "Two occupations; proposed semicolon-delimited analytical value"
    normalized = canonical_component(value)
    is_variant = normalized != value
    descriptive = any(marker in lower for marker in ("делает ", "носит ", "ловит ", "работает ", "варит ", "возит ", "был ", "на мельнице", "на катере", ":"))
    if descriptive:
        return "descriptive_or_qualified", normalized, "Yes", "Narrative or qualified occupation; review the analytical trade and preserve detail"
    if is_variant or value[:1].islower():
        return "case_spelling_or_synonym", normalized, "Yes", "Case, spelling, or close synonym proposed for consolidation"
    return "single_occupation", value, "No", "Single occupation value; retain pending vocabulary review"


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    REVIEW.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    grouped = defaultdict(list)
    for row in rows:
        grouped[row.get("occupation", "")].append(row)

    inventory, compounds, none_records = [], [], []
    group_record_counts = Counter()
    group_value_counts = Counter()
    type_record_counts = Counter()
    for value, matches in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        entry_type, norm, required, reason = proposal(value)
        fam = family(value)
        group_record_counts[fam] += len(matches)
        group_value_counts[fam] += 1
        type_record_counts[entry_type] += len(matches)
        pages = []
        for row in matches:
            page = row.get("page_number", "")
            if page and page not in pages:
                pages.append(page)
            if len(pages) == 5:
                break
        inventory.append({
            "occupation": value,
            "record_count": len(matches),
            "occupation_group": fam,
            "entry_type": entry_type,
            "occupation_norm_proposed": norm,
            "review_required": required,
            "review_reason": reason,
            "representative_person_ids": "; ".join(r.get("person_id", "") for r in matches[:5]),
            "representative_page_numbers": "; ".join(pages),
            "owner_decision": "",
            "owner_note": "",
        })
        if entry_type == "compound":
            for row in matches:
                compounds.append({
                    "person_id": row.get("person_id", ""),
                    "page_number": row.get("page_number", ""),
                    "occupation": value,
                    "occupation_norm_proposed": norm,
                    "comments": row.get("comments", ""),
                })
        if entry_type in {"blank", "explicit_no_occupation", "dependent_status"}:
            for row in matches:
                none_records.append({
                    "person_id": row.get("person_id", ""),
                    "page_number": row.get("page_number", ""),
                    "occupation": value,
                    "entry_type": entry_type,
                    "occupation_norm_proposed": norm,
                    "age": row.get("age", ""),
                    "sex": row.get("sex", ""),
                    "family_status_norm": row.get("family_status_norm", ""),
                    "comments": row.get("comments", ""),
                })

    group_summary = [
        {"occupation_group": g, "distinct_value_count": group_value_counts[g], "record_count": n}
        for g, n in sorted(group_record_counts.items(), key=lambda x: (-x[1], x[0]))
    ]
    write_csv(REVIEW / "occupation_value_inventory.csv", inventory, list(inventory[0]))
    write_csv(REVIEW / "occupation_group_summary.csv", group_summary, list(group_summary[0]))
    write_csv(REVIEW / "occupation_compound_values.csv", compounds, list(compounds[0]))
    write_csv(REVIEW / "occupation_no_occupation_records.csv", none_records, list(none_records[0]))
    no_occupation_values = [r for r in inventory if r["entry_type"] in {"blank", "explicit_no_occupation", "dependent_status"}]
    review_values = [r for r in inventory if r["review_required"] == "Yes"]
    write_csv(REVIEW / "occupation_no_occupation_values.csv", no_occupation_values, list(no_occupation_values[0]))
    write_csv(REVIEW / "occupation_values_requiring_review.csv", review_values, list(review_values[0]))
    qa = {
        "source": str(SOURCE.relative_to(ROOT)),
        "row_count": len(rows),
        "distinct_values_including_blank": len(grouped),
        "blank_records": len(grouped.get("", [])),
        "explicit_no_occupation_records": sum(len(grouped.get(v, [])) for v in ("Никакого", "Ничего", "Ничем")),
        "dependent_status_records": sum(len(grouped.get(v, [])) for v in ("При муже", "При матери", "При отце")),
        "compound_distinct_values": sum(r["entry_type"] == "compound" for r in inventory),
        "compound_records": len(compounds),
        "entry_type_record_counts": dict(sorted(type_record_counts.items())),
        "status": "review proposal only; no staged or canonical data modified",
    }
    (QA / "occupation_profile_qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
