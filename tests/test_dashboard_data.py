import pandas as pd

from stackoverflow_analytics.dashboard_data import (
    contains_any_multiselect_value,
    filter_main_table,
    filter_multiyear_core,
    language_popularity,
    median_salary_by_group,
    multiyear_ai_adoption_trend,
    multiyear_salary_trend,
    multiyear_top_technologies,
    prepare_main_table,
    salary_by_country,
    salary_map_by_country,
    split_multiselect_values,
    technology_count_distribution,
    technology_popularity,
    top_counts,
    worked_vs_wanted_languages,
)


def test_prepare_main_table_adds_salaryusd():
    source = pd.DataFrame(
        [
            {
                "ResponseId": 1,
                "Currency": "USD\tUnited States dollar",
                "CompTotal": "100000",
                "YearsCode": "10",
                "YearsCodePro": "5",
                "ConvertedCompYearly": "100000",
            }
        ]
    )

    result = prepare_main_table(source)

    assert result.iloc[0]["salaryusd"] == 100000


def test_filter_main_table_applies_selected_filters():
    source = pd.DataFrame(
        [
            {"ResponseId": 1, "Country": "A", "RemoteWork": "Remote", "EdLevel": "Bachelor"},
            {"ResponseId": 2, "Country": "B", "RemoteWork": "Hybrid", "EdLevel": "Master"},
        ]
    )

    result = filter_main_table(source, countries=["A"], remote_work=["Remote"])

    assert result["ResponseId"].tolist() == [1]


def test_filter_multiyear_core_applies_sidebar_filters():
    source = pd.DataFrame(
        [
            {
                "SurveyYear": 2024,
                "ResponseId": 1,
                "Country": "A",
                "RemoteWork": "Remote",
                "EdLevel": "Bachelor",
                "DevType": "Developer, back-end;Developer, full-stack",
            },
            {
                "SurveyYear": 2025,
                "ResponseId": 2,
                "Country": "B",
                "RemoteWork": "Hybrid",
                "EdLevel": "Master",
                "DevType": "Data scientist",
            },
        ]
    )

    result = filter_multiyear_core(
        source,
        years=[2024],
        countries=["A"],
        remote_work=["Remote"],
        education=["Bachelor"],
        developer_type=["Developer, full-stack"],
    )

    assert result["ResponseId"].tolist() == [1]


def test_filter_multiyear_core_empty_year_selection_returns_no_rows():
    source = pd.DataFrame({"SurveyYear": [2024], "ResponseId": [1]})

    result = filter_multiyear_core(source, years=[])

    assert result.empty


def test_multiselect_helpers_split_and_match_values():
    source = pd.Series(["Developer, back-end; Developer, full-stack", None, "Data scientist"])

    values = split_multiselect_values(source)
    mask = contains_any_multiselect_value(source, ["Developer, full-stack"])

    assert values.tolist() == ["Developer, back-end", "Developer, full-stack", "Data scientist"]
    assert mask.tolist() == [True, False, False]


def test_top_counts_returns_sorted_counts():
    source = pd.DataFrame({"Country": ["A", "A", "B"]})

    result = top_counts(source, "Country")

    assert result.to_dict("records")[0] == {"Country": "A", "count": 2}


def test_salary_by_country_uses_median_salary():
    source = pd.DataFrame(
        [
            {"ResponseId": 1, "Country": "A", "salaryusd": 100.0},
            {"ResponseId": 2, "Country": "A", "salaryusd": 300.0},
            {"ResponseId": 3, "Country": "B", "salaryusd": 1000.0},
        ]
    )

    result = salary_by_country(source)

    assert result.iloc[0]["Country"] == "B"
    assert result[result["Country"] == "A"].iloc[0]["median_salary_usd"] == 200.0


def test_median_salary_by_group_uses_requested_group():
    source = pd.DataFrame(
        [
            {"ResponseId": 1, "EdLevel": "Bachelor", "salaryusd": 100.0},
            {"ResponseId": 2, "EdLevel": "Bachelor", "salaryusd": 300.0},
        ]
    )

    result = median_salary_by_group(source, "EdLevel")

    assert result.iloc[0]["median_salary_usd"] == 200.0


def test_language_popularity_can_filter_by_response_ids():
    source = pd.DataFrame(
        [
            {"ResponseId": 1, "LanguageHaveWorkedWith": "Python"},
            {"ResponseId": 2, "LanguageHaveWorkedWith": "SQL"},
        ]
    )

    result = language_popularity(source, response_ids={1})

    assert result["LanguageHaveWorkedWith"].tolist() == ["Python"]


