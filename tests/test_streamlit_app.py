from streamlit.testing.v1 import AppTest

PAGES = [
    "Overview",
    "Salary",
    "World Map",
    "Technologies",
    "AI",
    "Work & Career",
    "Trends",
]


def test_streamlit_app_runs_without_runtime_errors(monkeypatch):
    monkeypatch.setenv("STACKOVERFLOW_ANALYTICS_TEST_MODE", "1")

    app = AppTest.from_file("app/streamlit_app.py")
    app.run(timeout=30)

    assert not app.exception


def test_streamlit_app_pages_run_without_runtime_errors(monkeypatch):
    monkeypatch.setenv("STACKOVERFLOW_ANALYTICS_TEST_MODE", "1")

    for page in PAGES:
        app = AppTest.from_file("app/streamlit_app.py")
        app.run(timeout=30)
        app.radio[0].set_value(page)
        app.run(timeout=30)

        assert not app.exception


def test_streamlit_app_handles_empty_year_selection(monkeypatch):
    monkeypatch.setenv("STACKOVERFLOW_ANALYTICS_TEST_MODE", "1")

    for page in ["World Map", "Trends"]:
        app = AppTest.from_file("app/streamlit_app.py")
        app.run(timeout=30)
        app.radio[0].set_value(page)
        app.multiselect[0].set_value([])
        app.run(timeout=30)

        assert not app.exception


def test_streamlit_app_handles_experience_filter(monkeypatch):
    monkeypatch.setenv("STACKOVERFLOW_ANALYTICS_TEST_MODE", "1")

    app = AppTest.from_file("app/streamlit_app.py")
    app.run(timeout=30)
    app.slider[0].set_range(0, 10)
    app.run(timeout=30)

    assert not app.exception


def test_streamlit_app_handles_country_respondent_threshold(monkeypatch):
    monkeypatch.setenv("STACKOVERFLOW_ANALYTICS_TEST_MODE", "1")

    app = AppTest.from_file("app/streamlit_app.py")
    app.run(timeout=30)
    app.number_input[0].set_value(2)
    app.run(timeout=30)

    assert not app.exception
