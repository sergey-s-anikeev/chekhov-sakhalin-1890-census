from __future__ import annotations
import argparse, ast, csv, json, re
from collections import Counter
from pathlib import Path
from typing import Any

try:
    import fitz  # PyMuPDF
except ImportError as e:
    raise SystemExit("PyMuPDF is required: pip install pymupdf") from e


FIELD_COLUMNS = [
    'settlement','page_number','household_number','legal_status','name_raw','family_status','age',
    'religion','origin_place','arrival_year','occupation','literacy','marriage_status',
    'allowance_status','illness','comments','notes_raw'
]
OPTIONAL_DEBUG_COLUMNS = ['source_record_number','source_block_raw']

FIELD_MAP = {
    '2':'household_number',
    '3':'legal_status',
    '4':'name_family',
    '5':'age',
    '6':'religion',
    '7':'origin_place',
    '8':'arrival_year',
    '9':'occupation',
    '10':'literacy',
    '11':'marriage_status',
    '12':'allowance_status',
    '13':'illness',
    '14':'comments',
}


def load_settlements(helper_path: Path) -> dict[str, dict[str, Any]]:
    src = helper_path.read_text(encoding='utf-8')
    module = ast.parse(src)
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'SETTLEMENTS':
                    return ast.literal_eval(node.value)
    raise ValueError(f"Could not find SETTLEMENTS in {helper_path}")


def normalize_text_layer(text: str) -> str:
    text = text.replace('\u00a0', ' ')
    text = text.replace('\ufeff', '')
    text = text.replace('\ufffe', '')
    text = text.replace('\ufb02', 'fl').replace('\ufb01', 'fi')
    text = text.replace('\xad\n', '')
    text = text.replace('\xad', '')
    text = text.replace('­\n', '')
    text = text.replace('­', '')
    return text


def clean_cell(value: str) -> str:
    value = normalize_text_layer(value)
    value = value.replace('\t', ' ')
    value = re.sub(r'\s+', ' ', value)
    value = re.sub(r'\s+([.,;:?])', r'\1', value)
    return value.strip()


def clean_field_value(value: str) -> str:
    """Clean a parsed source field and remove trailing separator punctuation.

    Many field values are followed by a period before the next field label,
    for example `2. 256. 3.` or `5. 4 мес[яца]. 6.`.
    Removing only the final separator keeps internal punctuation such as
    `Name. Family status` intact.
    """
    value = clean_cell(value)
    return value.strip().rstrip(' .')


