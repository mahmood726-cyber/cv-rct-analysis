import re
from collections import defaultdict


class DomainMapper:
    """
    Categorizes trials into cardiovascular sub-domains based on text analysis
    of titles and conditions.
    """

    DOMAIN_RULES = {
        "Heart Failure": [
            r"heart failure", r"hfpef", r"hfref", r"cardiomyopathy",
            r"cardiac failure",
        ],
        "Coronary Artery Disease": [
            r"coronary", r"ischemia", r"ischemic", r"angina",
            r"myocardial infarction", r"stemi", r"nstemi",
            r"acute coronary syndrome", r"\bacs\b", r"\bcad\b",
        ],
        "Arrhythmia": [
            r"arrhythmia", r"fibrillation", r"tachycardia", r"bradycardia",
            r"flutter", r"ablation", r"pacing", r"supraventricular",
        ],
        "Valvular Disease": [
            r"valve", r"aortic stenosis", r"mitral", r"regurgitation",
            r"tavi", r"tavr", r"valvular",
        ],
        "Hypertension": [
            r"hypertension", r"blood pressure", r"antihypertensive",
        ],
        "Vascular Disease": [
            r"stroke", r"cerebrovascular", r"\btia\b",
            r"peripheral arterial", r"aneurysm", r"thrombosis",
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
        """Categorizes a Trial object by analyzing its title and conditions."""
        text_to_analyze = f"{trial.title or ''} {trial.conditions or ''}"
        return self.map_to_domains(text_to_analyze)

    def categorize_trials(self, trials):
        """
        Batch-categorize trials into domain groups.
        Returns dict of {domain: [trial_list]}.
        """
        if not trials:
            return {}

        groups = defaultdict(list)
        for trial in trials:
            domain = self.map_domain(
                conditions=getattr(trial, 'conditions', '') or '',
                title=getattr(trial, 'title', '') or '',
            )
            groups[domain].append(trial)

        return dict(groups)
