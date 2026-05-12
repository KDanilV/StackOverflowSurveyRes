import os
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from stackoverflow_analytics.dashboard_data import (
    filter_main_table,
    language_popularity,
    median_salary_by_group,
    multiyear_ai_adoption_trend,
    multiyear_remote_trend,
    multiyear_salary_trend,
    multiyear_top_technologies,
    prepare_main_table,
    read_language_table,
    read_main_table,
    read_multiyear_core,
    read_multiyear_technology_counts,
    read_technology_tables,
    read_wanted_language_table,
    salary_by_country,
    technology_count_distribution,
    technology_popularity,
    top_counts,
    worked_vs_wanted_languages,
)

TEST_MODE_ENV = "STACKOVERFLOW_ANALYTICS_TEST_MODE"


@dataclass(frozen=True)
class DashboardData:
    main: pd.DataFrame
    language: pd.DataFrame
    wanted_language: pd.DataFrame
    technology_tables: dict[str, pd.DataFrame]
    multiyear_core: pd.DataFrame
    multiyear_technology_counts: pd.DataFrame


st.set_page_config(
    page_title="Stack Overflow Survey Analytics",
    page_icon=":bar_chart:",
    layout="wide",
)


def build_test_data() -> DashboardData:
    main = pd.DataFrame(
        [
            {
                "ResponseId": 1,
                "Country": "United States",
                "RemoteWork": "Remote",
                "EdLevel": "Bachelor",
                "Age": "25-34 years old",
                "DevType": "Developer, full-stack",
                "YearsCodePro": 5,
                "JobSat": 8,
                "AISelect": "Yes",
                "AISent": "Favorable",
                "salaryusd": 100000.0,
            }
        ]
    )
    language = pd.DataFrame([{"ResponseId": 1, "LanguageHaveWorkedWith": "Python"}])
    wanted_language = pd.DataFrame([{"ResponseId": 1, "LanguageWantToWorkWith": "Python"}])
    technology_tables = {
        "Databases": pd.DataFrame([{"ResponseId": 1, "DatabaseHaveWorkedWith": "SQLite"}]),
        "Platforms": pd.DataFrame([{"ResponseId": 1, "PlatformHaveWorkedWith": "AWS"}]),
    }
    multiyear_core = pd.DataFrame(
        [
            {
                "SurveyYear": 2024,
                "ResponseId": 1,
                "RemoteWork": "Remote",
                "ConvertedCompYearly": 100000,
                "AIAdoption": "Использует AI",
            }
        ]
    )
    multiyear_technology_counts = pd.DataFrame(
        [
            {
                "SurveyYear": 2024,
                "Category": "language",
                "Intent": "worked",
                "Technology": "Python",
                "Respondents": 1,
            }
        ]
    )
    return DashboardData(
        main=main,
        language=language,
        wanted_language=wanted_language,
        technology_tables=technology_tables,
        multiyear_core=multiyear_core,
        multiyear_technology_counts=multiyear_technology_counts,
    )


@st.cache_data(show_spinner="Loading survey data...")
def load_data() -> DashboardData:
    if os.getenv(TEST_MODE_ENV) == "1":
        return build_test_data()

    return DashboardData(
        main=prepare_main_table(read_main_table()),
        language=read_language_table(),
        wanted_language=read_wanted_language_table(),
        technology_tables=read_technology_tables(),
        multiyear_core=read_multiyear_core(),
        multiyear_technology_counts=read_multiyear_technology_counts(),
    )


def format_int(value):
    return f"{int(value):,}".replace(",", " ")


def render_sidebar(main_table: pd.DataFrame):
    with st.sidebar:
        st.header("Filters")
        countries = st.multiselect(
            "Country",
            sorted(main_table["Country"].dropna().unique()),
        )
        remote_work = st.multiselect(
            "Remote work",
            sorted(main_table["RemoteWork"].dropna().unique()),
        )
        education = st.multiselect(
            "Education",
            sorted(main_table["EdLevel"].dropna().unique()),
        )
        developer_type = st.multiselect(
            "Developer type",
            sorted(main_table["DevType"].dropna().unique()) if "DevType" in main_table else [],
        )

    return countries, remote_work, education, developer_type


def apply_filters(main_table: pd.DataFrame, filters):
    countries, remote_work, education, developer_type = filters
    filtered = filter_main_table(main_table, countries, remote_work, education)
    if developer_type and "DevType" in filtered:
        filtered = filtered[filtered["DevType"].isin(developer_type)]
    return filtered


def render_kpis(filtered: pd.DataFrame, language_table: pd.DataFrame, filtered_ids: set):
    total_respondents = len(filtered)
    country_count = filtered["Country"].nunique()
    median_salary = filtered["salaryusd"].median()
    top_language = language_popularity(language_table, filtered_ids, limit=1)

    kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
    kpi_1.metric("Respondents", format_int(total_respondents))
    kpi_2.metric("Countries", format_int(country_count))
    kpi_3.metric(
        "Median salary, USD",
        "n/a" if pd.isna(median_salary) else f"${median_salary:,.0f}",
    )
    kpi_4.metric(
        "Top language",
        "n/a" if top_language.empty else top_language.iloc[0]["LanguageHaveWorkedWith"],
    )


