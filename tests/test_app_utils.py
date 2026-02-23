import pytest
from datetime import date
from src.app_utils import (
    format_rate,
    format_delay,
    trials_to_dataframe,
    filter_by_date_range,
    filter_by_search_text,
    filter_by_pub_status,
    get_trial_detail,
)


def _make_pub(pub_date, pmid="12345", title="Pub Title", journal="J Cardiol", doi="10.1000/test"):
    return type('obj', (object,), {
        'publication_date': pub_date,
        'pmid': pmid,
        'title': title,
        'journal': journal,
        'doi': doi,
    })


def _make_trial(nct_id, conditions, title, completion_date, publications=None,
                phase="Phase 3", status="Completed", enrollment=100):
    trial = type('obj', (object,), {
        'nct_id': nct_id,
        'conditions': conditions,
        'title': title,
        'completion_date': completion_date,
        'publications': publications or [],
        'phase': phase,
        'status': status,
        'enrollment': enrollment,
        'interventions': 'Drug A',
        'primary_endpoints': 'Overall survival',
        'mapped_domains': [],
    })
    return trial


# --- format_rate ---

def test_format_rate():
    assert format_rate(0.5) == "50.0%"
    assert format_rate(1.0) == "100.0%"
    assert format_rate(0.0) == "0.0%"
    assert format_rate(0.12345) == "12.3%"
    assert format_rate(None) == "N/A"


# --- format_delay ---

def test_format_delay():
    assert format_delay(365) == "1.0 years"
    assert format_delay(180) == "180 days"
    assert format_delay(730) == "2.0 years"
    assert format_delay(None) == "N/A"
    assert format_delay(0) == "0 days"


# --- trials_to_dataframe ---

def test_trials_to_dataframe():
    trials = [
        _make_trial("NCT001", "Heart Failure", "HF Study", date(2020, 6, 1),
                     [_make_pub(date(2021, 1, 1))]),
        _make_trial("NCT002", "CAD", "CAD Study", date(2019, 3, 15), []),
    ]
    trials[0].mapped_domains = ["Heart Failure"]
    trials[1].mapped_domains = ["Coronary Artery Disease"]

    df = trials_to_dataframe(trials)

    assert len(df) == 2
    assert list(df.columns) == [
        "NCT ID", "Title", "Phase", "Domains",
        "Completion Date", "Status", "Pub Count"
    ]
    assert df.iloc[0]["NCT ID"] == "NCT001"
    assert df.iloc[0]["Pub Count"] == 1
    assert df.iloc[1]["Pub Count"] == 0
    assert df.iloc[0]["Domains"] == "Heart Failure"


def test_trials_to_dataframe_empty():
    df = trials_to_dataframe([])
    assert len(df) == 0


# --- filter_by_date_range ---

def test_filter_by_date_range():
    trials = [
        _make_trial("NCT001", "HF", "A", date(2018, 6, 1)),
        _make_trial("NCT002", "HF", "B", date(2020, 1, 15)),
        _make_trial("NCT003", "HF", "C", date(2022, 3, 1)),
        _make_trial("NCT004", "HF", "D", None),  # no completion date
    ]

    result = filter_by_date_range(trials, date(2019, 1, 1), date(2021, 12, 31))
    nct_ids = [t.nct_id for t in result]
    assert nct_ids == ["NCT002"]


def test_filter_by_date_range_none_bounds():
    """None start/end means no bound on that side."""
    trials = [
        _make_trial("NCT001", "HF", "A", date(2018, 6, 1)),
        _make_trial("NCT002", "HF", "B", date(2022, 1, 1)),
    ]
    # No start bound
    result = filter_by_date_range(trials, None, date(2020, 1, 1))
    assert len(result) == 1
    assert result[0].nct_id == "NCT001"

    # No end bound
    result = filter_by_date_range(trials, date(2020, 1, 1), None)
    assert len(result) == 1
    assert result[0].nct_id == "NCT002"

    # Both None = no filtering (but still excludes None completion_date)
    trials_with_none = trials + [_make_trial("NCT003", "HF", "C", None)]
    result = filter_by_date_range(trials_with_none, None, None)
    assert len(result) == 2  # excludes the None-date trial


