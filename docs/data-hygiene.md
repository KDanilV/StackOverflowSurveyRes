# Data Hygiene Notes

The repository currently contains large files that are used by the ETL scripts:

- `data/raw/survey_results_public.csv.xlsx`
- `data/raw/survey_results_public.xlsx`
- `data/processed/Cleaned_SurveyData.xlsx`

These files make the repository self-contained, but they also make clones heavier.

Final decision:

1. Keep raw survey files in Git.
2. Do not commit generated outputs such as `data/processed/Cleaned_SurveyData.xlsx`.
3. Regenerate processed outputs with the pipeline when needed.

Longer term, replace Excel as the intermediate format with Parquet for faster Streamlit startup.

