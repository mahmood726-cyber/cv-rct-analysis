from sqlalchemy.orm import sessionmaker
from src.models import Trial, Publication

class DBHandler:
    def __init__(self, engine):
        self.Session = sessionmaker(bind=engine)

    def add_trial(self, trial_data):
        session = self.Session()
        try:
            trial = Trial(**trial_data)
            session.add(trial)
            session.commit()
            session.refresh(trial)
            return trial
        finally:
            session.close()

    def get_trial_by_nct_id(self, nct_id):
        session = self.Session()
        try:
            return session.query(Trial).filter_by(nct_id=nct_id).first()
        finally:
            session.close()

    def add_publication(self, pub_data):
        session = self.Session()
        try:
            pub = Publication(**pub_data)
            session.add(pub)
            session.commit()
            session.refresh(pub)
            return pub
        finally:
            session.close()

    def get_publications_for_trial(self, trial_id):
        session = self.Session()
        try:
            return session.query(Publication).filter_by(trial_id=trial_id).all()
        finally:
            session.close()

    def upsert_trial(self, trial_data):
        session = self.Session()
        try:
            nct_id = trial_data.get('nct_id')
            existing = session.query(Trial).filter_by(nct_id=nct_id).first()
            if existing:
                for key, value in trial_data.items():
                    setattr(existing, key, value)
            else:
                existing = Trial(**trial_data)
                session.add(existing)
            session.commit()
            session.refresh(existing)
            return existing
        finally:
            session.close()
