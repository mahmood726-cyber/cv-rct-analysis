import pytest
from src.domain_mapper import DomainMapper

def test_map_to_domains():
    mapper = DomainMapper()
    
    # Test Heart Failure
    assert "Heart Failure" in mapper.map_to_domains("Study of chronic heart failure treatment")
    assert "Heart Failure" in mapper.map_to_domains("Congestive heart failure symptoms")
    
    # Test CAD
    assert "Coronary Artery Disease" in mapper.map_to_domains("Coronary artery bypass graft")
    assert "Coronary Artery Disease" in mapper.map_to_domains("Myocardial ischemia treatment")
    
    # Test Arrhythmia
    assert "Arrhythmia" in mapper.map_to_domains("Atrial fibrillation management")
    assert "Arrhythmia" in mapper.map_to_domains("Ventricular tachycardia ablation")
    
    # Test multiple
    domains = mapper.map_to_domains("Heart failure and atrial fibrillation")
    assert "Heart Failure" in domains
    assert "Arrhythmia" in domains
    
    # Test unknown
    assert mapper.map_to_domains("Something unrelated") == ["Other"]

def test_categorize_trial():
    mapper = DomainMapper()
    trial_mock = type('obj', (object,), {
        'conditions': 'Chronic Heart Failure',
        'title': 'A Study'
    })
    
    assert "Heart Failure" in mapper.categorize_trial(trial_mock)
