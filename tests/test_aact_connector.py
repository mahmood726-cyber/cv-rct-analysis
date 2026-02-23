import pytest
from src.aact_connector import AACTConnector

def test_generate_cv_query():
    connector = AACTConnector()
    query, params = connector.generate_cv_query(start_year=2015, end_year=2022)
    
    # Check for key requirements in the SQL string
    assert "studies.phase = 'Phase 3'" in query
    assert "studies.completion_date BETWEEN" in query
    assert "studies.study_type = 'Interventional'" in query # RCTs are interventional
    
    # Check params
    assert params["start_date"] == "2015-01-01"
    assert params["end_date"] == "2022-12-31"

def test_generate_cv_query_date_bounds():
    connector = AACTConnector()
    query, params = connector.generate_cv_query(start_year=2018, end_year=2019)
    assert params["start_date"] == "2018-01-01"
    assert params["end_date"] == "2019-12-31"
