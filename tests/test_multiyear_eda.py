import pandas as pd

from stackoverflow_analytics.multiyear_eda import (
    aggregate_technology_counts,
    build_core_frame,
    build_technology_frame,
    normalize_ai_adoption,
    normalize_years,
)


def test_normalize_years_handles_survey_text_values():
    assert normalize_years("Less than 1 year") == 0.5
    assert normalize_years("More than 50 years") == 51.0
    assert normalize_years("7") == 7.0


def test_build_core_frame_keeps_stable_analysis_columns():
    source = pd.DataFrame(
        {
            "ResponseId": [1],
            "Country": ["Germany"],
            "YearsCode": ["Less than 1 year"],
            "ConvertedCompYearly": [100000],
            "UnusedColumn": ["drop me"],
        }
    )

    result = build_core_frame(2025, source)

    assert "SurveyYear" in result.columns
    assert "UnusedColumn" not in result.columns
    assert result.loc[0, "SurveyYear"] == 2025
    assert result.loc[0, "YearsCode"] == 0.5
    assert result.loc[0, "HasSalary"]
    assert result.loc[0, "ProfessionalExperience"] is pd.NA or pd.isna(
        result.loc[0, "ProfessionalExperience"]
    )


def test_build_technology_frame_splits_worked_and_wanted_values():
    source = pd.DataFrame(
        {
            "ResponseId": [1],
            "LanguageHaveWorkedWith": ["Python;SQL"],
            "LanguageWantToWorkWith": ["Rust"],
        }
    )

    result = build_technology_frame(2024, source)

    assert set(result["Technology"]) == {"Python", "SQL", "Rust"}
    assert set(result["Intent"]) == {"worked", "wanted"}


def test_aggregate_technology_counts_counts_unique_respondents():
    source = pd.DataFrame(
        {
            "SurveyYear": [2024, 2024, 2024],
            "ResponseId": [1, 1, 2],
            "Category": ["language", "language", "language"],
            "Intent": ["worked", "worked", "worked"],
            "Technology": ["Python", "Python", "Python"],
            "SourceColumn": ["LanguageHaveWorkedWith"] * 3,
        }
    )

    result = aggregate_technology_counts([source])

    assert result.loc[0, "Respondents"] == 2


def test_aggregate_technology_counts_handles_empty_inputs():
    result = aggregate_technology_counts([])

    assert result.empty
    assert result.columns.tolist() == [
        "SurveyYear",
        "Category",
        "Intent",
        "Technology",
        "Respondents",
    ]


def test_build_core_frame_normalizes_2025_job_sat_and_ai_fields():
    source = pd.DataFrame(
        {
            "ResponseId": [1],
            "WorkExp": [6],
            "JobSatPoints_1": [8],
            "JobSatPoints_2": [6],
            "AIToolCurrently mostly AI": ["Writing code"],
        }
    )

    result = build_core_frame(2025, source)

    assert result.loc[0, "ProfessionalExperience"] == 6
    assert result.loc[0, "JobSatNormalized"] == 7
    assert result.loc[0, "AIAdoption"] == "Использует AI"


def test_normalize_ai_adoption_detects_planned_usage():
    source = pd.DataFrame({"AIToolPlan to partially use AI": ["Testing"]})

    result = normalize_ai_adoption(source)

    assert result.iloc[0] == "Планирует использовать AI"


def test_normalize_ai_adoption_prioritizes_current_usage():
    source = pd.DataFrame(
        {
            "AIToolCurrently mostly AI": ["Writing code"],
            "AIToolDon't plan to use AI for this task": ["Meetings"],
        }
    )

    result = normalize_ai_adoption(source)

    assert result.iloc[0] == "Использует AI"
