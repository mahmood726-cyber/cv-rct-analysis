import pytest
from src.database import get_engine, init_db, get_session
from src.models import Base, Trial
from sqlalchemy.orm import Session

def test_database_init_and_session():
    # Use in-memory SQLite for testing
    url = "sqlite:///:memory:"
    engine = get_engine(url)
    init_db(engine)
    
    session = get_session(engine)
    assert isinstance(session, Session)
    
    # Verify we can use the session
    trial = Trial(nct_id='NCT99999999', title='DB Test')
    session.add(trial)
    session.commit()
    
    retrieved = session.query(Trial).first()
    assert retrieved.nct_id == 'NCT99999999'
    session.close()
