"""Basic statistical calculations for CV-RCT publication metrics."""
import statistics


class CVStatsCalculator:
    """
    Calculates statistical metrics for cardiovascular trials and their publications.
    """

    def calculate_days_to_pub(self, completion_date, publication_date):
        """
        Calculates the number of days between trial completion and publication.
        Returns None if dates are missing or publication precedes completion.
        """
        if not completion_date or not publication_date:
            return None

        delta = publication_date - completion_date
        if delta.days < 0:
            return None
        return delta.days

    def calculate_publication_rate(self, trials):
        """
        Calculates the fraction of trials that have at least one publication.
        """
        if not trials:
            return 0.0

        published_count = sum(1 for trial in trials if len(trial.publications) > 0)
        return published_count / len(trials)

    def calculate_median_delay(self, delays):
        """
        Calculates the median delay in days from a list of delay values.
        """
        valid_delays = [d for d in delays if d is not None]
        if not valid_delays:
            return None

        return statistics.median(valid_delays)

    def get_summary_report(self, trials):
        """
        Generates a summary dictionary of statistics for a set of trials.
        """
        pub_rate = self.calculate_publication_rate(trials)

        delays = []
        for trial in trials:
            if trial.completion_date and trial.publications:
                earliest_pub = min(
                    [p.publication_date for p in trial.publications if p.publication_date],
                    default=None
                )
                if earliest_pub:
                    delay = self.calculate_days_to_pub(trial.completion_date, earliest_pub)
                    if delay is not None:
                        delays.append(delay)

        median_delay = self.calculate_median_delay(delays)

        return {
            "total_trials": len(trials),
            "publication_rate": pub_rate,
            "median_delay_days": median_delay,
            "published_count": sum(1 for trial in trials if len(trial.publications) > 0)
        }
