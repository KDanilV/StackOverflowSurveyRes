import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from stackoverflow_analytics.config import (  # noqa: E402
    DASHBOARD_CORE_FILE,
    DASHBOARD_TECHNOLOGY_COUNTS_FILE,
    MULTIYEAR_CORE_FILE,
    MULTIYEAR_TECHNOLOGY_COUNTS_FILE,
)
from stackoverflow_analytics.dashboard_data import (
    contains_any_multiselect_value,
    filter_main_table,
    filter_multiyear_core,
    language_popularity,
    median_compensation_by_group,
    multiyear_ai_adoption_trend,
    multiyear_remote_trend,
    multiyear_salary_trend,
    multiyear_top_technologies,
    read_multiyear_core,
    read_multiyear_technology_counts,
    salary_map_by_country,
    technology_count_distribution,
    top_counts,
    unique_multiselect_options,
)
from stackoverflow_analytics.multiyear_eda import run_eda as run_multiyear_eda  # noqa: E402

TEST_MODE_ENV = "STACKOVERFLOW_ANALYTICS_TEST_MODE"
MAX_CHART_LABEL_LENGTH = 34
MAX_EXPERIENCE_YEARS = 50
MAX_SALARY_DISTRIBUTION_USD = 500_000
SALARY_DISTRIBUTION_STEP_USD = 25_000
SALARY_MAP_COLOR_SCALE = [
    [0.0, "#c62828"],
    [0.5, "#f9d65c"],
    [1.0, "#1b8f3a"],
]
DISPLAY_VALUE_REPLACEMENTS = {
    "РСЃРїРѕР»СЊР·СѓРµС‚ AI": "Uses AI",
    "Использует AI": "Uses AI",
    "РџР»Р°РЅРёСЂСѓРµС‚ РёСЃРїРѕР»СЊР·РѕРІР°С‚СЊ AI": "Plans to use AI",
    "Планирует использовать AI": "Plans to use AI",
    "РќРµ РёСЃРїРѕР»СЊР·СѓРµС‚ AI": "Does not use AI",
    "Не использует AI": "Does not use AI",
    "РќРµС‚ РґР°РЅРЅС‹С…": "No data",
    "Нет данных": "No data",
}
PAGES = [
    "Overview",
    "Salary",
    "World Map",
    "Technologies",
    "AI",
    "Work & Career",
    "Trends",
]


@dataclass(frozen=True)
class DashboardData:
    main: pd.DataFrame
    language: pd.DataFrame
    wanted_language: pd.DataFrame
    technology_tables: dict[str, pd.DataFrame]
    multiyear_core: pd.DataFrame
    multiyear_technology_counts: pd.DataFrame


@dataclass(frozen=True)
class SidebarState:
    page: str
    countries: list[str]
    remote_work: list[str]
    education: list[str]
    developer_type: list[str]
    years: list[int]
    experience_range: tuple[int, int]
    minimum_country_respondents: int


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
                "Country": "United States",
                "RemoteWork": "Remote",
                "EdLevel": "Bachelor",
                "Age": "25-34 years old",
                "DevType": "Developer, full-stack",
                "ConvertedCompYearly": 100000,
                "ProfessionalExperience": 5,
                "YearsCodePro": 5,
                "AISent": "Favorable",
                "JobSatNormalized": 8,
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

    ensure_dashboard_outputs()
    multiyear_core = read_multiyear_core()

    return DashboardData(
        main=build_main_from_multiyear(multiyear_core),
        language=pd.DataFrame(columns=["ResponseId", "LanguageHaveWorkedWith"]),
        wanted_language=pd.DataFrame(columns=["ResponseId", "LanguageWantToWorkWith"]),
        technology_tables={},
        multiyear_core=multiyear_core,
        multiyear_technology_counts=read_multiyear_technology_counts(),
    )


def ensure_dashboard_outputs():
    packaged_outputs_exist = (
        DASHBOARD_CORE_FILE.exists() and DASHBOARD_TECHNOLOGY_COUNTS_FILE.exists()
    )
    processed_outputs_exist = (
        MULTIYEAR_CORE_FILE.exists() and MULTIYEAR_TECHNOLOGY_COUNTS_FILE.exists()
    )
    if packaged_outputs_exist or processed_outputs_exist:
        return

    run_multiyear_eda()


