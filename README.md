# CV-RCT Analysis

Analysis pipeline for cardiovascular Phase III randomized controlled trials (2015-2022), integrating data from ClinicalTrials.gov (via AACT), PubMed, and OpenAlex.

## Setup

```bash
# Clone and install dependencies
git clone <repository-url>
cd cv-rct-analysis
pip install -r requirements.txt
```

## Quick Start (Demo with Mock Data)

```bash
# 1. Populate a local SQLite database with mock trial data
python -m src.mock_data

# 2. Launch the Streamlit dashboard
streamlit run src/app.py
```

## Full Pipeline (Requires PostgreSQL + Network)

```bash
# Set database URL (default: postgresql://postgres:postgres@localhost:5432/cv_rct_db)
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"

# Run extraction + reconciliation pipeline
python -m src.pipeline --start 2015 --end 2022
```

## Running Tests

```bash
# All tests (no network/database required)
python -m pytest tests/ -v

# With coverage report
python -m pytest tests/ --cov=src --cov-report=term-missing
```

## Project Structure

```
src/
  app.py              # Streamlit dashboard entry point
  app_utils.py        # Dashboard helper functions (filtering, formatting)
  domain_mapper.py    # CV sub-domain classification (Heart Failure, CAD, etc.)
  stats_engine.py     # Statistical aggregation with domain-level summaries
  stats.py            # Basic publication metrics calculator
  viz.py              # Forest and funnel plot generation (Plotly)
  pipeline.py         # Orchestrates extraction + reconciliation
  extractor.py        # AACT data extraction
  reconciler.py       # PubMed/OpenAlex publication matching
  handlers.py         # Database CRUD operations
  models.py           # SQLAlchemy ORM models (Trial, Publication)
  database.py         # Engine and session management
  aact_connector.py   # Parameterized AACT SQL query generation
  validator.py        # Data integrity checks
  mock_data.py        # Demo data population script
tests/
  test_*.py           # pytest test suite (87 tests)
  conftest.py         # Test path configuration
```

## Important Notes

- **Mock data**: The demo uses obviously fake NCT IDs (NCT99000001-NCT99000005) to prevent confusion with real ClinicalTrials.gov entries.
- **Visualizations**: Forest and funnel plots in the demo use simulated effect sizes for illustration only. Real clinical outcomes require separate extraction.
- **Domain classification**: Trials are categorized into 8 cardiovascular sub-domains via keyword matching. Multi-label assignment means a single trial can appear in multiple domains.

## License

MIT License. See [LICENSE](LICENSE).
