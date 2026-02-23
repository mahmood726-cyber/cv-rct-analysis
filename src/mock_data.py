import sys
import os
from datetime import date
from src.database import get_engine, init_db
from src.handlers import DBHandler

def populate_mock_data():
    # Use SQLite for the demonstration to ensure it works without a local PostgreSQL setup
    db_path = os.path.abspath("cv_rct_mock.db")
    url = f"sqlite:///{db_path}"
    
    print(f"Creating mock database at {url}...")
    engine = get_engine(url)
    init_db(engine)
    db_handler = DBHandler(engine)
    
    # Sample Trials
    mock_trials = [
        {
            "nct_id": "NCT01234567",
            "title": "Effect of New drug on Chronic Heart Failure",
            "phase": "Phase 3",
            "conditions": "Heart Failure",
            "status": "Completed",
            "completion_date": date(2018, 6, 15),
            "enrollment": 1200
        },
        {
            "nct_id": "NCT08765432",
            "title": "Ablation for Atrial Fibrillation (The AFIB Trial)",
            "phase": "Phase 3",
            "conditions": "Atrial Fibrillation",
            "status": "Completed",
            "completion_date": date(2019, 3, 10),
            "enrollment": 850
        },
        {
            "nct_id": "NCT05555555",
            "title": "Statin therapy in Coronary Artery Disease",
            "phase": "Phase 3",
            "conditions": "CAD, Myocardial Infarction",
            "status": "Completed",
            "completion_date": date(2020, 11, 22),
            "enrollment": 4500
        },
        {
            "nct_id": "NCT01111111",
            "title": "Novel Anticoagulant for Stroke Prevention",
            "phase": "Phase 3",
            "conditions": "Stroke, Hypertension",
            "status": "Completed",
            "completion_date": date(2017, 1, 5),
            "enrollment": 3200
        },
        {
            "nct_id": "NCT02222222",
            "title": "TAVI vs Surgery in Low-Risk Patients",
            "phase": "Phase 3",
            "conditions": "Aortic Stenosis",
            "status": "Completed",
            "completion_date": date(2021, 8, 30),
            "enrollment": 1000
        }
    ]
    
    # Sample Publications linked to NCT IDs
    mock_pubs = [
        {
            "pmid": "30123456",
            "title": "Primary Results of the Heart Failure Study",
            "journal": "NEJM",
            "publication_date": date(2019, 1, 20),
            "nct_match": "NCT01234567"
        },
        {
            "pmid": "31876543",
            "title": "Ablation vs Drugs for AFIB Outcomes",
            "journal": "Lancet",
            "publication_date": date(2019, 12, 1),
            "nct_match": "NCT08765432"
        },
        {
            "pmid": "33555555",
            "title": "Intensive Statin Therapy in CAD",
            "journal": "JAMA",
            "publication_date": date(2021, 5, 15),
            "nct_match": "NCT05555555"
        }
    ]
    
    for t_data in mock_trials:
        trial = db_handler.upsert_trial(t_data)
        
        # Check if we have pubs for this trial
        for p_data in mock_pubs:
            if p_data["nct_match"] == trial.nct_id:
                pub_entry = p_data.copy()
                del pub_entry["nct_match"]
                pub_entry["trial_id"] = trial.id
                db_handler.add_publication(pub_entry)
                
    print("Successfully populated mock data.")
    return url

if __name__ == "__main__":
    populate_mock_data()
