"""Smoke test: run app.py headlessly and check it renders without errors."""

from streamlit.testing.v1 import AppTest


def test_app_runs_and_shows_kpis():
    # The path is relative to this test file. Allow extra time for Plotly's first import.
    app = AppTest.from_file("../app.py", default_timeout=30).run()

    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$116,500"
    assert app.metric[1].value == "482"
