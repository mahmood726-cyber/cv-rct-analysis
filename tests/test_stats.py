import pytest
from datetime import date
from src.stats import CVStatsCalculator


def _make_pub(pub_date):
    return type('obj', (object,), {'publication_date': pub_date})


def test_calculate_time_to_publication():
    calc = CVStatsCalculator()
    completion_date = date(2020, 1, 1)
    publication_date = date(2021, 1, 1)

    # 366 days because 2020 is a leap year
    assert calc.calculate_days_to_pub(completion_date, publication_date) == 366


def test_calculate_time_to_publication_negative():
    """Publication before completion returns None."""
    calc = CVStatsCalculator()
    assert calc.calculate_days_to_pub(date(2021, 1, 1), date(2020, 1, 1)) is None


def test_calculate_time_to_publication_none_inputs():
    calc = CVStatsCalculator()
    assert calc.calculate_days_to_pub(None, date(2021, 1, 1)) is None
    assert calc.calculate_days_to_pub(date(2020, 1, 1), None) is None


def test_calculate_publication_rate():
    calc = CVStatsCalculator()

    trials = [
        type('obj', (object,), {'publications': [_make_pub(date(2021, 1, 1))]}),
        type('obj', (object,), {'publications': []}),
        type('obj', (object,), {'publications': [_make_pub(date(2021, 6, 1)), _make_pub(date(2022, 1, 1))]}),
        type('obj', (object,), {'publications': []}),
    ]

    # 2 out of 4 have publications
    assert calc.calculate_publication_rate(trials) == 0.5


def test_calculate_publication_rate_empty():
    calc = CVStatsCalculator()
    assert calc.calculate_publication_rate([]) == 0.0


def test_median_publication_delay():
    calc = CVStatsCalculator()

    delays = [100, 200, 300, 400, 500]
    assert calc.calculate_median_delay(delays) == 300

    delays_even = [100, 200, 300, 400]
    assert calc.calculate_median_delay(delays_even) == 250


def test_median_publication_delay_with_nones():
    calc = CVStatsCalculator()
    assert calc.calculate_median_delay([None, 200, None, 400]) == 300
    assert calc.calculate_median_delay([None, None]) is None


def test_get_summary_report():
    calc = CVStatsCalculator()

    pub_mock = _make_pub(date(2021, 1, 1))
    trials = [
        type('obj', (object,), {
            'publications': [pub_mock],
            'completion_date': date(2020, 1, 1)
        }),
        type('obj', (object,), {
            'publications': [],
            'completion_date': date(2020, 1, 1)
        })
    ]

    report = calc.get_summary_report(trials)
    assert report["total_trials"] == 2
    assert report["published_count"] == 1
    assert report["publication_rate"] == 0.5
    assert report["median_delay_days"] == 366


def test_get_summary_report_excludes_negative_delays():
    """Pre-completion publications should not appear in delay stats."""
    calc = CVStatsCalculator()

    pub_before = _make_pub(date(2019, 6, 1))  # before completion
    pub_after = _make_pub(date(2021, 1, 1))   # 366 days

    trials = [
        type('obj', (object,), {
            'publications': [pub_before],
            'completion_date': date(2020, 1, 1)
        }),
        type('obj', (object,), {
            'publications': [pub_after],
            'completion_date': date(2020, 1, 1)
        }),
    ]

    report = calc.get_summary_report(trials)
    assert report["published_count"] == 2
    assert report["median_delay_days"] == 366  # only the valid delay