def build_main_from_multiyear(multiyear_core: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "ResponseId",
        "Country",
        "RemoteWork",
        "EdLevel",
        "Age",
        "DevType",
        "ConvertedCompYearly",
        "ProfessionalExperience",
        "YearsCodePro",
    ]
    if multiyear_core.empty:
        return pd.DataFrame(columns=[*columns, "salaryusd"])

    main = multiyear_core[multiyear_core["SurveyYear"] == 2024].copy()
    if main.empty:
        main = multiyear_core.copy()

    main = main.reindex(columns=columns)
    main["salaryusd"] = main["ConvertedCompYearly"]
    return main


def format_int(value):
    return f"{int(value):,}".replace(",", " ")


def short_chart_label(value, max_length: int = MAX_CHART_LABEL_LENGTH) -> str:
    if pd.isna(value):
        return "n/a"

    text = str(value).strip()
    text = DISPLAY_VALUE_REPLACEMENTS.get(text, text)
    is_interval = text.startswith(("(", "[")) and "," in text and text.endswith((")", "]"))
    if not is_interval:
        text = re.sub(r"\s*\([^)]*\)", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) <= max_length:
        return text
    return text[: max_length - 1].rstrip() + "…"


def chart_display_frame(
    data: pd.DataFrame,
    columns: list[str | None],
    max_length: int = MAX_CHART_LABEL_LENGTH,
) -> tuple[pd.DataFrame, dict[str, str]]:
    display_data = data.copy()
    display_columns = {}

    for column in columns:
        if (
            column
            and column in display_data
            and not pd.api.types.is_numeric_dtype(display_data[column])
        ):
            display_column = f"{column}__display"
            display_data[display_column] = display_data[column].map(
                lambda value: short_chart_label(value, max_length)
            )
            display_columns[column] = display_column

    return display_data, display_columns


def format_salary_range(left: float, right: float) -> str:
    return f"${left:,.0f} - ${right:,.0f}"


def salary_distribution_frame(
    salary_values: pd.Series,
    max_salary: int = MAX_SALARY_DISTRIBUTION_USD,
    step: int = SALARY_DISTRIBUTION_STEP_USD,
) -> pd.DataFrame:
    salary = pd.to_numeric(salary_values, errors="coerce").dropna()
    salary = salary[salary.between(0, max_salary, inclusive="both")]
    if salary.empty:
        return pd.DataFrame(columns=["salary_range", "count"])

    bins = list(range(0, max_salary + step, step))
    salary_bins = pd.cut(salary, bins=bins, include_lowest=True, right=False)
    distribution = (
        salary_bins.value_counts()
        .sort_index()
        .rename_axis("salary_range")
        .reset_index(name="count")
    )
    distribution = distribution[distribution["count"] > 0]
    distribution["salary_range"] = distribution["salary_range"].map(
        lambda interval: format_salary_range(interval.left, interval.right)
    )
    return distribution


def maybe_show_balloons():
    if os.getenv(TEST_MODE_ENV) == "1":
        return
    if st.session_state.get("balloons_shown"):
        return

    st.balloons()
    st.session_state["balloons_shown"] = True


def available_survey_years(multiyear_core: pd.DataFrame) -> list[int]:
    if multiyear_core.empty or "SurveyYear" not in multiyear_core:
        return []
    return [
        int(year) for year in sorted(multiyear_core["SurveyYear"].dropna().astype(int).unique())
    ]


def sidebar_options(source: pd.DataFrame, column: str) -> list[str]:
    if source.empty or column not in source:
        return []
    values = source[column].dropna().astype(str)
    if column == "DevType":
        return unique_multiselect_options(source[column])
    return sorted(values[values != ""].unique())


def filter_by_years(frame: pd.DataFrame, years: list[int]) -> pd.DataFrame:
    if frame.empty or "SurveyYear" not in frame or not years:
        return frame.iloc[0:0].copy() if not years else frame
    return frame[frame["SurveyYear"].isin(years)]


def countries_with_minimum_respondents(
    frame: pd.DataFrame,
    minimum_respondents: int,
) -> list[str]:
    if frame.empty or "Country" not in frame:
        return []

    counts = frame["Country"].dropna().astype(str).value_counts()
    return sorted(counts[counts >= minimum_respondents].index)


