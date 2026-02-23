import httpx
import logging

class PubMedClient:
    """
    Asynchronous client for interacting with the PubMed Entrez API.
    """
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self, api_key=None):
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)

    async def search_nct_id(self, nct_id):
        """
        Searches PubMed for a specific NCT ID and returns a list of PMIDs.
        """
        search_url = f"{self.BASE_URL}/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": nct_id,
            "retmode": "json"
        }
        if self.api_key:
            params["api_key"] = self.api_key

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(search_url, params=params)
                response.raise_for_status()
                data = response.json()
                pmids = data.get("esearchresult", {}).get("idlist", [])
                return pmids
            except Exception as e:
                self.logger.error(f"Error searching PubMed for {nct_id}: {e}")
                return []
