from .client import BaseClient


class VocabClient(BaseClient):
    """
    Client class for vocabulary requests.
    """

    def bulk_create(self, terms: list[dict]) -> list[dict]:
        """
        Bulk creates a list of terms.

        Args:
            terms (list[dict]): List of serialized terms.

        Returns:
            list[dict]: List of created, serialized terms.
        """
        url = f"{self.session.root_url}/vocab/api/term/bulk-create/"
        return self.session.post(url, terms).json()

    def bulk_update(self, terms: list[dict]) -> list[dict]:
        """
        Bulk updates a list of terms.

        Args:
            terms (list[dict]): List of serialized terms.

        Returns:
            list[dict]: List of updated, serialized terms.
        """
        url = f"{self.session.root_url}/vocab/api/term/bulk-update/"
        return self.session.patch(url, terms).json()

    def uids(self) -> list[tuple[int, int]]:
        """
        Get all term ids and uids.

        Returns:
            list[tuple[int,int]]: List of id, uid tuples for all terms.
        """
        url = f"{self.session.root_url}/vocab/api/term/uids/"
        return self.session.get(url).json()
