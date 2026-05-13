from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

RAW_SURVEY_FILE = RAW_DATA_DIR / "survey_results_public.xlsx"
CLEANED_SURVEY_FILE = PROCESSED_DATA_DIR / "Cleaned_SurveyData.xlsx"
CLEANED_SURVEY_MANIFEST_FILE = PROCESSED_DATA_DIR / "Cleaned_SurveyData.manifest.json"
MULTIYEAR_PROCESSED_DIR = PROCESSED_DATA_DIR / "multiyear"
MULTIYEAR_CORE_FILE = MULTIYEAR_PROCESSED_DIR / "core_survey.csv"
MULTIYEAR_TECHNOLOGY_COUNTS_FILE = MULTIYEAR_PROCESSED_DIR / "technology_counts.csv"
MULTIYEAR_EDA_SUMMARY_FILE = MULTIYEAR_PROCESSED_DIR / "eda_summary.json"

DASHBOARD_DATA_DIR = PROJECT_ROOT / "data" / "dashboard"
DASHBOARD_CORE_FILE = DASHBOARD_DATA_DIR / "core_survey.csv.gz"
DASHBOARD_TECHNOLOGY_COUNTS_FILE = DASHBOARD_DATA_DIR / "technology_counts.csv.gz"
