import pandas as pd


def format_rate(rate):
    """Formats a decimal rate as a percentage string."""
    if rate is None:
        return "N/A"
    return f"{rate * 100:.1f}%"


def format_delay(days):
    """Formats a delay in days to a human-readable string."""
    if days is None:
        return "N/A"
    if days >= 365:
        return f"{days / 365:.1f} years"
    return f"{days} days"


def trials_to_dataframe(trials):
    """Converts a list of trial objects to a pandas DataFrame for display."""
    if not trials:
        return pd.DataFrame(columns=[
            "NCT ID", "Title", "Phase", "Domains",
            "Completion Date", "Status", "Pub Count"
        ])

    rows = []
    for t in trials:
        rows.append({
            "NCT ID": t.nct_id,
            "Title": t.title,
            "Phase": t.phase,
            "Domains": ", ".join(getattr(t, 'mapped_domains', []) or []),
            "Completion Date": t.completion_date,
            "Status": t.status,
            "Pub Count": len(t.publications),
        })
    return pd.DataFrame(rows)


def filter_by_date_range(trials, start_date, end_date):
    """
    Filters trials by completion_date within [start_date, end_date].
    Trials with no completion_date are excluded.
    None bounds mean no constraint on that side.
    """
    result = []
    for t in trials:
        if t.completion_date is None:
            continue
        if start_date is not None and t.completion_date < start_date:
            continue
        if end_date is not None and t.completion_date > end_date:
            continue
        result.append(t)
    return result


def filter_by_search_text(trials, query):
    """
    Filters trials where NCT ID, title, or conditions contain the query string.
    Case-insensitive. Empty/None query returns all trials.
    """
    if not query:
        return trials

    q = query.lower()
    result = []
    for t in trials:
        searchable = f"{t.nct_id} {t.title or ''} {t.conditions or ''}".lower()
        if q in searchable:
            result.append(t)
    return result


def filter_by_pub_status(trials, status):
    """
    Filters by publication status.
    status: "All", "Published Only", or "Unpublished Only"
    """
    if status == "Published Only":
        return [t for t in trials if len(t.publications) > 0]
    elif status == "Unpublished Only":
        return [t for t in trials if len(t.publications) == 0]
    return trials


def get_trial_detail(trial):
    """
    Extracts a detail dict from a trial object for the detail view.
    """
    pubs = []
    for p in trial.publications:
        pubs.append({
            "pmid": p.pmid,
            "title": p.title,
            "journal": p.journal,
            "publication_date": p.publication_date,
            "doi": p.doi,
        })

    return {
        "nct_id": trial.nct_id,
        "title": trial.title,
        "phase": trial.phase,
        "conditions": trial.conditions,
        "interventions": getattr(trial, 'interventions', None),
        "primary_endpoints": getattr(trial, 'primary_endpoints', None),
        "completion_date": trial.completion_date,
        "enrollment": getattr(trial, 'enrollment', None),
        "status": trial.status,
        "domains": getattr(trial, 'mapped_domains', []),
        "publications": pubs,
    }
