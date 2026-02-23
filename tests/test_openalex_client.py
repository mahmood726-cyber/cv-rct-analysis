import pytest
import respx
import re
from httpx import Response
from src.openalex_client import OpenAlexClient

@pytest.mark.asyncio
async def test_get_work_by_pmid():
    client = OpenAlexClient()
    pmid = "12345678"
    
    # Mock OpenAlex Work response
    work_url_pattern = re.compile(r"https://api\.openalex\.org/works/https://pubmed\.ncbi\.nlm\.nih\.gov/.*")
    
    with respx.mock:
        respx.get(work_url_pattern).mock(return_value=Response(200, json={
            "id": "https://openalex.org/W12345678",
            "title": "OpenAlex Test Work",
            "doi": "https://doi.org/10.1000/test",
            "publication_date": "2021-01-01",
            "primary_location": {
                "source": {
                    "display_name": "Journal of Medicine"
                }
            },
            "abstract_inverted_index": {"Test": [0], "abstract": [1]}
        }))
        
        work = await client.get_work_by_pmid(pmid)
        assert work["title"] == "OpenAlex Test Work"
        assert work["id"] == "https://openalex.org/W12345678"

@pytest.mark.asyncio
async def test_get_work_by_pmid_not_found():
    client = OpenAlexClient()
    pmid = "99999999"
    
    work_url_pattern = re.compile(r"https://api\.openalex\.org/works/https://pubmed\.ncbi\.nlm\.nih\.gov/.*")
    
    with respx.mock:
        respx.get(work_url_pattern).mock(return_value=Response(404))
        
        work = await client.get_work_by_pmid(pmid)
        assert work is None