def render_sidebar(main_table: pd.DataFrame, multiyear_core: pd.DataFrame) -> SidebarState:
    years = available_survey_years(multiyear_core)
    filter_source = multiyear_core if not multiyear_core.empty else main_table

    with st.sidebar:
        st.header("Navigation")
        page = st.radio("Page", PAGES, label_visibility="collapsed")

        if years:
            st.header("Years")
            selected_years = st.multiselect(
                "Survey years",
                years,
                default=years,
            )
        else:
            selected_years = []

        st.header("Filters")
        minimum_country_respondents = st.number_input(
            "Minimum respondents per country",
            min_value=1,
            max_value=10_000,
            value=1,
            step=50,
        )
        country_source = filter_by_years(filter_source, selected_years)
        country_options = countries_with_minimum_respondents(
            country_source,
            int(minimum_country_respondents),
        )
        countries = st.multiselect(
            "Country",
            country_options,
        )
        remote_work = st.multiselect(
            "Remote work",
            sidebar_options(filter_source, "RemoteWork"),
        )
        education = st.multiselect(
            "Education",
            sidebar_options(filter_source, "EdLevel"),
        )
        developer_type = st.multiselect(
            "Developer type",
            sidebar_options(filter_source, "DevType"),
        )
        experience_range = st.slider(
            "Professional experience, years",
            min_value=0,
            max_value=MAX_EXPERIENCE_YEARS,
            value=(0, MAX_EXPERIENCE_YEARS),
            step=1,
        )

    return SidebarState(
        page=page,
        countries=countries,
        remote_work=remote_work,
        education=education,
        developer_type=developer_type,
        years=selected_years,
        experience_range=experience_range,
        minimum_country_respondents=int(minimum_country_respondents),
    )


def apply_filters(main_table: pd.DataFrame, sidebar: SidebarState):
    filtered = filter_main_table(
        main_table,
        sidebar.countries,
        sidebar.remote_work,
        sidebar.education,
    )
    if sidebar.developer_type and "DevType" in filtered:
        filtered = filtered[
            contains_any_multiselect_value(filtered["DevType"], sidebar.developer_type)
        ]
    if "YearsCodePro" in filtered:
        experience = pd.to_numeric(filtered["YearsCodePro"], errors="coerce")
        filtered = filtered[
            experience.isna() | experience.between(*sidebar.experience_range, inclusive="both")
        ]
    if sidebar.minimum_country_respondents and "Country" in filtered:
        valid_countries = countries_with_minimum_respondents(
            filtered,
            sidebar.minimum_country_respondents,
        )
        filtered = filtered[filtered["Country"].isin(valid_countries)]
    return filtered


def apply_multiyear_filters(multiyear_core: pd.DataFrame, sidebar: SidebarState):
    return filter_multiyear_core(
        multiyear_core,
        years=sidebar.years,
        countries=sidebar.countries,
        remote_work=sidebar.remote_work,
        education=sidebar.education,
        developer_type=sidebar.developer_type,
        experience_range=sidebar.experience_range,
        minimum_country_respondents=sidebar.minimum_country_respondents,
    )


def render_kpis(
    filtered: pd.DataFrame,
    language_table: pd.DataFrame,
    filtered_ids: set,
    filtered_multiyear: pd.DataFrame,
    technology_counts: pd.DataFrame,
    selected_years: list[int],
    has_multiyear_data: bool,
):
    if not has_multiyear_data:
        total_respondents = len(filtered)
        country_count = filtered["Country"].nunique()
        median_salary = filtered["salaryusd"].median()
        top_language_frame = language_popularity(language_table, filtered_ids, limit=1)
        top_language = (
            "n/a"
            if top_language_frame.empty
            else top_language_frame.iloc[0]["LanguageHaveWorkedWith"]
        )
    else:
        total_respondents = len(filtered_multiyear)
        country_count = (
            0 if "Country" not in filtered_multiyear else filtered_multiyear["Country"].nunique()
        )
        median_salary = (
            pd.NA
            if "ConvertedCompYearly" not in filtered_multiyear
            else filtered_multiyear["ConvertedCompYearly"].median()
        )
        top_language_frame = (
            pd.DataFrame()
            if not selected_years
            else multiyear_top_technologies(
                technology_counts,
                category="language",
                intent="worked",
                limit=1,
                years=selected_years,
            )
        )
        top_language = (
            "n/a" if top_language_frame.empty else top_language_frame.iloc[0]["Technology"]
        )

    kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
    kpi_1.metric("Respondents", format_int(total_respondents))
    kpi_2.metric("Countries", format_int(country_count))
    kpi_3.metric(
        "Median salary, USD",
        "n/a" if pd.isna(median_salary) else f"${median_salary:,.0f}",
    )
    kpi_4.metric(
        "Top language",
        top_language,
    )


