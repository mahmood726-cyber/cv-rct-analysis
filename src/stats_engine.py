"""Statistical aggregation engine for CV-RCT trials."""
import statistics


class StatsEngine:
    """
    Computes time-to-publication, publication rates, and domain-level summaries.
    Operates on lists of trial objects with .publications relationships.
    """

    def __init__(self, domain_mapper):
        self.domain_mapper = domain_mapper

    def time_to_publication(self, trial):
        """
        Returns days between trial completion_date and earliest publication_date.
        Returns None if either date is missing, trial has no publications,
        or publication precedes completion (data quality issue).
        """
        if not trial.completion_date or not trial.publications:
            return None

        pub_dates = [
            p.publication_date for p in trial.publications
            if p.publication_date is not None
        ]
        if not pub_dates:
            return None

        earliest = min(pub_dates)
        days = (earliest - trial.completion_date).days
        if days < 0:
            return None
        return days

    def publication_rate(self, trials):
        """Returns fraction of trials that have at least one publication."""
        if not trials:
            return 0.0
        published = sum(1 for t in trials if len(t.publications) > 0)
        return published / len(trials)

    def summary_stats(self, trials):
        """
        Aggregates metrics across all trials.
        Returns dict with total_trials, published/unpublished counts,
        publication_rate, median/mean time_to_pub.
        """
        if not trials:
            return {
                "total_trials": 0,
                "published_count": 0,
                "unpublished_count": 0,
                "publication_rate": 0.0,
                "median_time_to_pub": None,
                "mean_time_to_pub": None,
            }

        published_count = sum(1 for t in trials if len(t.publications) > 0)
        delays = []
        for trial in trials:
            d = self.time_to_publication(trial)
            if d is not None:
                delays.append(d)

        return {
            "total_trials": len(trials),
            "published_count": published_count,
            "unpublished_count": len(trials) - published_count,
            "publication_rate": published_count / len(trials),
            "median_time_to_pub": statistics.median(delays) if delays else None,
            "mean_time_to_pub": statistics.mean(delays) if delays else None,
        }

    def domain_summary(self, trials):
        """
        Groups trials by CV domain and computes per-domain summary_stats.
        Returns dict of {domain: summary_stats_dict}.
        """
        if not trials:
            return {}

        groups = self.domain_mapper.categorize_trials(trials)
        result = {}
        for domain, domain_trials in groups.items():
            result[domain] = self.summary_stats(domain_trials)
        return result
