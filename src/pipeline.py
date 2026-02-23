import asyncio
import logging
from src.models import Trial

class CVPipeline:
    def __init__(self, extractor, reconciler, db_handler):
        self.extractor = extractor
        self.reconciler = reconciler
        self.db_handler = db_handler
        self.logger = logging.getLogger(__name__)

    async def run(self, start_year=2015, end_year=2022):
        """
        Orchestrates the full pipeline: extraction followed by cross-referencing.
        """
        self.logger.info(f"Starting CV-RCT Extraction Pipeline for {start_year}-{end_year}")
        
        # Step 1: Extraction from AACT
        try:
            self.extractor.extract_phase_3_trials(start_year, end_year)
        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            return

        # Step 2: Reconciliation with PubMed/OpenAlex
        self.logger.info("Beginning publication cross-referencing...")
        
        session = self.db_handler.Session()
        try:
            # Fetch all trials that were just extracted/updated
            trials = session.query(Trial).all()
            self.logger.info(f"Processing {len(trials)} trials for reconciliation.")
            
            for trial in trials:
                try:
                    await self.reconciler.reconcile_trial(trial)
                except Exception as trial_err:
                    self.logger.error(f"Error reconciling trial {trial.nct_id}: {trial_err}")
                
            self.logger.info("Pipeline execution finished successfully.")
        except Exception as e:
            self.logger.error(f"Reconciliation failed: {e}")
        finally:
            session.close()

def main():
    import argparse
    from src.database import get_engine, init_db
    from src.handlers import DBHandler
    from src.aact_connector import AACTConnector
    from src.extractor import CVRExtractor
    from src.pubmed_client import PubMedClient
    from src.openalex_client import OpenAlexClient
    from src.reconciler import Reconciler

    parser = argparse.ArgumentParser(description="Run the CV-RCT Extraction Pipeline.")
    parser.add_argument("--start", type=int, default=2015)
    parser.add_argument("--end", type=int, default=2022)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    
    # Initialize components
    engine = get_engine()
    init_db(engine)
    db_handler = DBHandler(engine)
    
    aact = AACTConnector()
    extractor = CVRExtractor(aact, db_handler)
    
    pubmed = PubMedClient()
    openalex = OpenAlexClient()
    reconciler = Reconciler(pubmed, openalex, db_handler)
    
    pipeline = CVPipeline(extractor, reconciler, db_handler)
    
    asyncio.run(pipeline.run(args.start, args.end))

if __name__ == "__main__":
    main()
