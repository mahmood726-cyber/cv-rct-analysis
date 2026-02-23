import pytest
from unittest.mock import MagicMock, patch
from src.extractor import CVRExtractor
from datetime import date

@pytest.fixture
def mock_db_handler():
    return MagicMock()

@pytest.fixture
def mock_aact_connector():
    return MagicMock()

def test_transform_aact_row(mock_db_handler, mock_aact_connector):
    extractor = CVRExtractor(mock_aact_connector, mock_db_handler)
    
    aact_row = {
        'nct_id': 'NCT00000001',
        'official_title': 'Big Heart Study',
        'phase': 'Phase 3',
        'completion_date': date(2020, 5, 20),
        'enrollment': 500,
        'overall_status': 'Completed'
    }
    
    transformed = extractor.transform_row(aact_row)
    
    assert transformed['nct_id'] == 'NCT00000001'
    assert transformed['title'] == 'Big Heart Study'
    assert transformed['enrollment'] == 500
    assert transformed['status'] == 'Completed'

def test_extract_and_store(mock_db_handler, mock_aact_connector):
    # Setup mocks — generate_cv_query now returns (sql, params)
    mock_aact_connector.generate_cv_query.return_value = ("SELECT ...", {})
    
    # Mocking the engine and connection
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn
    
    # Mock result proxy and its mappings
    mock_result = MagicMock()
    mock_mappings = MagicMock()
    mock_mappings.all.return_value = [
        {'nct_id': 'NCT1', 'official_title': 'T1', 'phase': 'Phase 3', 'completion_date': None, 'enrollment': 10, 'overall_status': 'C'}
    ]
    mock_result.mappings.return_value = mock_mappings
    mock_conn.execute.return_value = mock_result
    
    extractor = CVRExtractor(mock_aact_connector, mock_db_handler)
    
    # Patch create_engine to return our mock_engine
    with patch('src.extractor.create_engine', return_value=mock_engine):
        extractor.extract_phase_3_trials(start_year=2015, end_year=2022)
    
    # Verify DB handler was called to upsert
    assert mock_db_handler.upsert_trial.called
    call_args = mock_db_handler.upsert_trial.call_args[0][0]
    assert call_args['nct_id'] == 'NCT1'
