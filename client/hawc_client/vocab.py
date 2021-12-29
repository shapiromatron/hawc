from typing import Dict, List, Tuple

from .client import BaseClient


class VocabClient(BaseClient):
    """
    Client class for vocabulary requests.
    """

    def bulk_create(self, terms: List[Dict]) -> List[Dict]:
        """
        Bulk creates a list of terms.

        Args:
            terms (List[Dict]): List of serialized terms.

        Returns:
            List[Dict]: List of created, serialized terms.
        """
        url = f"{self.session.root_url}/vocab/api/term/bulk-create/"
        return self.session.post(url, terms).json()

    def bulk_update(self, terms: List[Dict]) -> List[Dict]:
        """
        Bulk updates a list of terms.

        Args:
            terms (List[Dict]): List of serialized terms.

        Returns:
            List[Dict]: List of updated, serialized terms.
        """
        url = f"{self.session.root_url}/vocab/api/term/bulk-update/"
        return self.session.patch(url, terms).json()

    def uids(self) -> List[Tuple[int, int]]:
        """
        Get all term ids and uids.

        Returns:
            List[Tuple[int,int]]: List of id, uid tuples for all terms.
        """
        url = f"{self.session.root_url}/vocab/api/term/uids/"
        return self.session.get(url).json()
