# Statement of Work  
## Project: Chekhov Sakhalin 1890 Census Data Analysis

## 1. Project Overview

This project aims to transform indexed historical census records from Anton Chekhov’s 1890 Sakhalin census into a structured analytical dataset. The final output will include a cleaned sample or full person-level dataset, exploratory analysis, SQL queries, and visualizations showing population structure, settlement geography, legal/social status, age, gender, and migration origins where available.

The project is designed as a portfolio case for a Junior Data Analyst role, demonstrating skills in data extraction, data cleaning, documentation, SQL analysis, Python-based exploratory analysis, and Tableau visualization.

## 2. Project Objectives

The main objectives are:

- Extract structured data from a historical PDF source.
- Create a clean person-level dataset from indexed census records.
- Develop a data dictionary and source documentation.
- Analyze demographic and social patterns in the 1890 Sakhalin population.
- Build SQL queries to answer key analytical questions.
- Create visualizations and, if feasible, a Tableau dashboard.
- Document the methodology, limitations, and reproducibility of the project.

## 3. Scope of Work

### In Scope

The project will include:

- Reviewing the PDF source structure.
- Extracting a sample of approximately 300–500 records for the initial MVP.
- Cleaning and standardizing key variables.
- Creating a data dictionary.
- Creating a reproducible Python workflow for extraction and cleaning.
- Creating SQL queries for analysis.
- Conducting exploratory data analysis.
- Creating charts and/or maps.
- Preparing GitHub documentation in English.
- Creating a final project README with findings, limitations, and next steps.

### Out of Scope

The project will not initially include:

- Full historical interpretation of Chekhov’s work.
- Complete academic reconstruction of Sakhalin society in 1890.
- Predictive modeling.
- Perfect geocoding of all historical settlements in the first project phase.

## 4. Key Research Questions

The project will explore the following questions:

1. What was the age and gender structure of the recorded Sakhalin population in 1890?
2. How was the population distributed across settlements?
3. What legal or social status categories are visible in the census records?
4. How did population structure differ between settlements?
5. Which regions contributed to Sakhalin’s recorded population?
6. What data quality issues arise when transforming historical PDF records into structured data?

## 5. Data Sources

Primary source:

- Indexed PDF book containing person-level records from Anton Chekhov’s 1890 Sakhalin census:
- English Title: "Perhaps my figures, too, will be of use." Materials of A.P. Chekhov's Sakhalin Census. 1890. Yuzhno-Sakhalinsk: "Rubezh" Publishing House, 2005. – 600 p.
- Russian Title: «Быть может, пригодятся и мои цифры». Материалы Сахалинской переписи А.П. Чехова. 1890 год. Южно-Сахалинск: Издательство «Рубеж», 2005. – 600 с.

Possible supplementary sources:

- Historical maps of Sakhalin.
- Modern geographic coordinates for settlements where identifiable.
- Secondary historical literature for source context.
- Geographic data for modern reference mapping, if appropriate.

## 6. Tools and Technologies

The project will use:

- **Python** for extraction, cleaning, and exploratory analysis.
- **pandas** for tabular data processing.
- **pdfplumber / OCR tools** if needed for PDF extraction.
- **SQL** for structured querying and aggregation.
- **SQLite or PostgreSQL** for database storage.
- **Tableau** for dashboard creation.
- **GitHub** for project documentation and version control.
- **Markdown** for README, source notes, and data dictionary.

## 7. Deliverables

The final project should include:

1. **GitHub Repository**
   - Clean folder structure.
   - README file.
   - Source note.
   - Data dictionary.
   - Methodology notes.

2. **Data Extraction Sample**
   - Raw extracted sample.
   - Cleaned analytical sample.
   - Documentation of extraction quality.

3. **Python Notebooks**
   - PDF extraction quality check.
   - Data cleaning workflow.
   - Exploratory data analysis.

4. **SQL Files**
   - Queries for population counts.
   - Queries by settlement, age, gender, legal status, and origin.
   - Aggregation queries for visualization.

5. **Visual Outputs**
   - Charts showing demographic structure.
   - Settlement-level summaries.
   - Optional map of settlements or origins.
   - Optional Tableau dashboard.

6. **Final Analytical Summary**
   - Key findings.
   - Data limitations.
   - Next steps.

## 8. Proposed Repository Structure

