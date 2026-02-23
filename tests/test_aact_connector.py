import pytest
from src.aact_connector import AACTConnector

def test_generate_cv_query():
    connector = AACTConnector()
    query = connector.generate_cv_query(start_year=2015, end_year=2022)
    
    # Check for key requirements in the SQL string
    assert "Phase 3" in query
    assert "2015" in query
    assert "2022" in query
    assert "Interventional" in query # RCTs are interventional
    
    # Check for cardiovascular keywords/mesh terms (basic check)
    cv_terms = ["heart", "cardiovascular", "cardiac", "coronary", "arrhythmia"]
    assert any(term in query.lower() for term in cv_terms)

def test_generate_cv_query_date_bounds():
    connector = AACTConnector()
    query = connector.generate_cv_query(start_year=2018, end_year=2019)
    assert "2018" in query
    assert "2019" in query
    assert "2015" not in query