def test_worked_vs_wanted_languages_compares_counts():
    worked = pd.DataFrame(
        [
            {"ResponseId": 1, "LanguageHaveWorkedWith": "Python"},
            {"ResponseId": 2, "LanguageHaveWorkedWith": "SQL"},
        ]
    )
    wanted = pd.DataFrame(
        [
            {"ResponseId": 1, "LanguageWantToWorkWith": "Python"},
            {"ResponseId": 2, "LanguageWantToWorkWith": "Python"},
        ]
    )

    result = worked_vs_wanted_languages(worked, wanted)

    python_row = result[result["language"] == "Python"].iloc[0]
    assert python_row["worked_count"] == 1
    assert python_row["wanted_count"] == 2


def test_technology_popularity_combines_categories():
    tables = {
        "Databases": pd.DataFrame(
            [
                {"ResponseId": 1, "DatabaseHaveWorkedWith": "SQLite"},
                {"ResponseId": 2, "DatabaseHaveWorkedWith": "SQLite"},
            ]
        )
    }

    result = technology_popularity(tables)

    assert result.iloc[0]["technology"] == "SQLite"
    assert result.iloc[0]["category"] == "Databases"


def test_technology_count_distribution_counts_stack_breadth():
    tables = {
        "Databases": pd.DataFrame([{"ResponseId": 1}, {"ResponseId": 2}]),
        "Platforms": pd.DataFrame([{"ResponseId": 1}]),
    }

    result = technology_count_distribution(tables)

    assert result.to_dict("records") == [
        {"technology_count": 1, "respondents": 1},
        {"technology_count": 2, "respondents": 1},
    ]


def test_multiyear_salary_trend_uses_median_by_year():
    core = pd.DataFrame(
        {
            "SurveyYear": [2024, 2024, 2025],
            "ResponseId": [1, 2, 3],
            "ConvertedCompYearly": [100, 300, 500],
        }
    )

    result = multiyear_salary_trend(core)

    assert result.loc[result["SurveyYear"] == 2024, "median_salary_usd"].iloc[0] == 200


def test_multiyear_salary_trend_filters_selected_years():
    core = pd.DataFrame(
        {
            "SurveyYear": [2024, 2025],
            "ResponseId": [1, 2],
            "ConvertedCompYearly": [100, 500],
        }
    )

    result = multiyear_salary_trend(core, years=[2025])

    assert result["SurveyYear"].tolist() == [2025]


def test_multiyear_ai_adoption_trend_counts_statuses():
    core = pd.DataFrame(
        {
            "SurveyYear": [2024, 2024],
            "ResponseId": [1, 2],
            "AIAdoption": ["Использует AI", "Не использует AI"],
        }
    )

    result = multiyear_ai_adoption_trend(core)

    assert result["respondents"].sum() == 2


def test_multiyear_ai_adoption_trend_filters_selected_years():
    core = pd.DataFrame(
        {
            "SurveyYear": [2024, 2025],
            "ResponseId": [1, 2],
            "AIAdoption": ["Использует AI", "Не использует AI"],
        }
    )

    result = multiyear_ai_adoption_trend(core, years=[2025])

    assert result["SurveyYear"].tolist() == [2025]


def test_multiyear_top_technologies_filters_category_and_intent():
    counts = pd.DataFrame(
        {
            "SurveyYear": [2024, 2024, 2025],
            "Category": ["language", "database", "language"],
            "Intent": ["worked", "worked", "wanted"],
            "Technology": ["Python", "PostgreSQL", "Rust"],
            "Respondents": [10, 5, 7],
        }
    )

    result = multiyear_top_technologies(counts, "language", "worked")

    assert result["Technology"].tolist() == ["Python"]


def test_multiyear_top_technologies_filters_selected_years():
    counts = pd.DataFrame(
        {
            "SurveyYear": [2024, 2025],
            "Category": ["language", "language"],
            "Intent": ["worked", "worked"],
            "Technology": ["Python", "Rust"],
            "Respondents": [10, 7],
        }
    )

    result = multiyear_top_technologies(counts, "language", "worked", years=[2025])

    assert result["Technology"].tolist() == ["Rust"]


def test_salary_map_by_country_filters_by_year_and_threshold():
    core = pd.DataFrame(
        {
            "SurveyYear": [2024, 2024, 2024, 2025],
            "ResponseId": [1, 2, 3, 4],
            "Country": ["A", "A", "B", "A"],
            "ConvertedCompYearly": [100, 300, 1000, 500],
        }
    )

    result = salary_map_by_country(core, years=[2024], min_respondents=2)

    assert result.to_dict("records") == [
        {"Country": "A", "median_salary_usd": 200.0, "respondents": 2}
    ]


def test_salary_map_by_country_handles_missing_required_columns():
    result = salary_map_by_country(pd.DataFrame({"SurveyYear": [2024]}))

    assert result.empty
    assert result.columns.tolist() == ["Country", "median_salary_usd", "respondents"]
