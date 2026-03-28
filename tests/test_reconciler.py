import pytest
from unittest.mock import AsyncMock, MagicMock
from src.reconciler import Reconciler

@pytest.fixture
def mock_pubmed():
    return AsyncMock()

@pytest.fixture
def mock_openalex():
    client = MagicMock()
    client.get_work_by_pmid = AsyncMock()
    return client

@pytest.fixture
def mock_db_handler():
    return MagicMock()

@pytest.mark.asyncio
async def test_reconcile_trial(mock_pubmed, mock_openalex, mock_db_handler):
    reconciler = Reconciler(mock_pubmed, mock_openalex, mock_db_handler)

    trial = MagicMock()
    trial.id = 1
    trial.nct_id = "NCT01234567"

    mock_pubmed.search_nct_id.return_value = ["12345"]
    mock_db_handler.get_publications_for_trial.return_value = []
    mock_openalex.get_work_by_pmid.return_value = {
        "id": "https://openalex.org/W1",
        "title": "Pub Title",
        "doi": "https://doi.org/10.1",
        "publication_date": "2021-01-01"
    }

    await reconciler.reconcile_trial(trial)

    # Check if DB handler was called to add publication
    assert mock_db_handler.add_publication.called
    pub_data = mock_db_handler.add_publication.call_args[0][0]
    assert pub_data["pmid"] == "12345"
    assert pub_data["trial_id"] == 1
    assert pub_data["openalex_id"] == "https://openalex.org/W1"


@pytest.mark.asyncio
async def test_reconcile_trial_skips_existing_pmid(mock_pubmed, mock_openalex, mock_db_handler):
    """Existing PMID should be skipped without calling OpenAlex or add_publication."""
    reconciler = Reconciler(mock_pubmed, mock_openalex, mock_db_handler)

    trial = MagicMock()
    trial.id = 1
    trial.nct_id = "NCT01234567"

    mock_pubmed.search_nct_id.return_value = ["12345", "67890"]

    # "12345" already exists in DB
    existing_pub = MagicMock()
    existing_pub.pmid = "12345"
    mock_db_handler.get_publications_for_trial.return_value = [existing_pub]

    mock_openalex.get_work_by_pmid.return_value = {
        "id": "https://openalex.org/W2",
        "title": "New Pub",
        "doi": "https://doi.org/10.2",
        "publication_date": "2022-06-01"
    }

    await reconciler.reconcile_trial(trial)

    # OpenAlex should only be called for the NEW pmid "67890"
    mock_openalex.get_work_by_pmid.assert_called_once_with("67890")
    # Only one publication should be added (the new one)
    assert mock_db_handler.add_publication.call_count == 1
    pub_data = mock_db_handler.add_publication.call_args[0][0]
    assert pub_data["pmid"] == "67890"
