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
    # Join ordinary hyphenated Cyrillic line breaks introduced by PDF text extraction,
    # e.g. `Негра-\nмотен` -> `Неграмотен`. Preserve true compounds
    # such as `Каменец-Подольской` when the next segment starts uppercase.
    text = re.sub(r'(?<=[А-Яа-яЁё])[-−]\s*\n\s*(?=[а-яё])', '', text)
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
        m = re.match(r'^\s*(\d{2,4})\s*$', line)
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
    m_note = re.search(r'((?:РГ\s*Б\.?|РГБ\.?|РГ\s*АЛИ\.?|РГАЛИ\.?)\s*(?:№\.?\s*)?\d+)', block_text, flags=re.I)
    notes_raw = ''
    if m_note:
        notes_raw = clean_cell(m_note.group(1))
        block_text = block_text[:m_note.start()]

    block_text = clean_cell(block_text)

    # Some records include field `1.` (settlement/locality correction) before the usual
    # household field `2.`. Field 1 is not part of the person-level output schema;
    # remove it so the regular field parser can start at `2.`. Example:
    #   1. <Дербинск> В[ерхний] Армудан. 2. <42> 18. 3. ...
    block_text = re.sub(r'^\s*1\.\s*.*?\.\s*(?=2\.)', '', block_text, count=1)

    raw_fields: dict[str, str] = {}

    # Field 2 is followed by household number, usually numeric but sometimes textual.
    # Some printed records omit/misprint the explicit `2.` label and begin as:
    #   3. 3. Поселенец. 4. Name ...
    #   7. 3. Сс[ыльно]каторжная. 4. Name ...
    # where the first number is the household number and the second `3.` is the legal-status field.
    m_household_then_3 = re.match(r'^\s*([^\.\s]+)\.\s*(3\.\s*(?=[A-Za-zА-Яа-яЁё<]).*)$', block_text)
    if m_household_then_3 and m_household_then_3.group(1) != '2':
        raw_fields['2'] = clean_field_value(m_household_then_3.group(1))
        parse_region = m_household_then_3.group(2)
    else:
        m2 = re.match(r'^\s*2\.\s*', block_text)
        if m2:
            rest_after_2 = block_text[m2.end():]
            # True field 3 starts before status text/markup, not before a numeric household number.
            m3_rel = re.search(r'(?<![0-9A-Za-zА-Яа-яЁё\]\)])3\.\s*(?=[A-Za-zА-Яа-яЁё<])', rest_after_2)
            if m3_rel:
                raw_fields['2'] = clean_field_value(rest_after_2[:m3_rel.start()])
                parse_region = block_text[m2.end() + m3_rel.start():]
            else:
                # Some records omit the explicit `3.` legal-status label:
                #   2. 11. Сын сс[ыльнокаторжной]. 4. Иван ...
                # Some omit both legal_status and the `3.` label:
                #   2. 27. 4. Захар Балаховский ...
                m_household = re.match(r'^\s*([^\.]+?)\.\s*', rest_after_2)
                if m_household:
                    raw_fields['2'] = clean_field_value(m_household.group(1))
                    rest_after_household = rest_after_2[m_household.end():]
                    m4_rel = re.search(r'(?<![0-9A-Za-zА-Яа-яЁё\]\)])4\.\s*(?=[A-Za-zА-Яа-яЁё<])', rest_after_household)
                    if m4_rel:
                        raw_fields['3'] = clean_field_value(rest_after_household[:m4_rel.start()])
                        parse_region = rest_after_household[m4_rel.start():]
                    else:
                        parse_region = rest_after_household
                else:
                    parse_region = block_text[m2.end():]
        else:
            parse_region = block_text

    def looks_like_field_label(match: re.Match[str]) -> bool:
        """Return True when a numeric source marker is likely a field label.

        This protects numeric field values from being interpreted as labels, for
        example `5. 10. 6. Прав...` where `10.` is an age value, not field 10.
        """
        fld = match.group(1)
        rest = parse_region[match.end():].lstrip()
        if not rest:
            return False

        first = rest[0]
        starts_text = bool(re.match(r'[A-Za-zА-Яа-яЁё<]', first))

        if fld in {'3', '4', '6', '7', '9', '10', '11', '12', '13'}:
            return starts_text
        if fld == '5':
            return bool(re.match(r'[0-9<(?]', first))
        if fld == '8':
            # Arrival year is normally a four-digit year. Some source anomalies are
            # partially crossed out, e.g. `8. 1 <8> 10. ...`; still treat `8.` as
            # a field boundary so the origin_place field does not swallow it.
            return bool(re.match(r'(?:1[5-9]\d{2}|20\d{2}|\d[\d\s<>\[\]]{0,8}|<)', rest))
        if fld == '14':
            return bool(re.match(r'[0-9А-Яа-яЁё<]', first))
        return False

    candidates = list(re.finditer(r'(?<![0-9A-Za-zА-Яа-яЁё\]\)])(3|4|5|6|7|8|9|10|11|12|13|14)\.\s*', parse_region))
    candidates = [m for m in candidates if looks_like_field_label(m)]

    # Keep labels in source order and ignore false positives that go backwards.
    filtered = []
    last_num = 2
    for m in candidates:
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

    # Repair rare source/category-code anomalies before mapping to columns.
    # Example: `3. Дочь поселенца. 5. Анна ... Дочь. 5. 4 месяца ...`
    # where the first `5.` is a misprinted field-4 label.
    if not raw_fields.get('4') and raw_fields.get('3'):
        v = raw_fields['3']
        m_bad_field4 = re.search(r'\.\s*5\.\s*(?=[A-Za-zА-Яа-яЁё<])', v)
        if m_bad_field4:
            raw_fields['3'] = clean_field_value(v[:m_bad_field4.start()])
            raw_fields['4'] = clean_field_value(v[m_bad_field4.end():])
        elif re.search(r'\.\s+', v):
            # Example: `3. Аграфена Балаховская. Незаконнорожденная дочь ...`
            # The source omitted legal_status and used field 3 for name/family.
            raw_fields['4'] = clean_field_value(v)
            raw_fields['3'] = ''

    # Repair source category-code shift where field `4.` is misprinted as `5.`
    # and the subsequent labels are shifted, e.g.:
    #   3. Поселенец. 5. Егор ... Хозяин. 6. 53. 7. Православного. 8. Орловской.
    if raw_fields.get('4') and not raw_fields.get('5'):
        m_bad_age = re.search(r'\.\s*6\.\s*(?=[0-9<(?])', raw_fields['4'])
        if m_bad_age:
            raw_fields['5'] = clean_field_value(raw_fields['4'][m_bad_age.end():])
            raw_fields['4'] = clean_field_value(raw_fields['4'][:m_bad_age.start()])

    if raw_fields.get('7') and not raw_fields.get('6'):
        m_bad_religion_origin = re.search(r'\.\s*8\.\s*(?=[A-Za-zА-Яа-яЁё<])', raw_fields['7'])
        if m_bad_religion_origin:
            raw_fields['6'] = clean_field_value(raw_fields['7'][:m_bad_religion_origin.start()])
            raw_fields['7'] = clean_field_value(raw_fields['7'][m_bad_religion_origin.end():])

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

    # Repair typo where arrival-year label `8.` is printed/extracted as another `7.`:
    #   7. Полтавск[ой]. 7. 1881. 9. Неграмотен. 10. Женат ... 11. Нет.
    if raw_fields.get('7') and not raw_fields.get('8'):
        m_bad_arrival = re.search(r'\.\s*7\.\s*((?:1[5-9]\d{2}|20\d{2}|\d{3}\s+\d))\b', raw_fields['7'])
        if m_bad_arrival:
            raw_fields['8'] = clean_field_value(m_bad_arrival.group(1))
            raw_fields['7'] = clean_field_value(raw_fields['7'][:m_bad_arrival.start()])

    # Repair rare source field-number shifts where marital status and allowance
    # are printed under neighboring field labels. Examples:
    #   10. Холост. 11. Нет.
    #   10. Холост. 12. Нет.
    #   10. Неграмотен. 11. Да.
    def source_value_key(v: str) -> str:
        v = clean_cell(v).lower().replace('ё', 'е').strip(' .')
        v = re.sub(r'<[^>]*>', ' ', v)
        v = v.replace('[', '').replace(']', '')
        v = re.sub(r'\s+', ' ', v).strip(' .')
        v = re.sub(r'\s*\d+$', '', v).strip(' .')
        return v

    marriage_like = {
        'холост', 'холоста', 'вдов', 'вдова',
        'женат на родине', 'женат не родине', 'женат на сахалине',
        'на родине', 'на сахалине',
    }
    literacy_like = {'грамотен', 'грамотная', 'грамотный', 'неграмотен', 'неграмотная', 'неграмотный', 'образован'}
    bool_like = {'да', 'нет'}

    v9 = source_value_key(raw_fields.get('9', ''))
    v10 = source_value_key(raw_fields.get('10', ''))
    v11 = source_value_key(raw_fields.get('11', ''))
    v12 = source_value_key(raw_fields.get('12', ''))

    if v9 in literacy_like and v10 in marriage_like and v11 in bool_like and not raw_fields.get('12'):
        raw_fields['12'] = raw_fields['11']
        raw_fields['11'] = raw_fields['10']
        raw_fields['10'] = raw_fields['9']
        raw_fields['9'] = ''
    elif v10 in marriage_like and v11 in bool_like and not raw_fields.get('12'):
        raw_fields['12'] = raw_fields['11']
        raw_fields['11'] = raw_fields['10']
        raw_fields['10'] = ''
    elif v10 in marriage_like and v12 in bool_like and not raw_fields.get('11'):
        raw_fields['11'] = raw_fields['10']
        raw_fields['10'] = ''
    elif v10 in literacy_like and v11 in bool_like and not raw_fields.get('12'):
        raw_fields['12'] = raw_fields['11']
        raw_fields['11'] = ''

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


