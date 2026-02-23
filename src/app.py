"""Streamlit dashboard entry point for CV-RCT analysis."""
import streamlit as st
import pandas as pd
import logging
from sqlalchemy.orm import joinedload
from src.database import get_engine, init_db
from src.handlers import DBHandler
from src.stats import CVStatsCalculator
from src.domain_mapper import DomainMapper
from src.app_utils import format_rate

def load_data():
    # Try SQLite mock DB first for this session to ensure visibility
    import os
    mock_db = "cv_rct_mock.db"
    
    engines_to_try = []
    if os.path.exists(mock_db):
        engines_to_try.append(f"sqlite:///{os.path.abspath(mock_db)}")
    engines_to_try.append(get_engine().url)

    for url in engines_to_try:
        try:
            engine = get_engine(url)
            db_handler = DBHandler(engine)
            session = db_handler.Session()
            try:
                from src.models import Trial
                trials = session.query(Trial).options(
                    joinedload(Trial.publications)
                ).all()
                if trials:
                    return trials
            finally:
                session.close()
        except Exception:
            continue
    return []

def main():
    st.set_page_config(page_title="CV-RCT Analysis Dashboard", layout="wide")
    
    st.title("Cardiovascular RCT Analysis Dashboard")
    st.markdown("Exploring Phase III Trials (2015-2022) across CT.gov, PubMed, and OpenAlex")
    
    # Load data
    trials = load_data()
    
    if not trials:
        st.warning("No trials found in the database or database connection failed. Please ensure the extraction pipeline has been run.")
        st.info("Note: Default database is 'postgresql://postgres:postgres@localhost:5432/cv_rct_db'. Update DATABASE_URL if needed.")
        return

    mapper = DomainMapper()
    
    # Pre-process domains for filtering
    for trial in trials:
        trial.mapped_domains = mapper.categorize_trial(trial)

    # Sidebar for filters
    st.sidebar.header("Filters")
    
    # 1. Disease Area Filter
    all_domains = set()
    for t in trials:
        all_domains.update(t.mapped_domains)
    
    selected_domains = st.sidebar.multiselect(
        "Cardiovascular Sub-Domain",
        options=sorted(list(all_domains)),
        default=[]
    )
    
    # 2. Publication Status Filter
    pub_filter = st.sidebar.radio(
        "Publication Status",
        options=["All", "Published Only", "Unpublished Only"]
    )
    
    # Filter Logic
    filtered_trials = trials
    
    if selected_domains:
        filtered_trials = [
            t for t in filtered_trials 
            if any(domain in selected_domains for domain in t.mapped_domains)
        ]
        
    if pub_filter == "Published Only":
        filtered_trials = [t for t in filtered_trials if len(t.publications) > 0]
    elif pub_filter == "Unpublished Only":
        filtered_trials = [t for t in filtered_trials if len(t.publications) == 0]

    # Summary Statistics for filtered data
    calc = CVStatsCalculator()
    summary = calc.get_summary_report(filtered_trials)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Trials (Filtered)", summary["total_trials"])
    col2.metric("Published", summary["published_count"])
    col3.metric("Publication Rate", format_rate(summary["publication_rate"]))
    col4.metric("Median Delay (Days)", f"{summary['median_delay_days'] or 'N/A'}")

    st.divider()
    
    # Detailed Table view
    st.subheader(f"Trial List ({len(filtered_trials)} results)")
    
    if filtered_trials:
        trial_list = []
        for t in filtered_trials:
            trial_list.append({
                "NCT ID": t.nct_id,
                "Title": t.title,
                "Phase": t.phase,
                "Domains": ", ".join(t.mapped_domains),
                "Completion Date": t.completion_date,
                "Status": t.status,
                "Pub Count": len(t.publications)
            })
        
        df = pd.DataFrame(trial_list)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No trials match the selected filters.")

if __name__ == "__main__":
    main()
