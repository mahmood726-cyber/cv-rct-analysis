class AACTConnector:
    """
    Handles connection and querying logic for the AACT (ClinicalTrials.gov) database.
    AACT is a public PostgreSQL database provided by CTTI.
    """
    
    CV_MESH_TERMS = [
        'Heart Diseases', 'Cardiovascular Diseases', 'Arrhythmias, Cardiac', 
        'Coronary Artery Disease', 'Heart Failure', 'Myocardial Infarction',
        'Stroke', 'Hypertension', 'Atrial Fibrillation'
    ]
    
    CV_KEYWORDS = [
        'heart', 'cardiac', 'cardiovascular', 'coronary', 'arrhythmia', 
        'myocardial', 'valve', 'aorta', 'artery', 'vein'
    ]

    def __init__(self, db_url=None):
        self.db_url = db_url or "postgresql://aact:aact@aact-db.ctti-clinicaltrials.org:5432/aact"

    def generate_cv_query(self, start_year=2015, end_year=2022):
        """
        Generates a parameterized SQL query to find Phase 3 CV RCTs within a date range.
        Returns (sql_text, params_dict) for safe execution via conn.execute(text(sql), params).
        """
        # Validate year inputs are integers to prevent injection
        start_year = int(start_year)
        end_year = int(end_year)

        # Build mesh term placeholders
        mesh_placeholders = ", ".join(
            f":mesh_{i}" for i in range(len(self.CV_MESH_TERMS))
        )
        # Build keyword ILIKE clauses
        keyword_clauses = " OR ".join(
            f"browse_conditions.mesh_term ILIKE :kw_{i}"
            for i in range(len(self.CV_KEYWORDS))
        )

        query = f"""
        SELECT
            studies.nct_id,
            studies.official_title,
            studies.phase,
            studies.study_type,
            studies.completion_date,
            studies.enrollment,
            studies.overall_status
        FROM studies
        JOIN browse_conditions ON studies.nct_id = browse_conditions.nct_id
        WHERE studies.phase = 'Phase 3'
          AND studies.study_type = 'Interventional'
          AND studies.completion_date BETWEEN :start_date AND :end_date
          AND (
            browse_conditions.mesh_term IN ({mesh_placeholders})
            OR {keyword_clauses}
          )
        GROUP BY studies.nct_id
        """.strip()

        params = {
            "start_date": f"{start_year}-01-01",
            "end_date": f"{end_year}-12-31",
        }
        for i, term in enumerate(self.CV_MESH_TERMS):
            params[f"mesh_{i}"] = term
        for i, kw in enumerate(self.CV_KEYWORDS):
            params[f"kw_{i}"] = f"%{kw}%"

        return query, params
