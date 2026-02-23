import pytest
import respx
import re
from httpx import Response
from src.pubmed_client import PubMedClient

@pytest.mark.asyncio
async def test_search_nct_id():
    client = PubMedClient()
    nct_id = "NCT01234567"
    
    # Mock PubMed ESearch response
    # Using regex to match the URL more robustly
    search_url_pattern = re.compile(r"https://eutils\.ncbi\.nlm\.nih\.gov/entrez/eutils/esearch\.fcgi.*")
    
    with respx.mock:
        respx.get(search_url_pattern).mock(return_value=Response(200, json={
            "esearchresult": {
                "idlist": ["12345678", "87654321"]
            }
        }))
        
        pmids = await client.search_nct_id(nct_id)
        assert pmids == ["12345678", "87654321"]

@pytest.mark.asyncio
async def test_search_nct_id_empty():
    client = PubMedClient()
    nct_id = "NCT99999999"
    
    search_url_pattern = re.compile(r"https://eutils\.ncbi\.nlm\.nih\.gov/entrez/eutils/esearch\.fcgi.*")
    
    with respx.mock:
        respx.get(search_url_pattern).mock(return_value=Response(200, json={
            "esearchresult": {
                "idlist": []
            }
        }))
        
        pmids = await client.search_nct_id(nct_id)
        assert pmids == []