```text
chekhov-sakhalin-1890-census/
  README.md
  docs/
    SOW.md
    source_note.md
    data_dictionary.md
    methodology.md
    limitations.md
  data/
    raw/
    sample/
    processed/
  notebooks/
    01_pdf_extraction_quality_check.ipynb
    02_data_cleaning.ipynb
    03_exploratory_analysis.ipynb
  sql/
    01_create_tables.sql
    02_analysis_queries.sql
  tableau/
    dashboard_screenshots/
  outputs/
    charts/
    maps/
    summary_tables/
```
## 9. Project Phases and Timeline
Phase 1: Source Review and Project Setup

Tasks:
  - Create GitHub repository.
  - Create folder structure.
  - Write source note.
  - Review PDF structure.
  - Identify available fields.
  - Select 20–30 pages for initial sample.

Deliverables:
  - Repository structure.
  - Source note.
  - Initial data dictionary draft.
  - Sample extraction plan.

Phase 2: Data Extraction MVP

Tasks:
  - Extract 300–500 records.
  - Save raw extracted data.
  - Identify extraction errors.
  - Assess whether extraction can be automated.

Deliverables:
  - Raw extracted sample.
  - Extraction quality notebook.
  - Notes on PDF/OCR issues.

Phase 3: Data Cleaning and Structuring

Tasks:
  - Clean key variables.
  - Standardize settlement names.
  - Normalize age, gender, legal status, and origin fields.
  - Create unique person IDs.
  - Create cleaned sample dataset.

Deliverables:
  - Clean sample dataset.
  - Updated data dictionary.
  - Data cleaning notebook.
  - Phase 4: SQL Analysis

Tasks:
  - Load cleaned data into SQL database.
  - Create analysis queries.
  - Calculate basic demographic indicators.
  - Aggregate by settlement, age, gender, status, and origin.

Deliverables:
  - SQL table creation script.
  - SQL analysis queries.
  - Aggregated output tables.
  - Phase 5: Visualization and Dashboard

Tasks:
  - Create exploratory charts.
  - Build Tableau dashboard or static visual summary.
  - Create settlement-level visualizations.
  - Add maps if geographic data is reliable enough.

Deliverables:
  - Tableau dashboard or screenshots.
  - Charts and summary tables.
  - Optional settlement map.
  - Phase 6: Final Documentation

Tasks:
  - Write final README.
  - Add methodology.
  - Add limitations.
  - Summarize key findings.
  - Prepare portfolio-ready project description.

Deliverables:
  - Final GitHub README.
  - Methodology document.
  - Limitations document.
  - Portfolio summary.

## 10. Success Criteria

The project will be considered successful if it produces:

  - A clear, reproducible workflow from PDF source to structured data.
  - A cleaned analytical sample or full dataset.
  - A documented data dictionary.
  - At least 10 meaningful SQL queries.
  - At least 5 analytical visualizations.
  - A clear English-language GitHub README.
  - A portfolio-ready case study demonstrating data cleaning, SQL, Python, visualization, and historical data analysis.

## 11. Risks and Constraints

Potential risks:

  - PDF text may be difficult to extract.
  - OCR errors may affect names, places, and categories.
  - Historical terminology may be inconsistent.
  - Settlement names may be difficult to geocode.
  - Full person-level data may not be suitable for public release.
  - The project may become too large if the full dataset is attempted immediately.

Mitigation strategies:

  - Start with a 300–500 record MVP.
  - Preserve raw extracted text separately from cleaned data.
  - Document all cleaning decisions.
  - Use manual validation for a sample of records.
  - Publish only code, documentation, aggregated data, or a small sample until data-sharing conditions are clear.

## 12. Ethical and Legal Considerations

Although the records are historical, they are still person-level data. The project will avoid publishing the full raw dataset until copyright, access, and ethical considerations are reviewed.

The public GitHub repository may include:

  - Code.
  - Documentation.
  - Data dictionary.
  - Aggregated tables.
  - A small sample if appropriate.
  - Dashboard screenshots.

The repository should not include:

  - Full raw PDF if copyright is unclear.
  - Full person-level dataset unless permitted.
  - Sensitive interpretive claims not supported by the data.

## 13. Final Portfolio Positioning

This project demonstrates the ability to transform a complex historical source into a structured analytical product. It highlights skills relevant to junior data analyst roles, including data extraction, cleaning, SQL querying, exploratory analysis, visualization, documentation, and critical thinking about data quality and limitations.
