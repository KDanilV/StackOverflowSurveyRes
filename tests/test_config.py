from stackoverflow_analytics.config import (
    CLEANED_SURVEY_FILE,
    CLEANED_SURVEY_MANIFEST_FILE,
    PROJECT_ROOT,
    RAW_SURVEY_FILE,
)


def test_data_paths_point_to_data_directory():
    assert RAW_SURVEY_FILE == PROJECT_ROOT / "data" / "raw" / "survey_results_public.xlsx"
    assert CLEANED_SURVEY_FILE == PROJECT_ROOT / "data" / "processed" / "Cleaned_SurveyData.xlsx"
    assert (
        CLEANED_SURVEY_MANIFEST_FILE
        == PROJECT_ROOT / "data" / "processed" / "Cleaned_SurveyData.manifest.json"
    )
