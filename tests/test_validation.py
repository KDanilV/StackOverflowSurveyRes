import pandas as pd

from stackoverflow_analytics.validate import validate_cleaned_tables


def test_validate_cleaned_tables_accepts_consistent_tables():
    tables = {
        "Main": pd.DataFrame([{"ResponseId": 1}, {"ResponseId": 2}]),
        "LanguageHaveWorkedWith": pd.DataFrame(
            [{"ResponseId": 1, "LanguageHaveWorkedWith": "Python"}]
        ),
    }

    assert validate_cleaned_tables(tables) == []


def test_validate_cleaned_tables_requires_main_sheet():
    assert validate_cleaned_tables({}) == ['Missing required sheet: "Main"']


def test_validate_cleaned_tables_requires_main_response_id():
    tables = {"Main": pd.DataFrame([{"Other": 1}])}

    assert validate_cleaned_tables(tables) == ['Missing required column in "Main": ResponseId']


def test_validate_cleaned_tables_reports_duplicate_main_response_ids():
    tables = {"Main": pd.DataFrame([{"ResponseId": 1}, {"ResponseId": 1}])}

    errors = validate_cleaned_tables(tables)

    assert any("duplicate ResponseId" in error for error in errors)


def test_validate_cleaned_tables_reports_unknown_child_response_ids():
    tables = {
        "Main": pd.DataFrame([{"ResponseId": 1}]),
        "LanguageHaveWorkedWith": pd.DataFrame(
            [{"ResponseId": 2, "LanguageHaveWorkedWith": "Python"}]
        ),
    }

    errors = validate_cleaned_tables(tables)

    assert any("references unknown ResponseId" in error for error in errors)
