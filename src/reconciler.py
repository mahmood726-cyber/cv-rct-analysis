import logging
from datetime import datetime


class Reconciler:
    def __init__(self, pubmed_client, openalex_client, db_handler):
        self.pubmed_client = pubmed_client
        self.openalex_client = openalex_client
        self.db_handler = db_handler
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _extract_journal(work_data):
        """Safely extract journal name from OpenAlex primary_location."""
        location = work_data.get("primary_location")
        if not location:
            return None
        source = location.get("source")
        if not source:
            return None
        return source.get("display_name")

    async def reconcile_trial(self, trial):
        """Finds publications for a trial and stores them."""
        nct_id = trial.nct_id
        self.logger.info(f"Reconciling publications for {nct_id}...")

        pmids = await self.pubmed_client.search_nct_id(nct_id)

        if not pmids:
            self.logger.info(f"No PMIDs found for {nct_id}.")
            return

        # Fetch existing publications ONCE before the loop (fixes N+1 query)
        existing_pubs = self.db_handler.get_publications_for_trial(trial.id)
        existing_pmids = {p.pmid for p in existing_pubs}

        for pmid in pmids:
            if pmid in existing_pmids:
                self.logger.info(f"PMID {pmid} already linked to {nct_id}, skipping.")
                continue

            work_data = await self.openalex_client.get_work_by_pmid(pmid)

            if work_data:
                pub_date = work_data.get("publication_date")
                if pub_date:
                    try:
                        pub_date = datetime.strptime(pub_date, "%Y-%m-%d").date()
                    except ValueError:
                        pub_date = None

                pub_entry = {
                    "pmid": pmid,
                    "openalex_id": work_data.get("id"),
                    "title": work_data.get("title"),
                    "journal": self._extract_journal(work_data),
                    "publication_date": pub_date,
                    "doi": work_data.get("doi"),
                    "abstract": self.openalex_client.reconstruct_abstract(
                        work_data.get("abstract_inverted_index")),
                    "trial_id": trial.id
                }

                self.db_handler.add_publication(pub_entry)
                existing_pmids.add(pmid)
                self.logger.info(f"Linked PMID {pmid} to {nct_id}.")
            else:
                pub_entry = {
                    "pmid": pmid,
                    "trial_id": trial.id
                }
                self.db_handler.add_publication(pub_entry)
                existing_pmids.add(pmid)
                self.logger.warning(f"Linked PMID {pmid} to {nct_id} (OpenAlex data missing).")
