from urllib.parse import urlencode

from requests import Response

from .client import BaseClient


class AssessmentClient(BaseClient):
    """
    Client class for assessment requests.
    """

    def public(self) -> list[dict]:
        """
        Retrieves data pertaining to all public assessments

        Returns:
            list[dict]: Public assessment data
        """
        url = f"{self.session.root_url}/assessment/api/assessment/public/"
        return self.session.get(url).json()

    def team_member(self) -> list[dict]:
        """
        Retrieves assessments where use is a team member or project manager

        Returns:
            list[dict]: Public assessment data
        """
        url = f"{self.session.root_url}/assessment/api/assessment/team-member/"
        return self.session.get(url).json()

    def create_value(self, data: dict) -> dict:
        """
        Create an assessment value.

        Args:
            data (dict): required metadata for creation

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/assessment/api/value/"
        return self.session.post(url, data).json()

    def create_detail(self, data: dict) -> dict:
        """
        Create additional details for an assessment.

        Args:
            data (dict): required metadata for creation

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/assessment/api/detail/"
        return self.session.post(url, data).json()

    def all_values(self) -> list[dict]:
        """
        Get a list of all assessment values in HAWC (admin only).

        Returns:
            list[dict]: Assessment values data
        """
        url = f"{self.session.root_url}/admin/api/reports/values/"
        return self.session.get(url).json()

    def create(self, data: dict) -> dict:
        """
        Create an assessment.

        Args:
            data (dict): required metadata for creation

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/assessment/api/assessment/"
        return self.session.post(url, data).json()

    def update(self, assessment_id: int, data: dict) -> dict:
        """
        Update an existing assessment

        Args:
            assessment_id (int): assessment ID

            data: fields to update in the assessment

        Returns:
            dict: The resulting object, if update was successful
        """
        url = f"{self.session.root_url}/assessment/api/assessment/{assessment_id}/"
        return self.session.patch(url, data).json()

    def delete(self, assessment_id: int) -> Response:
        """
        Delete a assessment

        Args:
            assessment_id (int): assessment ID

        Returns:
            Response: The response object.
        """
        url = f"{self.session.root_url}/assessment/api/assessment/{assessment_id}/"
        return self.session.delete(url)

    def effect_tag_create(self, name: str, slug: str) -> dict:
        """Create an effect tag.

        Effect tags can be associated with endpoints our health outcomes.

        Args:
            name (str): Tag name
            slug (str): Tag slug

        Returns:
            dict: The created tag
        """
        url = f"{self.session.root_url}/assessment/api/effect-tag/"
        return self.session.post(url, {"name": name, "slug": slug}).json()

    def effect_tag_list(self, name: str = "") -> dict:
        """Return a paginated list of available tags.

        If a name is specified, list is filtered to tags with the specified name.

        Args:
            name (str, optional): A search term to filter tag listing

        Returns:
            dict: a list of search results
        """
        url = f"{self.session.root_url}/assessment/api/effect-tag/"
        if name:
            url += "?" + urlencode({"name": name})
        return self.session.get(url).json()
