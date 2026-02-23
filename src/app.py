import streamlit as st
import pandas as pd
from datetime import date
from src.database import get_engine, init_db
from src.handlers import DBHandler
from src.stats_engine import StatsEngine
from src.domain_mapper import DomainMapper
from src.app_utils import (
    format_rate,
    format_delay,
    trials_to_dataframe,
    filter_by_date_range,
    filter_by_search_text,
    filter_by_pub_status,
    get_trial_detail,
)


@st.cache_resource
def get_db_engine():
    engine = get_engine()
    init_db(engine)
    return engine


def load_data(engine):
    db_handler = DBHandler(engine)
    session = db_handler.Session()
    try:
        from src.models import Trial
        trials = session.query(Trial).all()
        # Eagerly load publications to avoid lazy-load issues after session close
        for t in trials:
            _ = t.publications
        return trials
    finally:
        session.close()


def main():
    st.set_page_config(page_title="CV-RCT Analysis Dashboard", layout="wide")

    st.title("Cardiovascular RCT Analysis Dashboard")
    st.markdown("Exploring Phase III Trials (2015-2024) across CT.gov, PubMed, and OpenAlex")

    # Load data
    engine = get_db_engine()
    trials = load_data(engine)

    if not trials:
        st.warning("No trials found in the database. Please run the extraction pipeline first.")
        return

    mapper = DomainMapper()
    stats_engine = StatsEngine(DBHandler(engine), mapper)

    # Pre-process domains
    for trial in trials:
        trial.mapped_domains = mapper.categorize_trial(trial)

    # ── Sidebar Filters ──────────────────────────────
    st.sidebar.header("Filters")

    # 1. Text search
    search_query = st.sidebar.text_input("Search (NCT ID, title, condition)", "")

    # 2. Disease area filter
    all_domains = set()
    for t in trials:
        all_domains.update(t.mapped_domains)

    selected_domains = st.sidebar.multiselect(
        "Cardiovascular Sub-Domain",
        options=sorted(list(all_domains)),
        default=[],
    )

    # 3. Publication status filter
    pub_filter = st.sidebar.radio(
        "Publication Status",
        options=["All", "Published Only", "Unpublished Only"],
    )

    # 4. Date range filter
    completion_dates = [t.completion_date for t in trials if t.completion_date]
    if completion_dates:
        min_date = min(completion_dates)
        max_date = max(completion_dates)
    else:
        min_date = date(2015, 1, 1)
        max_date = date.today()

    st.sidebar.subheader("Completion Date Range")
    date_start = st.sidebar.date_input("From", value=min_date, min_value=min_date, max_value=max_date)
    date_end = st.sidebar.date_input("To", value=max_date, min_value=min_date, max_value=max_date)

    # ── Apply Filters ────────────────────────────────
    filtered = trials

    # Text search
    filtered = filter_by_search_text(filtered, search_query)

    # Domain filter
    if selected_domains:
        filtered = [
            t for t in filtered
            if any(d in selected_domains for d in t.mapped_domains)
        ]

    # Publication status
    filtered = filter_by_pub_status(filtered, pub_filter)

    # Date range
    filtered = filter_by_date_range(filtered, date_start, date_end)

    # ── Summary Metrics ──────────────────────────────
    summary = stats_engine.summary_stats(filtered)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Trials (Filtered)", summary["total_trials"])
    col2.metric("Published", summary["published_count"])
    col3.metric("Publication Rate", format_rate(summary["publication_rate"]))
    col4.metric("Median Delay", format_delay(summary["median_time_to_pub"]))

    st.divider()

    # ── Per-Domain Breakdown ─────────────────────────
    if filtered:
        domain_stats = stats_engine.domain_summary(filtered)
        if domain_stats:
            st.subheader("Statistics by CV Domain")
            domain_rows = []
            for domain, ds in sorted(domain_stats.items()):
                domain_rows.append({
                    "Domain": domain,
                    "Trials": ds["total_trials"],
                    "Published": ds["published_count"],
                    "Pub Rate": format_rate(ds["publication_rate"]),
                    "Median Delay": format_delay(ds["median_time_to_pub"]),
                })
            st.dataframe(pd.DataFrame(domain_rows), use_container_width=True, hide_index=True)

        st.divider()

    # ── Trial Table ──────────────────────────────────
    st.subheader(f"Trial List ({len(filtered)} results)")

    if filtered:
        df = trials_to_dataframe(filtered)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # ── Trial Detail View ────────────────────────
        st.divider()
        st.subheader("Trial Details")

        trial_options = {f"{t.nct_id} — {(t.title or 'Untitled')[:60]}": t for t in filtered}
        selected_label = st.selectbox("Select a trial to view details", options=list(trial_options.keys()))

        if selected_label:
            selected_trial = trial_options[selected_label]
            detail = get_trial_detail(selected_trial)

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**NCT ID:** {detail['nct_id']}")
                st.markdown(f"**Phase:** {detail['phase']}")
                st.markdown(f"**Status:** {detail['status']}")
                st.markdown(f"**Enrollment:** {detail['enrollment'] or 'N/A'}")
            with col_b:
                st.markdown(f"**Conditions:** {detail['conditions'] or 'N/A'}")
                st.markdown(f"**Interventions:** {detail['interventions'] or 'N/A'}")
                st.markdown(f"**Primary Endpoints:** {detail['primary_endpoints'] or 'N/A'}")
                st.markdown(f"**Completion:** {detail['completion_date'] or 'N/A'}")

            if detail["publications"]:
                st.markdown("**Publications:**")
                for i, pub in enumerate(detail["publications"], 1):
                    with st.expander(f"Publication {i}: {pub['title'] or 'Untitled'}"):
                        st.markdown(f"- **Journal:** {pub['journal'] or 'N/A'}")
                        st.markdown(f"- **PMID:** {pub['pmid'] or 'N/A'}")
                        st.markdown(f"- **DOI:** {pub['doi'] or 'N/A'}")
                        st.markdown(f"- **Date:** {pub['publication_date'] or 'N/A'}")
            else:
                st.info("No publications linked to this trial.")
    else:
        st.info("No trials match the selected filters.")


if __name__ == "__main__":
    main()
