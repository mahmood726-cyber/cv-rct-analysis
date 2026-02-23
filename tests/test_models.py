import pytest
from src.models import Base, Trial, Publication
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def test_trial_model_creation():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    trial = Trial(nct_id='NCT01234567', title='Test Trial', phase='Phase 3', conditions='Heart Failure')
    session.add(trial)
    session.commit()
    
    retrieved = session.query(Trial).filter_by(nct_id='NCT01234567').first()
    assert retrieved.title == 'Test Trial'
    assert retrieved.phase == 'Phase 3'

def test_publication_model_creation():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    trial = Trial(nct_id='NCT01234567', title='Test Trial')
    session.add(trial)
    session.commit()
    
    pub = Publication(pmid='12345678', title='Test Publication', trial_id=trial.id)
    session.add(pub)
    session.commit()
    
    retrieved = session.query(Publication).filter_by(pmid='12345678').first()
    assert retrieved.trial.nct_id == 'NCT01234567'
