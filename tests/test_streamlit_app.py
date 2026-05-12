from streamlit.testing.v1 import AppTest


def test_streamlit_app_runs_without_runtime_errors(monkeypatch):
    monkeypatch.setenv("STACKOVERFLOW_ANALYTICS_TEST_MODE", "1")

    app = AppTest.from_file("app/streamlit_app.py")
    app.run(timeout=30)

    assert not app.exception
