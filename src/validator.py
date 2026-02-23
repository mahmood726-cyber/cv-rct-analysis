import re
import logging
from src.models import Trial

class DataValidator:
    def __init__(self, db_handler):
        self.db_handler = db_handler
        self.logger = logging.getLogger(__name__)

    def is_valid_nct_id(self, nct_id):
        """
        Validates the NCT ID format (NCT followed by 8 digits).
        """
        if not nct_id:
            return False
        return bool(re.match(r'^NCT\d{8}$', nct_id))

    def is_valid_pmid(self, pmid):
        """
        Validates that the PMID is numeric.
        """
        if not pmid:
            return False
        return bool(re.match(r'^\d+$', pmid))

    def check_integrity(self):
        """
        Checks the integrity of the trials in the database and returns a report.
        """
        self.logger.info("Running data integrity checks...")
        
        report = {
            "total_trials": 0,
            "invalid_nct_ids": [],
            "trials_without_publications": [],
            "issues_found": False
        }
        
        session = self.db_handler.Session()
        try:
            trials = session.query(Trial).all()
            report["total_trials"] = len(trials)
            
            for trial in trials:
                if not self.is_valid_nct_id(trial.nct_id):
                    report["invalid_nct_ids"].append(trial.nct_id)
                    report["issues_found"] = True
                
                if not trial.publications:
                    report["trials_without_publications"].append(trial.nct_id)
                    # We don't mark issues_found just for missing pubs, as some trials might genuinely not have them
            
            return report
        finally:
            session.close()
