# Stack Overflow Survey Analytics

ETL and Streamlit analytics project for the Stack Overflow Developer Survey. The
repository prepares raw survey data, normalizes multi-select answers, validates processed
outputs, and serves an interactive Streamlit dashboard.

Balloon idea credit: [Andekster](https://github.com/Andekster).

## Project Scope

- Clean and validate Stack Overflow Developer Survey data.
- Split multi-select survey answers into separate analytical tables.
- Calculate salary values in USD for salary-focused analysis.
- Provide a Streamlit dashboard for overview, salary, technologies, AI adoption, and work trends.

## Repository Layout

```text
data/
  raw/                      Source Stack Overflow survey files
  processed/                Generated pipeline outputs, ignored by Git
app/
  streamlit_app.py          Streamlit dashboard
stackoverflow_analytics/
  main.py                   Clean source data and write Cleaned_SurveyData.xlsx
  validate.py               Validate cleaned workbook integrity
  tousd.py                  Salary conversion helpers
  dashboard_data.py         Streamlit data preparation helpers
  kaggle_data.py            Download optional multi-year Kaggle sources
  multiyear_eda.py          Curate compact multi-year analysis files
  pipeline.py               Run cleaning and validation
  config.py                 Shared paths
pyproject.toml              uv dependencies and ruff configuration
```

## Requirements

- Python 3.12+
- `uv`

## Setup

```powershell
uv sync
```

## Pipeline

Generate processed data from the repository root:

```powershell
uv run python -m stackoverflow_analytics.pipeline
```

The generated files are intentionally not committed:

- `data/processed/Cleaned_SurveyData.xlsx`
- `data/processed/Cleaned_SurveyData.manifest.json`
- `data/processed/multiyear/`

## Streamlit Dashboard

Run the dashboard:

```powershell
uv run streamlit run app/streamlit_app.py
```

If generated outputs are missing, the dashboard creates the cleaned workbook and multi-year
EDA files from `data/raw/` during the first startup.

Current dashboard sections:

- Overview
- Salary
- Technologies
- AI
- Work & Career
- Trends

## Code Quality

```powershell
uv run ruff check .
uv run ruff format .
uv run pytest
```

## Data Notes

- `ResponseId` is the central identifier.
- Multi-select columns are detected by semicolon-separated values and exploded into separate
  tables.
- `data/processed/Cleaned_SurveyData.manifest.json` maps Excel sheet names back to full logical
  table names, avoiding data loss from Excel's 31-character sheet-name limit.
- `YearsCode` and `YearsCodePro` are converted to numeric values.
- Cleaned workbook validation checks `Main.ResponseId` uniqueness and child-table references.
- Salary conversion uses static exchange rates in `stackoverflow_analytics/tousd.py`; this
  is suitable for exploratory analytics, but should be documented or replaced with a dated
  exchange-rate source for stricter financial analysis.
- Raw files currently occupy about 480 MB and are kept in Git because the project is considered
  final and will not receive regular data refreshes.

Additional notes:

- [Data hygiene](docs/data-hygiene.md)
- [Multi-year data](docs/multi-year-data.md)
- [Streamlit dashboard plan](docs/streamlit-dashboard.md)

## Optional Multi-Year Sources

Additional Kaggle datasets can be downloaded for 2022, 2023, and 2025:

```powershell
uv run python -m stackoverflow_analytics.kaggle_data
```

Kaggle requires `%USERPROFILE%\.kaggle\kaggle.json` or `KAGGLE_CONFIG_DIR` with API
credentials. The downloaded files are placed under `data/raw/<year>/` and are intended to stay
in Git together with the existing raw files.

Run basic multi-year EDA and keep only important comparable fields:

```powershell
uv run python -m stackoverflow_analytics.multiyear_eda
```

Generated outputs:

- `data/processed/multiyear/core_survey.csv`
- `data/processed/multiyear/technology_counts.csv`
- `data/processed/multiyear/eda_summary.json`

The Streamlit `Trends` tab uses these files for year-over-year salary, remote work, AI adoption,
and technology popularity views.

## Current Limitations

- Streamlit currently reads the main yearly workbook from Excel; Parquet would be faster for startup.
- Generated outputs under `data/processed/` must be regenerated locally.


