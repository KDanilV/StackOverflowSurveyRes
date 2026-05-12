import math

import pandas as pd
import pytest

from stackoverflow_analytics.main import (
    clean_survey_data,
    convert_years,
    extract_age_range,
    make_excel_sheet_name,
    max_reasonable_experience,
)


@pytest.mark.parametrize(
    ("raw_age", "expected"),
    [
        ("Under 18 years old", (0, 17)),
        ("18-24 years old", (18, 24)),
        ("25-34 years old", (25, 34)),
        ("65 years or older", (65, 100)),
        (None, (None, None)),
    ],
)
def test_extract_age_range(raw_age, expected):
    assert extract_age_range(raw_age) == expected


@pytest.mark.parametrize(
    ("raw_years", "expected"),
    [
        ("Less than 1 year", 0.5),
        ("More than 50 years", 51),
        ("10", 10.0),
        (7, 7),
    ],
)
def test_convert_years(raw_years, expected):
    assert convert_years(raw_years) == expected


def test_convert_years_invalid_value_returns_nan():
    assert math.isnan(convert_years("not available"))


def test_max_reasonable_experience_filters_impossible_values():
    row = pd.Series({"Age": "18-24 years old", "YearsCode": 30})
    assert max_reasonable_experience(row) is False


def test_clean_survey_data_splits_multi_select_columns():
    source = pd.DataFrame(
        [
            {
                "ResponseId": 1,
                "Age": "25-34 years old",
                "YearsCode": "10",
                "YearsCodePro": "5",
                "LanguageHaveWorkedWith": "Python;SQL",
                "Country": "United States",
            }
        ]
    )

    tables = clean_survey_data(source)

    assert set(tables) == {"Main", "LanguageHaveWorkedWith"}
    assert "LanguageHaveWorkedWith" not in tables["Main"].columns
    assert tables["LanguageHaveWorkedWith"]["LanguageHaveWorkedWith"].tolist() == [
        "Python",
        "SQL",
    ]


def test_clean_survey_data_reports_missing_required_columns():
    source = pd.DataFrame([{"ResponseId": 1}])

    with pytest.raises(ValueError, match="Missing required columns"):
        clean_survey_data(source)


def test_make_excel_sheet_name_keeps_names_unique_under_excel_limit():
    used_names = set()

    first = make_excel_sheet_name("A" * 40, used_names)
    second = make_excel_sheet_name("A" * 40, used_names)

    assert first == "A" * 31
    assert second == ("A" * 29) + "_1"
