import asyncio
import logging
from datetime import datetime

class Reconciler:
    def __init__(self, pubmed_client, openalex_client, db_handler):
        self.pubmed_client = pubmed_client
        self.openalex_client = openalex_client
        self.db_handler = db_handler
        self.logger = logging.getLogger(__name__)

    async def reconcile_trial(self, trial):
        """
        Finds publications for a trial and stores them.
        """
        nct_id = trial.nct_id
        self.logger.info(f"Reconciling publications for {nct_id}...")
        
        pmids = await self.pubmed_client.search_nct_id(nct_id)
        
        if not pmids:
            self.logger.info(f"No PMIDs found for {nct_id}.")
            return

        for pmid in pmids:
            # Skip if publication already exists for this trial
            existing_pubs = self.db_handler.get_publications_for_trial(trial.id)
            if any(p.pmid == pmid for p in existing_pubs):
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
                
                # Extract journal name from OpenAlex structure
                journal = work_data.get("primary_location", {}).get("source", {}).get("display_name") if work_data.get("primary_location") else None
                
                pub_entry = {
                    "pmid": pmid,
                    "openalex_id": work_data.get("id"),
                    "title": work_data.get("title"),
                    "journal": journal,
                    "publication_date": pub_date,
                    "doi": work_data.get("doi"),
                    "abstract": self.openalex_client.reconstruct_abstract(work_data.get("abstract_inverted_index")),
                    "trial_id": trial.id
                }
                
                self.db_handler.add_publication(pub_entry)
                self.logger.info(f"Linked PMID {pmid} to {nct_id}.")
            else:
                # Minimal entry if OpenAlex fails
                pub_entry = {
                    "pmid": pmid,
                    "trial_id": trial.id
                }
                self.db_handler.add_publication(pub_entry)
                self.logger.warning(f"Linked PMID {pmid} to {nct_id} (OpenAlex data missing).")
