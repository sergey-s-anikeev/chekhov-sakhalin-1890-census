# chekhov-sakhalin-1890-census
Historical data analysis project based on Anton Chekhov’s 1890 Sakhalin census records. The project transforms indexed PDF records into a structured person-level dataset and explores population structure, settlement geography, legal status, age, gender, and migration origins using Python, SQL, and Tableau.

## Current Project Status

The project has moved from planning to the data extraction and normalization design phase.

Completed so far:

- Statement of Work created.
- Repository structure created.
- Source documentation started.
- Data dictionary completed.
- Final flat CSV schema designed.
- Locality metadata structure created.
- Controlled vocabularies started for legal status, family status, religion, and origin place.
- Python helper script drafted for cleaning, normalization, transformation, and QA.
- Initial extraction tests started on the searchable PDF text layer.

Current phase:

- Testing extraction from the PDF text layer.
- Creating raw person-record samples.
- Converting raw split records into the final flat CSV structure.
- Running QA checks before scaling to the full dataset.

Next milestone:

- Produce a validated sample CSV of 300–500 person records.
- Document extraction errors and manual-review cases.
- Finalize the first version of the cleaning workflow.

## Project Documentation

- [Statement of Work](docs/SOW.md)
- [Source Note](docs/source_note.md)
- [Data Dictionary](docs/data_dictionary.md)
- [Methodology](docs/methodology.md)
- [Limitations](docs/limitations.md)
- [QA Plan](docs/qa_plan.md)

## Repository Structure

```text
chekhov-sakhalin-1890-census/
  README.md
  data/
    .gitkeep
  docs/
    SOW.md
    source_note.md
    data_dictionary.md
    methodology.md
    limitations.md
    qa_plan.md
  notebooks/
    .gitkeep
  outputs/
    .gitkeep
  scripts/
    sakhalin_conversion_helpers_v11.py
  sql/
    .gitkeep
  tableau/
    .gitkeep
```

## Data Publication Note

The original PDF and full person-level dataset are not included in this repository until copyright, access, and ethical considerations are reviewed.

The repository may include documentation, code, QA rules, aggregated outputs, dashboard screenshots, and small sample records where appropriate.