def test_filter_by_date_range_same_day():
    """Same start and end date includes trials on that exact date."""
    trials = [
        _make_trial("NCT001", "HF", "A", date(2020, 6, 15)),
        _make_trial("NCT002", "HF", "B", date(2020, 6, 16)),
    ]
    result = filter_by_date_range(trials, date(2020, 6, 15), date(2020, 6, 15))
    assert len(result) == 1
    assert result[0].nct_id == "NCT001"


# --- filter_by_search_text ---

def test_filter_by_search_text():
    trials = [
        _make_trial("NCT00112233", "Heart Failure", "Empagliflozin HF trial", date(2020, 1, 1)),
        _make_trial("NCT00445566", "CAD", "Aspirin and coronary disease", date(2020, 1, 1)),
    ]
    # Search by NCT ID substring
    result = filter_by_search_text(trials, "001122")
    assert len(result) == 1
    assert result[0].nct_id == "NCT00112233"

    # Search by title keyword (case-insensitive)
    result = filter_by_search_text(trials, "empagliflozin")
    assert len(result) == 1

    # Search by condition
    result = filter_by_search_text(trials, "heart failure")
    assert len(result) == 1


def test_filter_by_search_text_empty():
    """Empty/None search returns all trials."""
    trials = [_make_trial("NCT001", "HF", "Study", date(2020, 1, 1))]
    assert filter_by_search_text(trials, "") == trials
    assert filter_by_search_text(trials, None) == trials


# --- filter_by_pub_status ---

def test_filter_by_pub_status():
    trials = [
        _make_trial("NCT001", "HF", "A", date(2020, 1, 1), [_make_pub(date(2021, 1, 1))]),
        _make_trial("NCT002", "HF", "B", date(2020, 1, 1), []),
    ]
    assert len(filter_by_pub_status(trials, "All")) == 2
    assert len(filter_by_pub_status(trials, "Published Only")) == 1
    assert filter_by_pub_status(trials, "Published Only")[0].nct_id == "NCT001"
    assert len(filter_by_pub_status(trials, "Unpublished Only")) == 1
    assert filter_by_pub_status(trials, "Unpublished Only")[0].nct_id == "NCT002"


def test_filter_by_pub_status_unknown_returns_all():
    """Unknown status string returns all trials (safe fallback)."""
    trials = [
        _make_trial("NCT001", "HF", "A", date(2020, 1, 1), [_make_pub(date(2021, 1, 1))]),
        _make_trial("NCT002", "HF", "B", date(2020, 1, 1), []),
    ]
    assert len(filter_by_pub_status(trials, "InvalidStatus")) == 2


# --- get_trial_detail ---

def test_get_trial_detail():
    pub = _make_pub(date(2021, 6, 15), pmid="99999", title="Results of HF Trial",
                    journal="Lancet", doi="10.1016/test")
    trial = _make_trial("NCT001", "Heart Failure", "Empagliflozin HF Trial",
                        date(2020, 1, 1), [pub], enrollment=500)
    trial.mapped_domains = ["Heart Failure"]

    detail = get_trial_detail(trial)

    assert detail["nct_id"] == "NCT001"
    assert detail["title"] == "Empagliflozin HF Trial"
    assert detail["enrollment"] == 500
    assert detail["conditions"] == "Heart Failure"
    assert detail["interventions"] == "Drug A"
    assert detail["primary_endpoints"] == "Overall survival"
    assert len(detail["publications"]) == 1
    assert detail["publications"][0]["pmid"] == "99999"
    assert detail["publications"][0]["journal"] == "Lancet"


def test_get_trial_detail_no_pubs():
    trial = _make_trial("NCT002", "CAD", "Aspirin Trial", date(2019, 1, 1), [])
    detail = get_trial_detail(trial)
    assert detail["publications"] == []
    assert detail["completion_date"] == date(2019, 1, 1)
