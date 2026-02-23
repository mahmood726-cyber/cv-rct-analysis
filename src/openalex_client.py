import httpx
import logging

class OpenAlexClient:
    """
    Asynchronous client for interacting with the OpenAlex API.
    """
    
    BASE_URL = "https://api.openalex.org"

    def __init__(self, email=None):
        # OpenAlex encourages including an email for the 'polite pool'
        self.headers = {"User-Agent": f"CV-RCT-Pipeline (mailto:{email})"} if email else {}
        self.logger = logging.getLogger(__name__)

    async def get_work_by_pmid(self, pmid):
        """
        Fetches work metadata from OpenAlex using a PMID.
        """
        # OpenAlex uses specialized canonical IDs for PMIDs
        work_url = f"{self.BASE_URL}/works/https://pubmed.ncbi.nlm.nih.gov/{pmid}"
        
        async with httpx.AsyncClient(headers=self.headers) as client:
            try:
                response = await client.get(work_url)
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return response.json()
            except Exception as e:
                self.logger.error(f"Error fetching OpenAlex metadata for PMID {pmid}: {e}")
                return None

    def reconstruct_abstract(self, inverted_index):
        """
        OpenAlex provides abstracts in an inverted index format.
        This helper reconstructs the full string.
        """
        if not inverted_index:
            return ""
        
        word_positions = []
        for word, positions in inverted_index.items():
            for pos in positions:
                word_positions.append((pos, word))
        
        word_positions.sort()
        return " ".join([word for pos, word in word_positions])
