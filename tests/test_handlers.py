import pytest
from sqlalchemy import create_engine
from src.models import Base, Trial, Publication
from src.handlers import DBHandler
from datetime import date

@pytest.fixture
def db_handler():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    return DBHandler(engine)

def test_add_trial(db_handler):
    trial_data = {
        'nct_id': 'NCT00000001',
        'title': 'Handler Test Trial',
        'phase': 'Phase 3',
        'completion_date': date(2022, 1, 1)
    }
    trial = db_handler.add_trial(trial_data)
    assert trial.id is not None
    
    retrieved = db_handler.get_trial_by_nct_id('NCT00000001')
    assert retrieved.title == 'Handler Test Trial'

def test_add_publication(db_handler):
    trial = db_handler.add_trial({'nct_id': 'NCT00000002', 'title': 'Trial for Pub'})
    pub_data = {
        'pmid': '88888888',
        'title': 'Handler Test Pub',
        'trial_id': trial.id
    }
    pub = db_handler.add_publication(pub_data)
    assert pub.id is not None
    
    retrieved = db_handler.get_publications_for_trial(trial.id)
    assert len(retrieved) == 1
    assert retrieved[0].pmid == '88888888'

def test_upsert_trial(db_handler):
    # Initial add
    db_handler.add_trial({'nct_id': 'NCT00000003', 'title': 'Original Title'})
    
    # Update via upsert
    updated_data = {'nct_id': 'NCT00000003', 'title': 'Updated Title'}
    db_handler.upsert_trial(updated_data)
    
    retrieved = db_handler.get_trial_by_nct_id('NCT00000003')
    assert retrieved.title == 'Updated Title'
