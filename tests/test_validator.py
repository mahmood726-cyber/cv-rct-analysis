import pytest
from unittest.mock import MagicMock
from src.validator import DataValidator

@pytest.fixture
def mock_db_handler():
    return MagicMock()

def test_validate_nct_id():
    validator = DataValidator(MagicMock())
    assert validator.is_valid_nct_id("NCT01234567") is True
    assert validator.is_valid_nct_id("NCT123") is False
    assert validator.is_valid_nct_id("ABC01234567") is False

def test_validate_pmid():
    validator = DataValidator(MagicMock())
    assert validator.is_valid_pmid("12345678") is True
    assert validator.is_valid_pmid("abc") is False

def test_check_integrity(mock_db_handler):
    validator = DataValidator(mock_db_handler)
    
    # Mock some trial data
    trial1 = MagicMock(nct_id="NCT00000001", publications=[MagicMock()])
    trial2 = MagicMock(nct_id="INVALID_ID", publications=[])
    
    mock_session = MagicMock()
    mock_session.query.return_value.all.return_value = [trial1, trial2]
    mock_db_handler.Session.return_value = mock_session
    
    report = validator.check_integrity()
    
    assert report["total_trials"] == 2
    assert report["invalid_nct_ids"] == ["INVALID_ID"]
    assert report["trials_without_publications"] == ["INVALID_ID"]
