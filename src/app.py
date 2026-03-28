"""Streamlit dashboard entry point for CV-RCT analysis."""
import os
import logging
import random
import streamlit as st
import pandas as pd
from sqlalchemy.orm import joinedload
from src.database import get_engine
from src.handlers import DBHandler
from src.stats import CVStatsCalculator
from src.domain_mapper import DomainMapper
from src.models import Trial
from src.app_utils import format_rate

logger = logging.getLogger(__name__)


def load_data():
    """Load trials from SQLite mock DB (if present) or configured PostgreSQL."""
    mock_db = "cv_rct_mock.db"

    urls_to_try = []
    if os.path.exists(mock_db):
        urls_to_try.append(f"sqlite:///{os.path.abspath(mock_db)}")
    urls_to_try.append(os.getenv("DATABASE_URL",
                                  "postgresql://postgres:postgres@localhost:5432/cv_rct_db"))

    for url in urls_to_try:
        engine = None
        try:
            engine = get_engine(url)
            db_handler = DBHandler(engine)
            session = db_handler.Session()
            try:
                trials = session.query(Trial).options(
                    joinedload(Trial.publications)
                ).all()
                if trials:
                    return trials
            finally:
                session.close()
        except Exception as exc:
            logger.debug("Could not load from %s: %s", url, exc)
            continue
        finally:
            if engine is not None:
                engine.dispose()
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

    # Export Section (must be after filtering)
    st.sidebar.divider()
    st.sidebar.subheader("Export")
    
    if filtered_trials:
        export_data = []
        for t in filtered_trials:
            export_data.append({
                "nct_id": t.nct_id,
                "title": t.title,
                "status": t.status,
                "domains": ", ".join(t.mapped_domains),
                "completion_date": str(t.completion_date),
                "publication_count": len(t.publications)
            })
        export_df = pd.DataFrame(export_data)
        csv = export_df.to_csv(index=False).encode('utf-8')
        
        st.sidebar.download_button(
            label="Download Filtered Results (CSV)",
            data=csv,
            file_name='cv_rct_export.csv',
            mime='text/csv',
        )

    # Summary Statistics for filtered data
    calc = CVStatsCalculator()
    summary = calc.get_summary_report(filtered_trials)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Trials (Filtered)", summary["total_trials"])
    col2.metric("Published", summary["published_count"])
    col3.metric("Publication Rate", format_rate(summary["publication_rate"]))
    median = summary['median_delay_days']
    col4.metric("Median Delay (Days)", "N/A" if median is None else str(median))

    st.divider()
    
    # Visualizations
    st.subheader("Meta-Analysis Visualizations")
    from src.viz import VizGenerator
    viz = VizGenerator()
    
    st.caption("Note: Effect sizes below are **simulated** for demonstration purposes. "
               "Actual clinical outcomes require separate extraction from trial publications.")

    viz_data = []
    for i, t in enumerate(filtered_trials):
        random.seed(t.nct_id)
        es = random.uniform(-0.5, 0.2)
        viz_data.append({
            "name": t.nct_id,
            "effect_size": es,
            "lower_ci": es - 0.15,
            "upper_ci": es + 0.15,
            "enrollment": t.enrollment or 100
        })
    
    if viz_data:
        vcol1, vcol2 = st.columns(2)
        with vcol1:
            forest = viz.create_forest_plot(viz_data)
            st.plotly_chart(forest, use_container_width=True)
        with vcol2:
            funnel = viz.create_funnel_plot(viz_data)
            st.plotly_chart(funnel, use_container_width=True)
    else:
        st.info("No data available for visualizations.")

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
