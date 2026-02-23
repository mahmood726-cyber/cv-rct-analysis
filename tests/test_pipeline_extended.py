import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
from src.pipeline import CVPipeline, main

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

def test_pipeline_main_entry_point():
    # Mocking all dependencies within the main function
    with patch('src.database.get_engine'), \
         patch('src.database.init_db'), \
         patch('src.handlers.DBHandler'), \
         patch('src.aact_connector.AACTConnector'), \
         patch('src.extractor.CVRExtractor'), \
         patch('src.pubmed_client.PubMedClient'), \
         patch('src.openalex_client.OpenAlexClient'), \
         patch('src.reconciler.Reconciler'), \
         patch('asyncio.run'), \
         patch('argparse.ArgumentParser.parse_args') as mock_args:
        
        mock_args.return_value = MagicMock(start=2018, end=2019)
        
        # Simulate running the script
        with patch.object(sys, 'argv', ['pipeline.py', '--start', '2018', '--end', '2019']):
            main()

@pytest.mark.asyncio
async def test_run_pipeline_error_handling(mock_extractor, mock_reconciler, mock_db_handler):
    pipeline = CVPipeline(mock_extractor, mock_reconciler, mock_db_handler)
    
    # Simulate extraction failure
    mock_extractor.extract_phase_3_trials.side_effect = Exception("AACT Error")
    
    await pipeline.run(start_year=2020, end_year=2020)
    
    # Reconciler should NOT be called if extraction fails
    assert not mock_reconciler.reconcile_trial.called

@pytest.mark.asyncio
async def test_run_pipeline_reconciliation_error(mock_extractor, mock_reconciler, mock_db_handler):
    pipeline = CVPipeline(mock_extractor, mock_reconciler, mock_db_handler)
    
    # Mock trials returned from local DB
    trial1 = MagicMock(nct_id="NCT1")
    mock_session = MagicMock()
    mock_session.query.return_value.all.return_value = [trial1]
    mock_db_handler.Session.return_value = mock_session
    
    # Simulate reconciliation failure for a single trial
    mock_reconciler.reconcile_trial.side_effect = Exception("API Error")
    
    await pipeline.run(start_year=2020, end_year=2020)
    
    # Verify reconciliation was attempted
    assert mock_reconciler.reconcile_trial.called
