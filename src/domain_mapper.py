import re

class DomainMapper:
    """
    Categorizes trials into cardiovascular sub-domains based on text analysis
    of titles and conditions.
    """
    
    DOMAIN_RULES = {
        "Heart Failure": [
            r"heart failure", r"hfn", r"hfpef", r"hfref", r"cardiomyopathy"
        ],
        "Coronary Artery Disease": [
            r"coronary", r"ischemia", r"ischemic", r"angina", r"myocardial infarction", r"stemi", r"nstemi", r"acs"
        ],
        "Arrhythmia": [
            r"arrhythmia", r"fibrillation", r"tachycardia", r"bradycardia", r"flutter", r"ablation", r"pacing"
        ],
        "Valvular Disease": [
            r"valve", r"aortic stenosis", r"mitral", r"regurgitation", r"tavi", r"tavr"
        ],
        "Hypertension": [
            r"hypertension", r"blood pressure"
        ],
        "Stroke": [
            r"stroke", r"cerebrovascular", r"tia"
        ]
    }

    def map_to_domains(self, text):
        """
        Maps a string of text to one or more CV domains.
        """
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

    def categorize_trial(self, trial):
        """
        Categorizes a Trial object by analyzing its title and conditions.
        """
        text_to_analyze = f"{trial.title or ''} {trial.conditions or ''}"
        return self.map_to_domains(text_to_analyze)
