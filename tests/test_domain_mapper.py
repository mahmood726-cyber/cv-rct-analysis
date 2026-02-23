import pytest
from src.domain_mapper import DomainMapper


@pytest.fixture
def mapper():
    return DomainMapper()


# --- Existing multi-domain tests (preserved) ---

def test_map_to_domains(mapper):
    assert "Heart Failure" in mapper.map_to_domains("Study of chronic heart failure treatment")
    assert "Coronary Artery Disease" in mapper.map_to_domains("Coronary artery bypass graft")
    assert "Arrhythmia" in mapper.map_to_domains("Atrial fibrillation management")

    domains = mapper.map_to_domains("Heart failure and atrial fibrillation")
    assert "Heart Failure" in domains
    assert "Arrhythmia" in domains

    assert mapper.map_to_domains("Something unrelated") == ["Other"]


def test_categorize_trial(mapper):
    trial_mock = type('obj', (object,), {
        'conditions': 'Chronic Heart Failure',
        'title': 'A Study'
    })
    assert "Heart Failure" in mapper.categorize_trial(trial_mock)


# --- map_domain (single-string return) ---

def test_map_heart_failure(mapper):
    """Conditions containing HF variants map to Heart Failure."""
    for text in ["heart failure", "HFrEF", "HFpEF", "cardiomyopathy", "cardiac failure"]:
        assert mapper.map_domain(conditions=text) == "Heart Failure", f"Failed for: {text}"


def test_map_cad(mapper):
    """Coronary / ischemic conditions map to CAD."""
    for text in [
        "coronary artery disease", "myocardial infarction",
        "acute coronary syndrome", "angina", "STEMI", "NSTEMI"
    ]:
        assert mapper.map_domain(conditions=text) == "Coronary Artery Disease", f"Failed for: {text}"


def test_map_arrhythmia(mapper):
    for text in ["atrial fibrillation", "arrhythmia", "ventricular tachycardia", "supraventricular"]:
        assert mapper.map_domain(conditions=text) == "Arrhythmia", f"Failed for: {text}"


def test_map_hypertension(mapper):
    for text in ["hypertension", "blood pressure", "antihypertensive"]:
        assert mapper.map_domain(conditions=text) == "Hypertension", f"Failed for: {text}"


def test_map_valvular(mapper):
    for text in ["aortic stenosis", "mitral regurgitation", "valve replacement"]:
        assert mapper.map_domain(conditions=text) == "Valvular Disease", f"Failed for: {text}"


def test_map_vascular(mapper):
    for text in ["peripheral arterial disease", "stroke survivors", "cerebrovascular accident", "aneurysm", "thrombosis"]:
        assert mapper.map_domain(conditions=text) == "Vascular Disease", f"Failed for: {text}"


def test_map_lipid(mapper):
    """Lipid disorders domain."""
    for text in ["dyslipidemia", "hyperlipidemia", "cholesterol lowering", "statin therapy", "PCSK9 inhibitor"]:
        assert mapper.map_domain(conditions=text) == "Lipid Disorders", f"Failed for: {text}"


def test_map_pulmonary_hypertension(mapper):
    for text in ["pulmonary hypertension", "pulmonary arterial hypertension", "PAH treatment"]:
        assert mapper.map_domain(conditions=text) == "Pulmonary Hypertension", f"Failed for: {text}"


def test_map_other(mapper):
    """Unrecognized conditions fall back to Other."""
    assert mapper.map_domain(conditions="diabetes mellitus") == "Other"
    assert mapper.map_domain(conditions="") == "Other"
    assert mapper.map_domain(conditions=None) == "Other"


def test_map_from_title(mapper):
    """When conditions are empty, falls back to title text."""
    assert mapper.map_domain(conditions="", title="A trial of heart failure therapy") == "Heart Failure"
    assert mapper.map_domain(conditions=None, title="Atrial fibrillation study") == "Arrhythmia"


def test_map_multiple_matches_returns_first(mapper):
    """When text matches multiple domains, returns the first match (dict order)."""
    result = mapper.map_domain(conditions="heart failure with atrial fibrillation")
    # Heart Failure comes before Arrhythmia in DOMAIN_RULES
    assert result == "Heart Failure"


# --- False-positive prevention ---

def test_ablation_not_false_positive(mapper):
    """Generic 'ablation' alone should not trigger Arrhythmia (needs cardiac/catheter context)."""
    # Hepatic ablation should not match Arrhythmia
    assert mapper.map_domain(conditions="radiofrequency ablation of hepatic tumors") == "Other"
    # But cardiac ablation should
    assert mapper.map_domain(conditions="catheter ablation for atrial fibrillation") == "Arrhythmia"


def test_ischemia_specificity(mapper):
    """Bare 'ischemia' should not trigger CAD (too broad — matches limb/renal)."""
    assert mapper.map_domain(conditions="limb ischemia") == "Other"
    assert mapper.map_domain(conditions="renal ischemia") == "Other"
    # But specific cardiac ischemia matches
    assert mapper.map_domain(conditions="ischemic heart disease") == "Coronary Artery Disease"
    assert mapper.map_domain(conditions="myocardial ischemia") == "Coronary Artery Disease"


def test_pacing_not_false_positive(mapper):
    """Generic 'pacing' should not trigger Arrhythmia."""
    assert mapper.map_domain(conditions="self-pacing exercise intervention") == "Other"
    assert mapper.map_domain(conditions="cardiac pacing for bradycardia") == "Arrhythmia"


# --- categorize_trials (batch, multi-label) ---

def test_categorize_trials(mapper):
    """Batch processing groups trials by domain."""
    trials = [
        type('obj', (object,), {'conditions': 'Heart Failure', 'title': 'Study A'}),
        type('obj', (object,), {'conditions': 'Atrial Fibrillation', 'title': 'Study B'}),
        type('obj', (object,), {'conditions': 'Heart Failure', 'title': 'Study C'}),
        type('obj', (object,), {'conditions': 'Diabetes', 'title': 'Study D'}),
        type('obj', (object,), {'conditions': 'Coronary artery disease', 'title': 'Study E'}),
    ]

    result = mapper.categorize_trials(trials)

    assert len(result["Heart Failure"]) == 2
    assert len(result["Arrhythmia"]) == 1
    assert len(result["Coronary Artery Disease"]) == 1
    assert len(result["Other"]) == 1


def test_categorize_trials_multi_label(mapper):
    """A trial matching two domains appears in both groups."""
    trials = [
        type('obj', (object,), {
            'conditions': 'Heart failure with atrial fibrillation',
            'title': 'Dual study'
        }),
    ]
    result = mapper.categorize_trials(trials)
    assert "Heart Failure" in result
    assert "Arrhythmia" in result
    # Same trial object in both groups
    assert result["Heart Failure"][0] is result["Arrhythmia"][0]


def test_categorize_trials_empty(mapper):
    """Empty trial list returns empty dict."""
    result = mapper.categorize_trials([])
    assert result == {}


# --- Consistent concatenation order ---

def test_categorize_trial_conditions_first(mapper):
    """categorize_trial should check conditions before title (conditions-first order)."""
    trial = type('obj', (object,), {
        'conditions': 'Heart Failure',
        'title': 'A generic study'
    })
    assert "Heart Failure" in mapper.categorize_trial(trial)