def render_overview_tab(filtered: pd.DataFrame):
    left, right = st.columns(2)
    with left:
        st.subheader("Respondents by country")
        st.bar_chart(top_counts(filtered, "Country", 20), x="Country", y="count")
    with right:
        st.subheader("Remote work")
        st.bar_chart(top_counts(filtered, "RemoteWork", 10), x="RemoteWork", y="count")

    st.subheader("Education")
    st.bar_chart(top_counts(filtered, "EdLevel", 15), x="EdLevel", y="count")

    st.subheader("Age")
    st.bar_chart(top_counts(filtered, "Age", 12), x="Age", y="count")


def render_salary_tab(filtered: pd.DataFrame):
    st.subheader("Median salary by country")
    country_salary = salary_by_country(filtered, 20)
    st.bar_chart(country_salary, x="Country", y="median_salary_usd")

    left, right = st.columns(2)
    with left:
        st.subheader("Median salary by experience")
        experience_salary = median_salary_by_group(filtered, "YearsCodePro", 20)
        st.bar_chart(experience_salary, x="YearsCodePro", y="median_salary_usd")
    with right:
        st.subheader("Median salary by education")
        education_salary = median_salary_by_group(filtered, "EdLevel", 12)
        st.bar_chart(education_salary, x="EdLevel", y="median_salary_usd")

    st.subheader("Salary distribution")
    salary_values = filtered["salaryusd"].dropna()
    if salary_values.empty:
        st.info("No salary data for the current filters.")
        return

    salary_bins = pd.cut(salary_values, bins=20)
    salary_distribution = (
        salary_bins.value_counts()
        .sort_index()
        .rename_axis("salary_range")
        .reset_index(name="count")
    )
    salary_distribution["salary_range"] = salary_distribution["salary_range"].astype(str)
    st.bar_chart(salary_distribution, x="salary_range", y="count")


def render_technologies_tab(data: DashboardData, filtered_ids: set):
    st.subheader("Language popularity")
    language_counts = language_popularity(data.language, filtered_ids, 20)
    st.bar_chart(language_counts, x="LanguageHaveWorkedWith", y="count")

    st.subheader("Worked vs wanted languages")
    language_comparison = worked_vs_wanted_languages(
        data.language, data.wanted_language, filtered_ids, 25
    )
    st.dataframe(language_comparison, use_container_width=True)

    st.subheader("Technology popularity")
    technology_counts = technology_popularity(data.technology_tables, filtered_ids, 15)
    for category, category_data in technology_counts.groupby("category"):
        st.caption(category)
        st.bar_chart(category_data, x="technology", y="count")

    st.subheader("Technology stack breadth")
    stack_width = technology_count_distribution(data.technology_tables, filtered_ids)
    st.bar_chart(stack_width, x="technology_count", y="respondents")


def render_ai_tab(filtered: pd.DataFrame):
    left, right = st.columns(2)
    with left:
        st.subheader("AI selection")
        st.bar_chart(top_counts(filtered, "AISelect", 10), x="AISelect", y="count")
    with right:
        st.subheader("AI sentiment")
        st.bar_chart(top_counts(filtered, "AISent", 10), x="AISent", y="count")


def render_work_tab(filtered: pd.DataFrame):
    left, right = st.columns(2)
    with left:
        st.subheader("Developer type")
        st.bar_chart(top_counts(filtered, "DevType", 15), x="DevType", y="count")
    with right:
        st.subheader("Job satisfaction")
        st.bar_chart(top_counts(filtered, "JobSat", 12), x="JobSat", y="count")

    st.subheader("Remote work by country")
    remote_by_country = (
        filtered.dropna(subset=["Country", "RemoteWork"])
        .groupby(["Country", "RemoteWork"], as_index=False)
        .size()
        .sort_values("size", ascending=False)
        .head(40)
    )
    st.dataframe(remote_by_country, use_container_width=True)


def render_trends_tab(data: DashboardData):
    if data.multiyear_core.empty:
        st.info("Run multi-year EDA to generate trend data.")
        return

    left, right = st.columns(2)
    with left:
        st.subheader("Median salary by year")
        st.line_chart(
            multiyear_salary_trend(data.multiyear_core),
            x="SurveyYear",
            y="median_salary_usd",
        )
    with right:
        st.subheader("AI adoption by year")
        st.bar_chart(
            multiyear_ai_adoption_trend(data.multiyear_core),
            x="SurveyYear",
            y="respondents",
            color="AIAdoption",
        )

    st.subheader("Remote work by year")
    st.bar_chart(
        multiyear_remote_trend(data.multiyear_core),
        x="SurveyYear",
        y="respondents",
        color="RemoteWork",
    )

    st.subheader("Top worked-with languages")
    language_trend = multiyear_top_technologies(
        data.multiyear_technology_counts,
        category="language",
        intent="worked",
        limit=10,
    )
    st.line_chart(
        language_trend,
        x="SurveyYear",
        y="Respondents",
        color="Technology",
    )


def main():
    st.title("Stack Overflow Developer Survey")

    data = load_data()
    filtered = apply_filters(data.main, render_sidebar(data.main))
    filtered_ids = set(filtered["ResponseId"])
    render_kpis(filtered, data.language, filtered_ids)

    overview_tab, salary_tab, tech_tab, ai_tab, work_tab, trends_tab = st.tabs(
        ["Overview", "Salary", "Technologies", "AI", "Work & Career", "Trends"]
    )

    with overview_tab:
        render_overview_tab(filtered)
    with salary_tab:
        render_salary_tab(filtered)
    with tech_tab:
        render_technologies_tab(data, filtered_ids)
    with ai_tab:
        render_ai_tab(filtered)
    with work_tab:
        render_work_tab(filtered)
    with trends_tab:
        render_trends_tab(data)


if __name__ == "__main__":
    main()