def render_bar_chart(data, x, y, x_label, y_label, color=None, color_label=None):
    if data.empty:
        st.info("No data for the current filters.")
        return

    chart_data, display_columns = chart_display_frame(data, [x, color])
    chart_x = display_columns.get(x, x)
    chart_color = display_columns.get(color, color)
    labels = {chart_x: x_label, y: y_label}
    if chart_color:
        labels[chart_color] = color_label or color or "Category"

    fig = px.bar(
        chart_data,
        x=chart_x,
        y=y,
        color=chart_color,
        labels=labels,
    )
    fig.update_layout(margin={"r": 8, "t": 8, "l": 8, "b": 8})
    st.plotly_chart(fig, use_container_width=True)


def render_line_chart(data, x, y, x_label, y_label, color=None, color_label=None):
    if data.empty:
        st.info("No data for the current filters.")
        return

    chart_data, display_columns = chart_display_frame(data, [x, color])
    chart_x = display_columns.get(x, x)
    chart_color = display_columns.get(color, color)
    labels = {chart_x: x_label, y: y_label}
    if chart_color:
        labels[chart_color] = color_label or color or "Category"

    fig = px.line(
        chart_data,
        x=chart_x,
        y=y,
        color=chart_color,
        markers=True,
        labels=labels,
    )
    fig.update_layout(margin={"r": 8, "t": 8, "l": 8, "b": 8})
    st.plotly_chart(fig, use_container_width=True)


def aggregate_technology_counts(
    technology_counts: pd.DataFrame,
    category: str,
    intent: str,
    selected_years: list[int],
    limit: int,
) -> pd.DataFrame:
    if not selected_years:
        return pd.DataFrame(columns=["Technology", "Respondents"])

    selected = multiyear_top_technologies(
        technology_counts,
        category=category,
        intent=intent,
        limit=limit,
        years=selected_years,
    )
    if selected.empty:
        return pd.DataFrame(columns=["Technology", "Respondents"])

    return (
        selected.groupby("Technology", as_index=False)["Respondents"]
        .sum()
        .sort_values("Respondents", ascending=False)
        .head(limit)
    )


def render_overview_tab(filtered: pd.DataFrame):
    left, right = st.columns(2)
    with left:
        st.subheader("Respondents by country")
        render_bar_chart(
            top_counts(filtered, "Country", 20),
            "Country",
            "count",
            "Country",
            "Respondents",
        )
    with right:
        st.subheader("Remote work")
        render_bar_chart(
            top_counts(filtered, "RemoteWork", 10),
            "RemoteWork",
            "count",
            "Work format",
            "Respondents",
        )

    st.subheader("Education")
    render_bar_chart(
        top_counts(filtered, "EdLevel", 15),
        "EdLevel",
        "count",
        "Education level",
        "Respondents",
    )

    st.subheader("Age")
    render_bar_chart(
        top_counts(filtered, "Age", 12),
        "Age",
        "count",
        "Age group",
        "Respondents",
    )


