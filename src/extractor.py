from sqlalchemy import create_engine, text
import logging

class CVRExtractor:
    def __init__(self, aact_connector, db_handler):
        self.aact_connector = aact_connector
        self.db_handler = db_handler
        self.logger = logging.getLogger(__name__)

    def transform_row(self, row):
        """
        Maps AACT database columns to our local Trial model fields.
        """
        return {
            'nct_id': row.get('nct_id'),
            'title': row.get('official_title'),
            'phase': row.get('phase'),
            'completion_date': row.get('completion_date'),
            'enrollment': row.get('enrollment'),
            'status': row.get('overall_status')
        }

    def extract_phase_3_trials(self, start_year=2015, end_year=2022):
        """
        Connects to AACT, runs the query, and stores results in local DB.
        """
        query_sql, params = self.aact_connector.generate_cv_query(start_year, end_year)

        self.logger.info(f"Connecting to AACT to extract trials for {start_year}-{end_year}...")

        # Note: We use a separate engine for AACT as it's external
        aact_engine = create_engine(self.aact_connector.db_url)

        try:
            with aact_engine.connect() as conn:
                result = conn.execute(text(query_sql), params)
                rows = result.mappings().all()

                self.logger.info(f"Found {len(rows)} trials in AACT. Processing...")

                for row in rows:
                    trial_data = self.transform_row(row)
                    self.db_handler.upsert_trial(trial_data)

            self.logger.info("Extraction and storage complete.")
        except Exception as e:
            self.logger.error(f"Error during extraction: {e}")
            raise
        finally:
            aact_engine.dispose()