def heading_key(s: str) -> str:
    s = clean_cell(s).upper().replace('Ё', 'Е')
    s = re.sub(r'\s*[-–—]\s*', '-', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def build_heading_map(settlements: dict[str, dict[str, Any]]) -> dict[str, str]:
    heading_map: dict[str, str] = {}
    for settlement in settlements:
        if settlement.startswith('Пост '):
            heading_map[heading_key(settlement)] = settlement
            heading_map[heading_key(settlement.replace('Пост ', ''))] = settlement
        elif settlement in {'Арковский кордон', 'Арковский станок', 'Тарайское Зимовье'}:
            heading_map[heading_key(settlement)] = settlement
        else:
            heading_map[heading_key(settlement)] = settlement
            heading_map[heading_key('СЕЛЕНИЕ ' + settlement)] = settlement

    # Manual variants seen in the source text layer / PDF extraction.
    heading_map.update({
        heading_key('СЕЛЕНИЕ МАУКА'): 'Маука',
        heading_key('ПОСТ КОРСАКОВСКИЙ'): 'Пост Корсаковский',
        heading_key('СЕЛЕНИЕ ПОРО-АН-ТОМАРИ'): 'Поро-ан-Томари',
        heading_key('СЕЛЕНИЕ ПЕРВАЯ ПАДЬ'): 'Первая Падь',
        heading_key('СЕЛЕНИЕ ВТОРАЯ ПАДЬ'): 'Вторая Падь',
        heading_key('СЕЛЕНИЕ ТРЕТЬЯ ПАДЬ'): 'Третья Падь',
        heading_key('СЕЛЕНИЕ СОЛОВЬЕВКА'): 'Соловьевка',
        heading_key('СЕЛЕНИЕ ЛЮТОГА'): 'Лютога',
        heading_key('СЕЛЕНИЕ ГОЛЫЙ МЫС'): 'Голый Мыс',
        heading_key('СЕЛЕНИЕ МИЦУЛЬКА'): 'Мицулька',
        heading_key('СЕЛЕНИЕ ЛИСТВЕНИЧНОЕ'): 'Лиственичное',
        heading_key('СЕЛЕНИЕ ХОМУТОВКА'): 'Хомутовка',
        heading_key('СЕЛЕНИЕ БОЛЬШАЯ ЕЛАНЬ'): 'Большая Елань',
        heading_key('СЕЛЕНИЕ ВЛАДИМИРОВКА'): 'Владимировка',
    })
    return heading_map


def canonical_heading(line: str, heading_map: dict[str, str]) -> str | None:
    raw = clean_cell(line)
    if not raw:
        return None
    upper = raw.upper()

    # Ignore running headers and combined footer/header labels.
    if 'ОКРУГ' in upper and not upper.startswith(('СЕЛЕНИЕ', 'ПОСТ')):
        return None
    if '–' in raw or '—' in raw:
        return None

    k = heading_key(raw)
    if k in heading_map:
        return heading_map[k]

    # Try removing source heading prefixes and matching the core name.
    k2 = re.sub(r'^(СЕЛЕНИЕ|ПОСТ)\s+', '', k).strip()
    return heading_map.get(k2)


def extract_printed_page_number(text: str) -> str:
    for line in text.splitlines()[:7]:
        m = re.match(r'^\s*(\d{3,4})\s*$', line)
        if m:
            return m.group(1)
    return ''


def split_name_family(field4: str) -> tuple[str, str]:
    field4 = clean_cell(field4).strip(' .')
    if not field4:
        return '', ''
    parts = re.split(r'\.\s+', field4, maxsplit=1)
    if len(parts) == 1:
        return parts[0].strip(' .'), ''
    return parts[0].strip(' .'), parts[1].strip(' .')


def parse_fields(block_text: str) -> dict[str, str]:
    # Cut after archival number to avoid footnote paragraphs entering person fields.
    m_note = re.search(r'(РГ\s*Б\s*(?:№\s*)?\d+|РГБ\s*(?:№\s*)?\d+)', block_text, flags=re.I)
    notes_raw = ''
    if m_note:
        notes_raw = clean_cell(m_note.group(1))
        block_text = block_text[:m_note.start()]

    block_text = clean_cell(block_text)
    raw_fields: dict[str, str] = {}

    # Field 2 is followed by household number, usually numeric but sometimes textual.
    m2 = re.match(r'^\s*2\.\s*', block_text)
    if m2:
        rest_after_2 = block_text[m2.end():]
        # True field 3 starts before status text/markup, not before a numeric household number.
        m3_rel = re.search(r'(?<![0-9A-Za-zА-Яа-яЁё\]\)])3\.\s*(?=[А-Яа-яЁё<])', rest_after_2)
        if m3_rel:
            raw_fields['2'] = clean_field_value(rest_after_2[:m3_rel.start()])
            parse_region = block_text[m2.end() + m3_rel.start():]
        else:
            parse_region = block_text[m2.end():]
    else:
        parse_region = block_text

    matches = list(re.finditer(r'(?<![0-9A-Za-zА-Яа-яЁё\]\)])(3|4|5|6|7|8|9|10|11|12|13|14)\.\s*', parse_region))

    # Keep labels in source order and ignore false positives that go backwards.
    filtered = []
    last_num = 2
    for m in matches:
        num = int(m.group(1))
        if num > last_num:
            filtered.append(m)
            last_num = num
    matches = filtered

    for i, m in enumerate(matches):
        fld = m.group(1)
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(parse_region)
        raw_fields[fld] = clean_field_value(parse_region[start:end])

    # Some printed records omit the explicit `7.` origin-place label and place
    # the origin immediately after religion, e.g.:
    #   6. Прав[ославного]. На Сахал[ине]. 12. Нет.
    # Keep this as two source fields in the raw CSV so downstream normalization
    # remains consistent.
    if raw_fields.get('6') and not raw_fields.get('7'):
        religion_and_maybe_origin = raw_fields['6']
        parts = re.split(r'\.\s+', religion_and_maybe_origin, maxsplit=1)
        if len(parts) == 2 and parts[1].strip():
            raw_fields['6'] = clean_field_value(parts[0])
            raw_fields['7'] = clean_field_value(parts[1])

    row = {c: '' for c in FIELD_COLUMNS}
    for fld, col in FIELD_MAP.items():
        if col == 'name_family':
            name, family = split_name_family(raw_fields.get(fld, ''))
            row['name_raw'] = name
            row['family_status'] = family
        else:
            row[col] = raw_fields.get(fld, '')
    row['notes_raw'] = notes_raw
    return row


def extract_page_texts(pdf_path: Path, extracted_dir: Path) -> list[dict[str, Any]]:
    extracted_dir.mkdir(exist_ok=True, parents=True)
    pages = []
    doc = fitz.open(pdf_path)
    for pdf_index, page in enumerate(doc, start=1):
        text = normalize_text_layer(page.get_text('text') or '')
        printed = extract_printed_page_number(text)
        outname = f'pdf_page_{pdf_index:04}_book_page_{printed or "unknown"}.txt'
        (extracted_dir / outname).write_text(text, encoding='utf-8')
        pages.append({'pdf_page': pdf_index, 'book_page': printed, 'text': text, 'file': outname})
    return pages


def record_start_matches(text: str) -> list[re.Match[str]]:
    """
    Detect person-record starts robustly across all districts.

    Supported formats:
      88.\n2. 37. 3. ...
      104. 2. 41. 3. ...
      1153. 2. 256. 3. ...

    The lookahead requires field `2.` immediately after the source record number
    or on the next line. This prevents matching internal source fields such as
    `5.`, `6.`, `10.`, or values inside a person record.
    """
    return list(re.finditer(r'(?m)^\s*(\d{1,5})\.\s*(?=(?:2\.|\n\s*2\.))', text))


def parse_records(pages: list[dict[str, Any]], heading_map: dict[str, str]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    current_settlement: str | None = None

    for page in pages:
        text = page['text']
        rec_starts = record_start_matches(text)

        events: list[tuple[str, int, str, int | None]] = []
        for line_m in re.finditer(r'(?m)^.*$', text):
            heading = canonical_heading(line_m.group(0), heading_map)
            if heading:
                events.append(('heading', line_m.start(), heading, None))

        for idx, m in enumerate(rec_starts):
            events.append(('record', m.start(), m.group(1), idx))

        events.sort(key=lambda x: x[1])
        first_heading_on_page = next((e[2] for e in events if e[0] == 'heading'), None)

        for event_type, _pos, value, idx in events:
            if event_type == 'heading':
                current_settlement = value
                continue

            assert idx is not None
            record_no = value
            start = rec_starts[idx].end()
            end = rec_starts[idx + 1].start() if idx + 1 < len(rec_starts) else len(text)
            block = text[start:end]
            parsed = parse_fields(block)
            settlement = current_settlement or first_heading_on_page or ''
            parsed['settlement'] = settlement
            parsed['page_number'] = page['book_page']
            parsed['source_record_number'] = record_no
            parsed['source_block_raw'] = clean_cell(block)

            if parsed.get('household_number') or parsed.get('name_raw') or parsed.get('notes_raw'):
                records.append(parsed)

    return records


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(exist_ok=True, parents=True)
    cols = FIELD_COLUMNS + OPTIONAL_DEBUG_COLUMNS
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows)



def record_sequence_summary(records: list[dict[str, str]]) -> dict[str, Any]:
    """
    Summarize parsed source record numbers and detect gaps.

    Source record numbers are useful QA signals because large gaps usually mean
    that the record-start parser missed a page layout variant. The check is not
    treated as a hard error because separately uploaded district PDFs may start
    mid-sequence or contain source numbering anomalies.
    """
    nums: list[int] = []
    by_settlement: dict[str, list[int]] = {}

    for row in records:
        raw = str(row.get('source_record_number', '')).strip()
        if not raw.isdigit():
            continue
        n = int(raw)
        nums.append(n)
        by_settlement.setdefault(row.get('settlement', ''), []).append(n)

    def summarize_number_list(values: list[int]) -> dict[str, Any]:
        if not values:
            return {'count': 0, 'min': None, 'max': None, 'missing_ranges': []}
        uniq = sorted(set(values))
        missing = []
        expected = set(range(uniq[0], uniq[-1] + 1))
        missing_nums = sorted(expected - set(uniq))
        if missing_nums:
            start = prev = missing_nums[0]
            for x in missing_nums[1:]:
                if x == prev + 1:
                    prev = x
                else:
                    missing.append([start, prev])
                    start = prev = x
            missing.append([start, prev])
        return {
            'count': len(values),
            'unique_count': len(uniq),
            'min': uniq[0],
            'max': uniq[-1],
            'missing_ranges': missing,
        }

    return {
        'overall': summarize_number_list(nums),
        'by_settlement': {k: summarize_number_list(v) for k, v in by_settlement.items()},
    }


def complete_settlement_sample(records: list[dict[str, str]], min_rows: int = 500) -> list[dict[str, str]]:
    """Return a sample with at least min_rows, never cutting through a settlement."""
    if len(records) <= min_rows:
        return records
    rows: list[dict[str, str]] = []
    for row in records:
        rows.append(row)
        if len(rows) >= min_rows:
            current_settlement = row.get('settlement', '')
            # Continue until the settlement changes; then stop before adding next settlement.
            # This is handled by the next loop iteration check.
            continue
        
    # Simpler deterministic implementation: find settlement boundary after min_rows.
    cutoff = min_rows
    last_settlement = records[cutoff - 1].get('settlement', '')
    while cutoff < len(records) and records[cutoff].get('settlement', '') == last_settlement:
        cutoff += 1
    return records[:cutoff]


def main() -> None:
    parser = argparse.ArgumentParser(description='Extract and parse Chekhov Sakhalin census PDF records. Generic district parser, v3.')
    parser.add_argument('--pdf', required=True, help='Path to source PDF.')
    parser.add_argument('--helper', required=True, help='Path to helper script containing SETTLEMENTS.')
    parser.add_argument('--out-dir', default='chekhov_pipeline_v2', help='Output directory.')
    parser.add_argument('--sample-min-rows', type=int, default=500, help='Minimum sample rows; sample will not cut a settlement.')
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    helper_path = Path(args.helper)
    out_dir = Path(args.out_dir)
    extracted_dir = out_dir / 'extracted_pages'
    data_dir = out_dir / 'data_sample'
    out_dir.mkdir(parents=True, exist_ok=True)

    settlements = load_settlements(helper_path)
    heading_map = build_heading_map(settlements)
    pages = extract_page_texts(pdf_path, extracted_dir)
    records = parse_records(pages, heading_map)
    sample = complete_settlement_sample(records, args.sample_min_rows)

    all_csv = data_dir / 'raw_extracted_records_all_from_uploaded_pdf_v3.csv'
    sample_csv = data_dir / 'raw_extracted_sample_min500_complete_settlements_v3.csv'
    write_csv(all_csv, records)
    write_csv(sample_csv, sample)

    summary = {
        'pdf_path': str(pdf_path),
        'pdf_pages': len(pages),
        'book_page_start': pages[0]['book_page'] if pages else None,
        'book_page_end': pages[-1]['book_page'] if pages else None,
        'records_parsed_total': len(records),
        'records_in_complete_settlement_sample': len(sample),
        'sample_min_rows_requested': args.sample_min_rows,
        'settlement_counts': dict(Counter(r['settlement'] for r in records)),
        'sample_settlement_counts': dict(Counter(r['settlement'] for r in sample)),
        'source_record_number_sequence': record_sequence_summary(records),
        'extracted_text_dir': str(extracted_dir),
        'all_records_csv': str(all_csv),
        'sample_csv': str(sample_csv),
    }
    (out_dir / 'extraction_summary_v3.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