def render_salary_tab(filtered: pd.DataFrame):
    st.subheader("Median salary by country")
    country_salary = median_compensation_by_group(filtered, "Country", 20)
    render_bar_chart(
        country_salary,
        "Country",
        "median_salary_usd",
        "Country",
        "Median salary, USD",
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Median salary by experience")
        experience_salary = median_compensation_by_group(filtered, "ProfessionalExperience", 20)
        render_bar_chart(
            experience_salary,
            "ProfessionalExperience",
            "median_salary_usd",
            "Professional experience, years",
            "Median salary, USD",
        )
    with right:
        st.subheader("Median salary by education")
        education_salary = median_compensation_by_group(filtered, "EdLevel", 12)
        render_bar_chart(
            education_salary,
            "EdLevel",
            "median_salary_usd",
            "Education level",
            "Median salary, USD",
        )

    st.subheader("Salary distribution")
    if "ConvertedCompYearly" not in filtered:
        st.info("No salary data for the current filters.")
        return

    salary_distribution = salary_distribution_frame(filtered["ConvertedCompYearly"])
    if salary_distribution.empty:
        st.info("No salary data for the current filters.")
        return

    render_bar_chart(
        salary_distribution,
        "salary_range",
        "count",
        "Salary range, USD",
        "Respondents",
    )


def render_technologies_tab(
    data: DashboardData,
    filtered_ids: set,
    selected_years: list[int],
):
    st.subheader("Language popularity")
    language_counts = aggregate_technology_counts(
        data.multiyear_technology_counts,
        category="language",
        intent="worked",
        selected_years=selected_years,
        limit=20,
    )
    render_bar_chart(
        language_counts,
        "Technology",
        "Respondents",
        "Programming language",
        "Respondents",
    )

    st.subheader("Worked vs wanted languages")
    worked_languages = aggregate_technology_counts(
        data.multiyear_technology_counts,
        category="language",
        intent="worked",
        selected_years=selected_years,
        limit=25,
    ).rename(columns={"Respondents": "worked_count"})
    wanted_languages = aggregate_technology_counts(
        data.multiyear_technology_counts,
        category="language",
        intent="wanted",
        selected_years=selected_years,
        limit=25,
    ).rename(columns={"Respondents": "wanted_count"})
    language_comparison = worked_languages.merge(wanted_languages, on="Technology", how="outer")
    language_comparison["worked_count"] = (
        pd.to_numeric(language_comparison["worked_count"], errors="coerce").fillna(0).astype(int)
    )
    language_comparison["wanted_count"] = (
        pd.to_numeric(language_comparison["wanted_count"], errors="coerce").fillna(0).astype(int)
    )
    language_comparison["want_gap"] = (
        language_comparison["wanted_count"] - language_comparison["worked_count"]
    )
    st.dataframe(language_comparison, use_container_width=True)

    st.subheader("Technology popularity")
    technology_counts = data.multiyear_technology_counts
    if technology_counts.empty or "Intent" not in technology_counts:
        st.info("No technology data for the current filters.")
        return

    worked_categories = (
        technology_counts.loc[technology_counts["Intent"] == "worked", "Category"].dropna().unique()
    )
    for category in sorted(worked_categories):
        category_data = aggregate_technology_counts(
            data.multiyear_technology_counts,
            category=category,
            intent="worked",
            selected_years=selected_years,
            limit=15,
        )
        st.caption(category)
        render_bar_chart(
            category_data,
            "Technology",
            "Respondents",
            "Technology",
            "Respondents",
        )

    st.subheader("Technology stack breadth")
    stack_width = technology_count_distribution(data.technology_tables, filtered_ids)
    render_bar_chart(
        stack_width,
        "technology_count",
        "respondents",
        "Technologies in stack",
        "Respondents",
    )


def render_ai_tab(filtered: pd.DataFrame):
    left, right = st.columns(2)
    with left:
        st.subheader("AI adoption")
        render_bar_chart(
            top_counts(filtered, "AIAdoption", 10),
            "AIAdoption",
            "count",
            "AI adoption status",
            "Respondents",
        )
    with right:
        st.subheader("AI sentiment")
        render_bar_chart(
            top_counts(filtered, "AISent", 10),
            "AISent",
            "count",
            "AI sentiment",
            "Respondents",
        )


def render_work_tab(filtered: pd.DataFrame):
    left, right = st.columns(2)
    with left:
        st.subheader("Developer type")
        render_bar_chart(
            top_counts(filtered, "DevType", 15),
            "DevType",
            "count",
            "Developer type",
            "Respondents",
        )
    with right:
        st.subheader("Job satisfaction")
        render_bar_chart(
            top_counts(filtered, "JobSatNormalized", 12),
            "JobSatNormalized",
            "count",
            "Job satisfaction score",
            "Respondents",
        )

    st.subheader("Remote work by country")
    remote_by_country = (
        filtered.dropna(subset=["Country", "RemoteWork"])
        .groupby(["Country", "RemoteWork"], as_index=False)
        .size()
        .sort_values("size", ascending=False)
        .head(40)
    )
    st.dataframe(remote_by_country, use_container_width=True)


def render_trends_tab(
    filtered_multiyear: pd.DataFrame,
    technology_counts: pd.DataFrame,
    selected_years: list[int],
):
    if not selected_years:
        st.info("Select at least one survey year.")
        return
    if filtered_multiyear.empty:
        st.info("No data for the current filters.")
        return
    if technology_counts.empty:
        st.info("Run multi-year EDA to generate trend data.")
        return

    left, right = st.columns(2)
    with left:
        st.subheader("Median salary by year")
        render_line_chart(
            multiyear_salary_trend(filtered_multiyear, selected_years),
            "SurveyYear",
            "median_salary_usd",
            "Survey year",
            "Median salary, USD",
        )
    with right:
        st.subheader("AI adoption by year")
        render_bar_chart(
            multiyear_ai_adoption_trend(filtered_multiyear, selected_years),
            "SurveyYear",
            "respondents",
            "Survey year",
            "Respondents",
            "AIAdoption",
            "AI adoption status",
        )

    st.subheader("Remote work by year")
    render_bar_chart(
        multiyear_remote_trend(filtered_multiyear, selected_years),
        "SurveyYear",
        "respondents",
        "Survey year",
        "Respondents",
        "RemoteWork",
        "Work format",
    )

    st.subheader("Top worked-with languages")
    language_trend = multiyear_top_technologies(
        technology_counts,
        category="language",
        intent="worked",
        limit=10,
        years=selected_years,
    )
    render_line_chart(
        language_trend,
        "SurveyYear",
        "Respondents",
        "Survey year",
        "Respondents",
        "Technology",
        "Technology",
    )


def render_world_map_tab(filtered_multiyear: pd.DataFrame, selected_years: list[int]):
    if not selected_years:
        st.info("Select at least one survey year.")
        return
    if filtered_multiyear.empty:
        st.info("No data for the current filters.")
        return

    st.caption(f"Aggregated salary data for selected years: {', '.join(map(str, selected_years))}")
    min_respondents = st.slider("Minimum salary respondents per country", 10, 300, 30, step=10)
    salary_map = salary_map_by_country(
        filtered_multiyear,
        years=None,
        min_respondents=min_respondents,
    )

    if salary_map.empty:
        st.info("No countries match the current respondent threshold.")
        return

    try:
        fig = px.choropleth(
            salary_map,
            locations="Country",
            locationmode="country names",
            color="median_salary_usd",
            hover_name="Country",
            hover_data={
                "median_salary_usd": ":,.0f",
                "respondents": ":,",
                "Country": False,
            },
            color_continuous_scale=SALARY_MAP_COLOR_SCALE,
            labels={
                "median_salary_usd": "Median salary, USD",
                "respondents": "Respondents",
            },
            projection="robinson",
        )
        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            coloraxis_colorbar_title="USD",
        )
        st.plotly_chart(fig, use_container_width=True)
    except (ValueError, TypeError, RuntimeError) as error:
        st.warning(f"Map rendering failed: {error}")

    st.subheader("Highest median salaries")
    st.dataframe(
        salary_map.head(25).assign(
            median_salary_usd=lambda frame: frame["median_salary_usd"].round(0).astype(int)
        ),
        use_container_width=True,
        hide_index=True,
    )