class RecordStart:
    """Small match-like object used for robust record-start detection."""
    def __init__(self, start_pos: int, end_pos: int, record_number: str):
        self._start = start_pos
        self._end = end_pos
        self._record_number = record_number

    def start(self) -> int:
        return self._start

    def end(self) -> int:
        return self._end

    def group(self, idx: int = 0) -> str:
        if idx == 1:
            return self._record_number
        return self._record_number


def looks_like_record_body_start(text: str) -> bool:
    """Return True when text after a source record number begins like a person record.

    Valid starts include:
      - 2. <household>. 3. <legal_status> ...
      - 2. <household>. <legal_status>. 4. <name> ...  (rare missing `3.` label)
      - 2. <household>. 4. <name> ...                 (rare missing legal-status field)
      - <household>. 3. <legal_status>. 4. <name> ... (rare missing/misprinted `2.` label)
      - 3. <legal_status>. 4. <name> ...              (rare missing `2.` label)

    This deliberately rejects continuation lines such as:
      - 5. 2. 6. Правосл[авного] ...

    where `5.` is an age field label, not a source record number.
    """
    s = clean_cell(text)
    if not s:
        return False

    # Some records include field `1.` before the usual field `2.`.
    # Field 1 is a source locality/correction field and should not prevent
    # recognition of the person record start.
    s_for_match = re.sub(r'^\s*1\.\s*.*?\.\s*(?=2\.)', '', s, count=1)

    # Common normal case: field 2 + household + field 3.
    if re.match(r'^2\.\s*[^.]{1,40}\.\s*3\.\s*(?=[A-Za-zА-Яа-яЁё<])', s_for_match):
        return True

    # Missing field-3 label: field 2 + household + legal status text + field 4.
    if re.match(r'^2\.\s*[^.]{1,40}\.\s*[А-Яа-яЁё<][^\n]{1,160}?\.\s*4\.\s*(?=[A-Za-zА-Яа-яЁё<])', s):
        return True

    # Missing legal-status field and missing field-3 label: field 2 + household + field 4.
    if re.match(r'^2\.\s*[^.]{1,40}\.\s*4\.\s*(?=[A-Za-zА-Яа-яЁё<])', s_for_match):
        return True

    # Missing/misprinted field-2 label: household number + field 3 + legal status + field 4.
    if re.match(r'^\d{1,4}\.\s*3\.\s*[А-Яа-яЁё<][^\n]{1,160}?\.\s*4\.\s*(?=[A-Za-zА-Яа-яЁё<])', s):
        return True

    # Rare missing field-2 label: field 3 + legal status + field 4.
    if re.match(r'^3\.\s*[А-Яа-яЁё<][^\n]{1,160}?\.\s*4\.\s*(?=[A-Za-zА-Яа-яЁё<])', s):
        return True

    return False


