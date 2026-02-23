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
        Generates a SQL query to find Phase 3 CV RCTs within a date range.
        """
        mesh_terms_str = "', '".join(self.CV_MESH_TERMS)
        keywords_str = "%' OR browse_conditions.mesh_term ILIKE '%".join(self.CV_KEYWORDS)
        
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
          AND studies.completion_date BETWEEN '{start_year}-01-01' AND '{end_year}-12-31'
          AND (
            browse_conditions.mesh_term IN ('{mesh_terms_str}')
            OR browse_conditions.mesh_term ILIKE '%{keywords_str}%'
          )
        GROUP BY studies.nct_id
        """
        return query.strip()
