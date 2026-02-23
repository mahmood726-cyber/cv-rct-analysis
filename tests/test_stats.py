import pytest
from datetime import date
from src.stats import CVStatsCalculator

def test_calculate_time_to_publication():
    calc = CVStatsCalculator()
    completion_date = date(2020, 1, 1)
    publication_date = date(2021, 1, 1)
    
    # 366 days because 2020 is a leap year
    assert calc.calculate_days_to_pub(completion_date, publication_date) == 366

def test_calculate_publication_rate():
    calc = CVStatsCalculator()
    
    # Mock trials list
    trials = [
        type('obj', (object,), {'publications': [1]}),
        type('obj', (object,), {'publications': []}),
        type('obj', (object,), {'publications': [1, 2]}),
        type('obj', (object,), {'publications': []}),
    ]
    
    # 2 out of 4 have publications
    assert calc.calculate_publication_rate(trials) == 0.5

def test_median_publication_delay():
    calc = CVStatsCalculator()
    
    delays = [100, 200, 300, 400, 500]
    assert calc.calculate_median_delay(delays) == 300
    
    delays_even = [100, 200, 300, 400]
    assert calc.calculate_median_delay(delays_even) == 250

def test_get_summary_report():
    calc = CVStatsCalculator()
    
    # Mock data
    pub_mock = type('obj', (object,), {'publication_date': date(2021, 1, 1)})
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