def main():
    st.title("Stack Overflow Developer Survey")
    st.markdown(
        '<p style="color:#16803c;font-weight:700;margin-top:-0.5rem;">'
        "Идея с шариками принадлежит "
        '<a href="https://github.com/Andekster" target="_blank" style="color:#16803c;">'
        "Andekster</a>"
        "</p>",
        unsafe_allow_html=True,
    )
    maybe_show_balloons()

    data = load_data()
    sidebar = render_sidebar(data.main, data.multiyear_core)
    filtered = apply_filters(data.main, sidebar)
    filtered_ids = (
        set(filtered["ResponseId"]) if data.multiyear_core.empty or 2024 in sidebar.years else set()
    )
    filtered_multiyear = apply_multiyear_filters(data.multiyear_core, sidebar)
    render_kpis(
        filtered,
        data.language,
        filtered_ids,
        filtered_multiyear,
        data.multiyear_technology_counts,
        sidebar.years,
        not data.multiyear_core.empty,
    )

    if sidebar.page == "Overview":
        render_overview_tab(filtered_multiyear)
    elif sidebar.page == "Salary":
        render_salary_tab(filtered_multiyear)
    elif sidebar.page == "World Map":
        render_world_map_tab(filtered_multiyear, sidebar.years)
    elif sidebar.page == "Technologies":
        render_technologies_tab(data, filtered_ids, sidebar.years)
    elif sidebar.page == "AI":
        render_ai_tab(filtered_multiyear)
    elif sidebar.page == "Work & Career":
        render_work_tab(filtered_multiyear)
    elif sidebar.page == "Trends":
        render_trends_tab(filtered_multiyear, data.multiyear_technology_counts, sidebar.years)


if __name__ == "__main__":
    main()
