# Source Note

## Source Description

This project is based on indexed person-level records from Anton Chekhov's 1890 Sakhalin census.

The source is a published PDF book with a readable/searchable text layer. The project does not use OCR as the primary extraction method. Text is extracted from the PDF text layer page by page, while preserving printed book page numbers for verification.

## Unit of Analysis

Individual person record.

## Geographic Scope

Sakhalin Island.

## Temporal Scope

1890.

## Expected Dataset Size

The expected final combined dataset contains approximately 7,445 person-level records.

## Source Structure

The source records are converted into a flat analytical CSV where one row represents one person.

The source contains numbered fields that are transformed into normalized analytical columns, including household number, legal/social status, name, family/household role, age, religion, origin place, arrival year, occupation, literacy, marriage status, allowance status, illness, comments, and archival notes.

## Page Number Rule

The `page_number` field preserves the printed book page where the person record begins.

The PDF viewer page number must not be used unless it matches the printed book pagination.

If a person record starts on one printed page and continues onto the next page, `page_number` should refer to the printed page where the record begins.

## Extraction Note

The extraction workflow removes running headers, repeated locality or district headings, printed page-number text, and general footnote comments from person-level fields.

The original source text is treated as historical evidence. The project preserves raw values where needed and creates normalized analytical fields separately.

## Data Access and Publication Note

The original PDF is not included in this repository until copyright, access, and ethical considerations are reviewed.

The public repository may include:

- source documentation;
- data dictionary;
- methodology;
- QA plan;
- Python extraction and cleaning scripts;
- aggregated outputs;
- dashboard screenshots;
- small sample records where appropriate.

The public repository should not include:

- the full raw PDF;
