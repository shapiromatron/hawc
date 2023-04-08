import pandas as pd

from .client import BaseClient


class StudyClient(BaseClient):
    """
    Client class for study requests.
    """

    def create(self, reference_id: int, data: dict | None = None) -> dict:
        """
        Creates a study using a given reference ID.

        Args:
            reference_id (int): Reference ID to create study from.
            data (dict, optional): Dict containing any additional field/value pairings for the study.
                Possible pairings are:
                    short_citation (str): Short study citation, can be used as identifier.
                    full_citation (str): Complete study citation.
                    bioassay: bool (study contains animal bioassay data)
                    epi: bool (study contains epidemiology data)
                    epi_meta: bool (study contains epidemiology meta-analysis data)
                    in_vitro: bool (study contains in-vitro data)
                    coi_reported: int (COI reported, see
                        hawc.apps.study.constants.CoiReported for choices)
                    coi_details: str (COI details; use the COI declaration when available)
                    funding_source: str (any funding source information)
                    study_identifier: str (reference descriptor for assessment-tracking,
                        for example, "{Author, year, #EndNoteNumber}")
                    contact_author: bool (was the author contacted for clarification/additional data)
                    ask_author: str (correspondence details)
                    published: bool (study, evaluation, and extraction details may be visible to permitted users)
                    summary: str (often left blank, used to add comments on data extration)
                    editable: bool (project-managers/team-members allowed to edit this study)
                Defaults to {empty}.

        Returns:
            dict: JSON of the created study
        """
        if data is None:
            data = {}
        data["reference_id"] = reference_id

        url = f"{self.session.root_url}/study/api/study/"
        return self.session.post(url, data).json()

    def studies(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves all studies for the given assessment.
        Args:
            assessment_id (int): Assessment ID
        Returns:
            pd.DataFrame: A dataframe for a study
        """
        url = f"{self.session.root_url}/study/api/study/?assessment_id={assessment_id}"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def create_from_identifier(
        self, db_type: str, db_id: str | int, assessment_id: int, **kwargs
    ) -> dict:
        """
        Creates a study using the given identifier.
        The identifier and reference are also created as needed.

        Args:
            db_type (str): Database type (HERO, PUBMED, DOI)
            db_id (Union[str,int]): Database ID
            assessment_id (int): Assessment ID to create the study under

        Returns:
            dict: JSON of the created study
        """
        payload = {"db_type": db_type, "db_id": db_id, "assessment_id": assessment_id, **kwargs}
        url = f"{self.session.root_url}/study/api/study/create-from-identifier/"
        return self.session.post(url, payload).json()
