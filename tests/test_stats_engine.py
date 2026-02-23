import pytest
from datetime import date
from unittest.mock import MagicMock
from src.stats_engine import StatsEngine
from src.domain_mapper import DomainMapper


def _make_trial(nct_id, conditions, title, completion_date, publications=None):
    """Helper to create mock trial objects."""
    trial = type('obj', (object,), {
        'nct_id': nct_id,
        'conditions': conditions,
        'title': title,
        'completion_date': completion_date,
        'enrollment': 100,
        'publications': publications or [],
    })
    return trial


def _make_pub(publication_date):
    """Helper to create mock publication objects."""
    return type('obj', (object,), {
        'publication_date': publication_date,
    })


@pytest.fixture
def engine():
    db_handler = MagicMock()
    domain_mapper = DomainMapper()
    return StatsEngine(db_handler, domain_mapper)


# --- time_to_publication ---

def test_time_to_publication(engine):
    """Completion 2020-01-01 + Publication 2021-06-15 = 531 days."""
    pub = _make_pub(date(2021, 6, 15))
    trial = _make_trial("NCT001", "HF", "Study", date(2020, 1, 1), [pub])
    assert engine.time_to_publication(trial) == 531


def test_time_to_publication_multiple_pubs(engine):
    """Uses earliest publication date."""
    pub1 = _make_pub(date(2022, 1, 1))
    pub2 = _make_pub(date(2021, 6, 15))  # earlier
    trial = _make_trial("NCT002", "HF", "Study", date(2020, 1, 1), [pub1, pub2])
    assert engine.time_to_publication(trial) == 531


def test_time_to_publication_no_pub(engine):
    """Trial without publications returns None."""
    trial = _make_trial("NCT003", "HF", "Study", date(2020, 1, 1), [])
    assert engine.time_to_publication(trial) is None


def test_time_to_publication_no_completion(engine):
    """Trial without completion_date returns None."""
    pub = _make_pub(date(2021, 6, 15))
    trial = _make_trial("NCT004", "HF", "Study", None, [pub])
    assert engine.time_to_publication(trial) is None


def test_time_to_publication_pub_no_date(engine):
    """Publication with None date returns None."""
    pub = _make_pub(None)
    trial = _make_trial("NCT005", "HF", "Study", date(2020, 1, 1), [pub])
    assert engine.time_to_publication(trial) is None


# --- publication_rate ---

def test_publication_rate(engine):
    """10 trials, 7 with publications -> 0.70."""
    trials = []
    for i in range(7):
        trials.append(_make_trial(f"NCT0{i}", "HF", "S", date(2020, 1, 1),
                                  [_make_pub(date(2021, 1, 1))]))
    for i in range(3):
        trials.append(_make_trial(f"NCT1{i}", "HF", "S", date(2020, 1, 1), []))

    assert engine.publication_rate(trials) == pytest.approx(0.70)


def test_publication_rate_empty(engine):
    """0 trials -> 0.0."""
    assert engine.publication_rate([]) == 0.0


def test_publication_rate_all_published(engine):
    trials = [_make_trial("NCT01", "HF", "S", date(2020, 1, 1),
                          [_make_pub(date(2021, 1, 1))])]
    assert engine.publication_rate(trials) == 1.0


# --- summary_stats ---

def test_summary_stats(engine):
    """Full summary with aggregated metrics."""
    pub1 = _make_pub(date(2021, 6, 15))   # 531 days from 2020-01-01
    pub2 = _make_pub(date(2020, 7, 1))    # 182 days from 2020-01-01

    trials = [
        _make_trial("NCT001", "Heart Failure", "HF Study", date(2020, 1, 1), [pub1]),
        _make_trial("NCT002", "Coronary artery disease", "CAD Study", date(2020, 1, 1), [pub2]),
        _make_trial("NCT003", "Atrial fibrillation", "AF Study", date(2020, 1, 1), []),
    ]

    stats = engine.summary_stats(trials)

    assert stats["total_trials"] == 3
    assert stats["published_count"] == 2
    assert stats["unpublished_count"] == 1
    assert stats["publication_rate"] == pytest.approx(2 / 3)
    assert stats["median_time_to_pub"] == pytest.approx((531 + 182) / 2)  # median of 2 = mean
    assert stats["mean_time_to_pub"] == pytest.approx((531 + 182) / 2)


def test_summary_stats_no_publications(engine):
    """All unpublished trials."""
    trials = [
        _make_trial("NCT001", "HF", "S", date(2020, 1, 1), []),
        _make_trial("NCT002", "HF", "S", date(2020, 1, 1), []),
    ]
    stats = engine.summary_stats(trials)
    assert stats["total_trials"] == 2
    assert stats["published_count"] == 0
    assert stats["publication_rate"] == 0.0
    assert stats["median_time_to_pub"] is None
    assert stats["mean_time_to_pub"] is None


# --- domain_summary ---

def test_domain_summary(engine):
    """Groups trials by domain and computes per-domain stats."""
    pub_hf = _make_pub(date(2021, 1, 1))
    pub_cad = _make_pub(date(2021, 6, 15))

    trials = [
        _make_trial("NCT001", "Heart Failure", "HF Study", date(2020, 1, 1), [pub_hf]),
        _make_trial("NCT002", "Heart Failure", "HF Study 2", date(2020, 1, 1), []),
        _make_trial("NCT003", "Coronary artery disease", "CAD Study", date(2020, 1, 1), [pub_cad]),
    ]

    result = engine.domain_summary(trials)

    assert "Heart Failure" in result
    assert "Coronary Artery Disease" in result
    assert result["Heart Failure"]["total_trials"] == 2
    assert result["Heart Failure"]["published_count"] == 1
    assert result["Heart Failure"]["publication_rate"] == pytest.approx(0.5)
    assert result["Coronary Artery Disease"]["total_trials"] == 1
    assert result["Coronary Artery Disease"]["publication_rate"] == 1.0


def test_domain_summary_empty(engine):
    """Empty trial list returns empty dict."""
    assert engine.domain_summary([]) == {}


# --- discrepancy_detection ---

def test_discrepancy_detection(engine):
    """Detects enrollment mismatch between trial and publication."""
    pub = _make_pub(date(2021, 1, 1))
    pub.reported_enrollment = 200  # publication says 200 but trial says 100

    trial = _make_trial("NCT001", "HF", "Study", date(2020, 1, 1), [pub])
    trial.enrollment = 100

    discrepancies = engine.detect_discrepancies([trial])
    assert len(discrepancies) == 1
    assert discrepancies[0]["nct_id"] == "NCT001"
    assert discrepancies[0]["trial_enrollment"] == 100
    assert discrepancies[0]["pub_enrollment"] == 200


def test_discrepancy_detection_no_mismatch(engine):
    """No discrepancy when enrollments match or publication has no reported enrollment."""
    pub = _make_pub(date(2021, 1, 1))
    # No reported_enrollment attribute — should not flag

    trial = _make_trial("NCT001", "HF", "Study", date(2020, 1, 1), [pub])
    trial.enrollment = 100

    discrepancies = engine.detect_discrepancies([trial])
    assert len(discrepancies) == 0
