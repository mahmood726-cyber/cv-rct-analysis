import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.pipeline import CVPipeline

@pytest.fixture
def mock_extractor():
    return MagicMock()

@pytest.fixture
def mock_reconciler():
    client = MagicMock()
    client.reconcile_trial = AsyncMock()
    return client

@pytest.fixture
def mock_db_handler():
    return MagicMock()

@pytest.mark.asyncio
async def test_run_pipeline(mock_extractor, mock_reconciler, mock_db_handler):
    pipeline = CVPipeline(mock_extractor, mock_reconciler, mock_db_handler)
    
    # Mock trials returned from local DB after extraction
    trial1 = MagicMock(nct_id="NCT1")
    trial2 = MagicMock(nct_id="NCT2")
    
    # Mock database session return
    mock_session = MagicMock()
    mock_session.query.return_value.all.return_value = [trial1, trial2]
    mock_db_handler.Session.return_value = mock_session
    
    await pipeline.run(start_year=2020, end_year=2020)
    
    # Verify extraction was called
    assert mock_extractor.extract_phase_3_trials.called
    mock_extractor.extract_phase_3_trials.assert_called_with(2020, 2020)
    
    # Verify reconciliation was called for each trial
    assert mock_reconciler.reconcile_trial.call_count == 2
