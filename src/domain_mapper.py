"""Categorizes clinical trials into cardiovascular sub-domains via keyword matching."""
import re
from collections import defaultdict


class DomainMapper:
    """
    Categorizes trials into cardiovascular sub-domains based on text analysis
    of titles and conditions. Domain priority follows insertion order
    (Python 3.7+ dict ordering guarantee).
    """

    DOMAIN_RULES = {
        "Heart Failure": [
            r"heart failure", r"\bhfpef\b", r"\bhfref\b", r"cardiomyopathy",
            r"cardiac failure", r"ventricular dysfunction",
        ],
        "Coronary Artery Disease": [
            r"coronary", r"ischemic heart", r"myocardial ischemia", r"angina",
            r"myocardial infarction", r"\bstemi\b", r"\bnstemi\b",
            r"acute coronary syndrome", r"\bcad\b",
            r"percutaneous coronary", r"\bpci\b", r"\bcabg\b",
        ],
        "Arrhythmia": [
            r"arrhythmia", r"atrial fibrillation", r"atrial flutter",
            r"ventricular tachycardia", r"bradycardia",
            r"supraventricular", r"cardiac ablation", r"catheter ablation",
            r"cardiac pacing", r"\bpacemaker\b", r"\bicd\b", r"\bcrt\b",
        ],
        "Valvular Disease": [
            r"valve", r"aortic stenosis", r"mitral", r"regurgitation",
            r"\btavi\b", r"\btavr\b", r"valvular",
        ],
        "Pulmonary Hypertension": [
            r"pulmonary hypertension", r"pulmonary arterial hypertension",
            r"\bpah\b",
        ],
        "Hypertension": [
            r"hypertension", r"blood pressure", r"antihypertensive",
        ],
        "Lipid Disorders": [
            r"dyslipidemia", r"hyperlipidemia", r"cholesterol",
            r"\bstatin\b", r"\bpcsk9\b", r"lipid-lowering",
        ],
        "Vascular Disease": [
            r"\bstroke\b", r"cerebrovascular", r"\btia\b",
            r"peripheral arterial", r"aneurysm", r"thrombosis",
            r"deep vein", r"pulmonary embolism", r"\bdvt\b", r"\bpad\b",
        ],
    }

    def map_to_domains(self, text):
        """Maps a string of text to one or more CV domains."""
        if not text:
            return ["Other"]

        found_domains = []
        text_lower = text.lower()

        for domain, patterns in self.DOMAIN_RULES.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    found_domains.append(domain)
                    break

        return found_domains if found_domains else ["Other"]

    def map_domain(self, conditions="", title=""):
        """
        Maps conditions + title text to a single CV domain (first match).
        Returns "Other" if no domain matches.
        """
        text = f"{conditions or ''} {title or ''}".strip()
        domains = self.map_to_domains(text)
        return domains[0]

    def categorize_trial(self, trial):
        """Categorizes a Trial object by analyzing its conditions and title."""
        text_to_analyze = f"{trial.conditions or ''} {trial.title or ''}"
        return self.map_to_domains(text_to_analyze)

    def categorize_trials(self, trials):
        """
        Batch-categorize trials into domain groups.
        Each trial is assigned to ALL matching domains (multi-label).
        Returns dict of {domain: [trial_list]}.
        """
        if not trials:
            return {}

        groups = defaultdict(list)
        for trial in trials:
            domains = self.categorize_trial(trial)
            for domain in domains:
                groups[domain].append(trial)

        return dict(groups)