def record_start_matches(text: str) -> list[RecordStart]:
    """
    Detect person-record starts robustly across all districts.

    Supported formats:
      88.\n2. 37. 3. ...
      104. 2. 41. 3. ...
      1153. 2. 256. 3. ...

    The detector validates the field sequence after the source record number,
    which prevents false splits on wrapped age lines such as:
      5. 2. 6. Правосл[авного] ...
    """
    starts: list[RecordStart] = []
    lines = list(re.finditer(r'(?m)^.*(?:\n|$)', text))
    previous_nonempty_line = ''

    for idx, line_match in enumerate(lines):
        line = line_match.group(0)
        line_no_newline = line.rstrip('\r\n')
        stripped = line_no_newline.strip()
        if not stripped:
            continue

        # Case 1: standalone source record number on one line; record body starts
        # on the next non-empty line.
        m_standalone = re.match(r'^(\d{1,5})\.\s*$', stripped)
        if m_standalone:
            next_nonempty = ''
            for nxt in lines[idx + 1:]:
                candidate = nxt.group(0).strip()
                if candidate:
                    next_nonempty = candidate
                    break
            if looks_like_record_body_start(next_nonempty):
                starts.append(RecordStart(
                    line_match.start(),
                    line_match.start() + line_no_newline.find(m_standalone.group(1)) + len(m_standalone.group(1)) + 1,
                    m_standalone.group(1),
                ))
            previous_nonempty_line = stripped
            continue

        # Case 2: inline source record number + record body on the same line.
        # Reject if the previous line was a standalone source record number,
        # because then this is the field-2 line belonging to that previous number.
        m_number = re.match(r'^(\d{1,5})\.\s+(.*)$', stripped)
        if m_number and not re.match(r'^\d{1,5}\.\s*$', previous_nonempty_line):
            body_after_number = m_number.group(2)
            if looks_like_record_body_start(body_after_number):
                offset = line_no_newline.find(m_number.group(0))
                starts.append(RecordStart(
                    line_match.start() + max(offset, 0),
                    line_match.start() + max(offset, 0) + len(m_number.group(1)) + 1,
                    m_number.group(1),
                ))

        previous_nonempty_line = stripped

    # Case 3: embedded source record numbers after an archival reference on the same line.
    # Seen in Alexandrovsky full-district validation, where source records such as
    # `... РГБ № 2009. 18. 2. 4. 2. 3. ...` were swallowed into the previous
    # block because the new source record number was not at line start.
    embedded_pattern = re.compile(
        r'(?:(?:РГ\s*Б|РГБ|РГ\s*АЛИ|РГАЛИ)\s*(?:№\.?\s*)?\d+[а-яА-Яa-zA-Z-]*\.?\s+)'
        r'(\d{1,5})\.\s+(?=(?:1\.\s*)?2\.)',
        flags=re.I,
    )
    for m in embedded_pattern.finditer(text):
        record_no = m.group(1)
        body_after_number = text[m.end(): m.end() + 260]
        if looks_like_record_body_start(body_after_number):
            starts.append(RecordStart(m.start(1), m.end(1) + 1, record_no))

    # Deduplicate and sort; prefer the earliest match for each start position.
    unique: dict[tuple[int, str], RecordStart] = {}
    for s in starts:
        unique[(s.start(), s.group(1))] = s
    starts = sorted(unique.values(), key=lambda s: s.start())

    return starts


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
    parser = argparse.ArgumentParser(description='Extract and parse Chekhov Sakhalin census PDF records. Generic district parser, v3.12.0.')
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
