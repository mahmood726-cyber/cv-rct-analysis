import streamlit as st
import pandas as pd
from src.database import get_engine, init_db
from src.handlers import DBHandler
from src.stats import CVStatsCalculator
from src.domain_mapper import DomainMapper
from src.app_utils import format_rate

def load_data():
    engine = get_engine()
    db_handler = DBHandler(engine)
    session = db_handler.Session()
    try:
        from src.models import Trial
        trials = session.query(Trial).all()
        return trials
    finally:
        session.close()

def main():
    st.set_page_config(page_title="CV-RCT Analysis Dashboard", layout="wide")
    
    st.title("Cardiovascular RCT Analysis Dashboard")
    st.markdown("Exploring Phase III Trials (2015-2022) across CT.gov, PubMed, and OpenAlex")
    
    # Load data
    trials = load_data()
    
    if not trials:
        st.warning("No trials found in the database. Please run the extraction pipeline first.")
        return

    # Sidebar for filters
    st.sidebar.header("Filters")
    
    # Summary Statistics
    calc = CVStatsCalculator()
    summary = calc.get_summary_report(trials)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Trials", summary["total_trials"])
    col2.metric("Published Trials", summary["published_count"])
    col3.metric("Publication Rate", format_rate(summary["publication_rate"]))
    col4.metric("Median Delay (Days)", f"{summary['median_delay_days'] or 'N/A'}")

    st.divider()
    st.subheader("Recent Trials")
    
    # Simple table view
    trial_list = []
    for t in trials[:10]: # Show first 10 for now
        trial_list.append({
            "NCT ID": t.nct_id,
            "Title": t.title,
            "Phase": t.phase,
            "Completion Date": t.completion_date,
            "Status": t.status
        })
    
    st.table(pd.DataFrame(trial_list))

if __name__ == "__main__":
    main()
