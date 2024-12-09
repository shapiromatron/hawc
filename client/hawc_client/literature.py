import pandas as pd
from requests import Response

from .client import BaseClient


class LiteratureClient(BaseClient):
    """
    Client class for literature requests.
    """

    def _import(
        self, source: int, assessment_id: int, title: str, description: str, ids: list[int]
    ) -> dict:
        """
        Imports a list of IDs as literature references for the given assessment.

        Args:
            source (int): Database source (1 for PubMed, 2 for HERO)
            assessment_id (int): Assessment ID
            title (str): Title of import
            description (str): Description of import
            ids (list[int]): IDs

        Returns:
            dict: JSON response
        """
        payload = {
            "assessment": assessment_id,
            "search_type": "i",
            "source": source,
            "title": title,
            "description": description,
            "search_string": ",".join(str(id_) for id_ in ids),
        }
        url = f"{self.session.root_url}/lit/api/search/"
        return self.session.post(url, payload).json()

    def import_hero(self, assessment_id: int, title: str, description: str, ids: list[int]) -> dict:
        """
        Imports a list of HERO IDs as literature references for the given assessment.

        Args:
            assessment_id (int): Assessment ID
            title (str): Title of import
            description (str): Description of import
            ids (list[int]): HERO IDs

        Returns:
            dict: JSON response
        """
        return self._import(2, assessment_id, title, description, ids)

    def import_pubmed(
        self, assessment_id: int, title: str, description: str, ids: list[int]
    ) -> dict:
        """
        Imports a list of PubMed IDs as literature references for the given assessment.

        Args:
            assessment_id (int): Assessment ID
            title (str): Title of import
            description (str): Description of import
            ids (list[int]): PubMed IDs

        Returns:
            dict: JSON response
        """
        return self._import(1, assessment_id, title, description, ids)

    def tags(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves all of the tags for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: Assessment tags
        """
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/tags/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def get_tagtree(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves the nested tag tree for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            dict: JSON representation of the tag tree
        """
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/tagtree/"
        response_json = self.session.get(url).json()
        return response_json["tree"]

    def clone_tagtree(self, source_assessment_id: int, target_assessment_id: int) -> pd.DataFrame:
        """
        Copies the tag tree from one assessment to another.

        Args:
            source_assessment_id (int): Assessment ID to copy tag tree from
            target_assessment_id (int): Assessment ID to copy tag tree to

        Returns:
            dict: JSON representation of the new tag tree
        """
        fetch_url = f"{self.session.root_url}/lit/api/assessment/{source_assessment_id}/tagtree/"
        tree = self.session.get(fetch_url).json()

        update_url = f"{self.session.root_url}/lit/api/assessment/{target_assessment_id}/tagtree/"
        update_response_json = self.session.post(update_url, tree).json()

        return update_response_json["tree"]

    def update_tagtree(self, assessment_id: int, tags: list[dict]) -> pd.DataFrame:
        """
        Updates the tag tree.

        Args:
            assessment_id (int): Assessment ID to update
            tags (list[dict]): tag definitions. For each tag dict element, "name" is required. "slug" is
               optional. "children" is optional and should contain a recursive list containing valid tags.

        Returns:
            dict: JSON representation of the new tag tree. If errors, a JSON list containing details.
        """
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/tagtree/"
        response_json = self.session.post(url, {"tree": tags}).json()
        return response_json["tree"]

    def reference_tags(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves the literature references and their corresponding tags for a given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: References with corresponding tags
        """
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/reference-tags/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def import_reference_tags(
        self, assessment_id: int, csv: str, operation: str = "append", dry_run: bool = False
    ) -> pd.DataFrame:
        """
        Imports a CSV of reference IDs with corresponding tag IDs to the given assessment.

        Args:
            assessment_id (int): Assessment ID
            csv (str): Reference IDs to tag ID mapping. The header of this CSV string should be "reference_id,tag_id".
            operation (str, optional): Either add new references tags to existing (`append`), or replace current tag mappings (`replace`). Defaults to "append".
            dry_run (bool, optional): If set to True, runs validation checks but does not execute

        Returns:
            pd.DataFrame: All tag mappings for the selected `assessment_id`, after the requested changes
        """
        payload = {"csv": csv, "operation": operation, "dry_run": dry_run}
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/reference-tags/"
        response_json = self.session.post(url, payload).json()
        return pd.DataFrame(response_json)

    def reference_ids(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves the reference IDs and corresponding HERO/PubMed/etc IDs for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: Reference IDs and HERO/PubMed/etc IDs
        """
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/reference-ids/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def references(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves all references for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: References data
        """
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/reference-export/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def reference_user_tags(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves all user tag for all references for an assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: References user tag data
        """
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/user-tag-export/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def reference(self, reference_id: int) -> dict:
        """
        Retrieves the selected reference.

        Args:
            reference_id (int): ID of the reference to retrieve

        Returns:
            dict: JSON representation of the reference
        """
        url = f"{self.session.root_url}/lit/api/reference/{reference_id}/"
        response_json = self.session.get(url).json()
        return response_json

    def update_reference(self, reference_id: int, **kwargs) -> dict:
        """
        Updates reference with given values. Fields not passed as parameters
        are unchanged.

        Args:
            reference_id (int): ID of reference to update
            **kwargs (optional): Named parameters of fields to update in reference. Example parameters:
                title (str): title of the reference
                abstract (str): reference abstract
                tags (list[int]): tag IDs to apply to reference;
                    replaces the existing tags

        Example Usage:
            updated_reference_json = client.lit.update_reference(
                reference_id = 1,
                title = "reference",
                tags = [1,2,3]
            )

        Returns:
            dict: JSON representation of the updated reference.
        """
        url = f"{self.session.root_url}/lit/api/reference/{reference_id}/"
        response_json = self.session.patch(url, kwargs).json()
        return response_json

    def delete_reference(self, reference_id: int) -> None:
        """
        Deletes the selected reference. This also removes the reference from any
        searches/imports which may have included the reference. If data was
        extracted with this reference and it is associated with bioassay or epi
        extractions they will also be removed.

        Args:
            reference_id (int): ID of reference to delete

        Returns:
            None: If the operation is successful there is no return value.
            If the operation is unsuccessful, an error will be raised.
        """
        url = f"{self.session.root_url}/lit/api/reference/{reference_id}/"
        self.session.delete(url)

    def replace_hero(self, assessment_id: int, replace: list[list[int]]) -> None:
        """
        Replace HERO ID associated with each reference with a new HERO ID. Reference
        fields are updated using the new HERO ID's reference metadata.  This request is
        throttled; can only be executed once per minute.

        This method schedules a task to be executed when workers are available; task completion
        therefore is not guaranteed even with a successful response.

        Args:
            assessment_id (int): Assessment ID for all references in the list.
            replace (list[list[int]]): List of reference ID / new HERO ID pairings, both values
                should be integers, ex., [[reference_id, hero_id], ... ]

        Returns:
            None: If the operation is successful there is no return value.
            If the operation is unsuccessful, an error will be raised.
        """
        body = {"replace": replace}
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/replace-hero/"
        self.session.post(url, body)

    def update_references_from_hero(self, assessment_id: int) -> None:
        """
        Updates the fields of all HERO references in an assessment with the most recent metadata
        from HERO. This request is throttled; can only be executed once per minute.

        This method schedules a task to be executed when workers are available; task completion
        therefore is not guaranteed even with a successful response.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            None: If the operation is successful there is no return value.
            If the operation is unsuccessful, an error will be raised.
        """
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/update-reference-metadata-from-hero/"
        self.session.post(url)

    def create_tag(self, data: dict) -> dict:
        """
        Create a tag.

        Args:
            data (dict): required metadata for creation

        Returns:
            dict: The resulting object, if create was successful.
        """
        url = f"{self.session.root_url}/lit/api/tags/"
        response = self.session.post(url, data)
        return response.json()

    def update_tag(self, tag_id: int, data: dict) -> dict:
        """
        Update an existing tag.

        Args:
            tag_id (int): Tag ID
            data (dict): fields to update in tag

        Returns:
            dict: The resulting object, if update was successful.
        """
        url = f"{self.session.root_url}/lit/api/tags/{tag_id}/"
        response = self.session.patch(url, data)
        return response.json()

    def delete_tag(self, tag_id: int) -> Response:
        """
        Delete a tag.

        Args:
            tag_id (int): Tag ID

        Returns:
            Response: The response object.
        """
        url = f"{self.session.root_url}/lit/api/tags/{tag_id}/"
        return self.session.delete(url)

    def move_tag(self, tag_id: int, new_index: int) -> dict:
        """
        Change the order of a tag within its tagtree.

        Args:
            tag_id (int): Tag ID
            new_index: Index to place this tag in relation to its siblings in the tagtree

        Returns:
            Response: The response object.
        """
        url = f"{self.session.root_url}/lit/api/tags/{tag_id}/move/"
        body = {"newIndex": new_index}
        return self.session.patch(url, body)
