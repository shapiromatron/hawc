import pandas as pd
from requests import Response

from .client import BaseClient


class EpiV2Client(BaseClient):
    """
    Client class for epidemiology v2 requests.
    """

    def metadata(self) -> dict:
        """
        Retrieves field choices for all epiv2 models.

        Returns:
            dict: Model metadata
        """
        url = f"{self.session.root_url}/epidemiology/api/metadata/"
        return self.session.get(url).json()

    def data(self, assessment_id: int, retrieve_unpublished_data: bool = False) -> pd.DataFrame:
        """
        Retrieves flat epidemiology v2 data export for the given assessment.

        Args:
            assessment_id (int): Assessment ID
            retrieve_unpublished_data (bool): include unpublished data in returned DataFrame

        Returns:
            pd.DataFrame: Epidemiology data
        """
        url = f"{self.session.root_url}/epidemiology/api/assessment/{assessment_id}/export/"
        if retrieve_unpublished_data:
            url += "?unpublished=true"

        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def get_designs_for_assessment(self, assessment_id: int, page: int = 1) -> pd.DataFrame:
        """
        Retrieves all of the designs for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: design data
        """
        url = f"{self.session.root_url}/epidemiology/api/design/?assessment_id={assessment_id}&page={page}"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def get_designs_for_study(
        self, assessment_id: int, study_id: int, page: int = 1
    ) -> pd.DataFrame:
        """
        Retrieves all of the designs for the given study.

        Args:
            assessment_id (int): Assessment ID
            study_id (int): Study ID

        Returns:
            pd.DataFrame: design data
        """
        url = f"{self.session.root_url}/epidemiology/api/design/?assessment_id={assessment_id}&study={study_id}&page={page}"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def get_design(self, design_id: int) -> dict:
        """
        Retrieves data for a single design

        Args:
            design_id (int): design ID

        Returns:
            dict: design data
        """
        url = f"{self.session.root_url}/epidemiology/api/design/{design_id}/"
        return self.session.get(url).json()

    def create_design(self, data: dict) -> dict:
        """
        Create a new design

        Args:
            data (dict): fields to create on the design. Keys:
                study_id (int): id of the associated study
                study_design (str): design (predefined choices: 'Cohort', 'Case-control', etc.)
                age_profile (list[str]): age profile (predefined choices: 'Adults', 'Pregnant women', etc.)
                source (str): source (predefined choices: 'General population', Occupational', etc.)
                sex (str): sex (predefined choices: 'Female', 'Not reported', etc.)
                countries (list[str]): list of country codes to associate with the design
                region (str): other geographic information (free-text)
                summary (str): description of the study population (free-text)
                study_name (str): study name assigned by the authors (free-text)
                age_description (str): population age details (free-text)
                race (str): population race/ethnicity (free-text)
                participant_n (int): total # of participants enrolled in the study
                years_enrolled (str): years of enrollment (free-text)
                years_followup (str): years/length of follow-up (free-text)
                criteria (str): inclusion/exclusion criteria (free-text)
                susceptibility (str): notes on if study presents information for potentially susceptible/vulnerable populations or sub-populations (free-text)
                comments (str): comments (free-text)

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epidemiology/api/design/"
        return self.session.post(url, data).json()

    def update_design(self, design_id: int, data: dict) -> dict:
        """
        Update an existing design

        Args:
            design_id (int): design ID
            data: fields to update in the design
                See "create_design" docstring for example fields.

        Returns:
            dict: The resulting object, if update was successful
        """

        url = f"{self.session.root_url}/epidemiology/api/design/{design_id}/"
        return self.session.patch(url, data).json()

    def delete_design(self, design_id: int) -> Response:
        """
        Delete a design

        Args:
            design_id (int): design ID

        Returns:
            Response: The response object.
        """
        url = f"{self.session.root_url}/epidemiology/api/design/{design_id}/"
        return self.session.delete(url)

    def get_chemical(self, chemical_id: int) -> dict:
        """
        Retrieves data for a single chemical

        Args:
            chemical_id (int): chemical ID

        Returns:
            dict: chemical data
        """
        url = f"{self.session.root_url}/epidemiology/api/chemical/{chemical_id}/"
        return self.session.get(url).json()

    def create_chemical(self, data: dict) -> dict:
        """
        Create a new chemical

        Args:
            data (dict): fields to create on the chemical. Keys:
                design (int): id of the associated design
                name (str): name of the chemical
                dsstox_id (str): DSSTox substance identifier

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epidemiology/api/chemical/"
        return self.session.post(url, data).json()

    def update_chemical(self, chemical_id: int, data: dict) -> dict:
        """
        Update an existing chemical

        Args:
            chemical_id (int): chemical ID
            data: fields to update in the chemical
                See "create_chemical" docstring for example fields.

        Returns:
            dict: The resulting object, if update was successful
        """

        url = f"{self.session.root_url}/epidemiology/api/chemical/{chemical_id}/"
        return self.session.patch(url, data).json()

    def delete_chemical(self, chemical_id: int) -> Response:
        """
        Delete a chemical

        Args:
            chemical_id (int): chemical ID

        Returns:
            Response: The response object.
        """
        url = f"{self.session.root_url}/epidemiology/api/chemical/{chemical_id}/"
        return self.session.delete(url)

    def get_exposure(self, exposure_id: int) -> dict:
        """
        Retrieves data for a single exposure

        Args:
            exposure_id (int): exposure ID

        Returns:
            dict: exposure data
        """
        url = f"{self.session.root_url}/epidemiology/api/exposure/{exposure_id}/"
        return self.session.get(url).json()

    def create_exposure(self, data: dict) -> dict:
        """
        Create a new exposure

        Args:
            data (dict): fields to create on the exposure. Keys:
                design (int): id of the associated design
                name (str): unique name for the exposure (free-text)
                measurement_type (list[str]): measurement types (predefined choices: 'Biomonitoring', 'Air', etc.)
                measurement_timing (str): age, other timing, cross-sectional, etc. (free-text)
                exposure_route (str): most appropriate route (predefined choices: 'Inhalation', 'Oral', etc.)
                measurement_method (str): method used to measure exposure (free-text)
                comments (str): general comments (free-text)
                biomonitoring_matrix (str): if measurement_type does not includes 'Biomonitoring', use empty string (free-text)
                biomonitoring_source (str): if measurement_type does not include 'Biomonitoring', use empty string (free-text)

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epidemiology/api/exposure/"
        return self.session.post(url, data).json()

    def update_exposure(self, exposure_id: int, data: dict) -> dict:
        """
        Update an existing exposure

        Args:
            exposure_id (int): exposure ID
            data: fields to update in the exposure
                See "create_exposure" docstring for example fields.

        Returns:
            dict: The resulting object, if update was successful
        """

        url = f"{self.session.root_url}/epidemiology/api/exposure/{exposure_id}/"
        return self.session.patch(url, data).json()

    def delete_exposure(self, exposure_id: int) -> Response:
        """
        Delete an exposure

        Args:
            exposure_id (int): exposure ID

        Returns:
            Response: The response object.
        """
        url = f"{self.session.root_url}/epidemiology/api/exposure/{exposure_id}/"
        return self.session.delete(url)

    def get_exposure_level(self, exposure_level_id: int) -> dict:
        """
        Retrieves data for a single exposure level

        Args:
            exposure_level_id (int): exposure level ID

        Returns:
            dict: exposure level data
        """
        url = f"{self.session.root_url}/epidemiology/api/exposure-level/{exposure_level_id}/"
        return self.session.get(url).json()

    def create_exposure_level(self, data: dict) -> dict:
        """
        Create a new exposure level

        Args:
            data (dict): fields to create on the exposure level. Keys:
                design (int): id of the associated design
                chemical_id (int): id of the associated chemical
                exposure_measurement_id (int): id of the associated exposure
                name (str): unique name for the exposure level (free-text)
                sub_population (str): subgroup within the study population (free-text)
                median (float)
                mean (float)
                variance (float)
                variance_type (str): measure of variation reported (predefined choices: 'N/A', 'SD', etc.)
                units (str): (free-text)
                ci_lcl (str): lower interval (free-text, non-numeric values should be limited to '<', 'LOD', etc.)
                percentile_25 (str): 25th percentile (free-text, non-numeric values should be limited to '<', 'LOD', etc.)
                percentile_75 (str): 75th percentile (free-text, non-numeric values should be limited to '<', 'LOD', etc.)
                ci_ucl (str): upper interval (free-text, non-numeric values should be limited to '<', 'LOD', etc.)
                ci_type (str): lower/upper interval type (predefined choices: 'Rng', 'P90', 'Oth', etc.)
                negligible_exposure (str): % of population without measurable exposure (free-text)
                data_location (str): e.g. table number (free-text)
                comments (str): general comments (free-text)

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epidemiology/api/exposure-level/"
        return self.session.post(url, data).json()

    def update_exposure_level(self, exposure_level_id: int, data: dict) -> dict:
        """
        Update an existing exposure level

        Args:
            exposure_level_id (int): exposure level ID
            data: fields to update in the exposure level
                See "create_exposure_level" docstring for example fields.

        Returns:
            dict: The resulting object, if update was successful
        """

        url = f"{self.session.root_url}/epidemiology/api/exposure-level/{exposure_level_id}/"
        return self.session.patch(url, data).json()

    def delete_exposure_level(self, exposure_level_id: int) -> Response:
        """
        Delete an exposure level

        Args:
            exposure_level_id (int): exposure level ID

        Returns:
            Response: The response object.
        """
        url = f"{self.session.root_url}/epidemiology/api/exposure-level/{exposure_level_id}/"
        return self.session.delete(url)

    def get_outcome(self, outcome_id: int) -> dict:
        """
        Retrieves data for a single outcome

        Args:
            outcome_id (int): outcome ID

        Returns:
            dict: outcome data
        """
        url = f"{self.session.root_url}/epidemiology/api/outcome/{outcome_id}/"
        return self.session.get(url).json()

    def create_outcome(self, data: dict) -> dict:
        """
        Create a new outcome

        Args:
            data (dict): fields to create on the outcome. Keys:
                design (int): id of the associated design
                system (str): most relevant system (predefined choices: 'CA'/'Cancer', 'DE'/'Dermal', etc.)
                effect (str): health effect of interest (free-text)
                effect_detail (str): optional additional effect specification (free-text)
                endpoint (str): unique name for the specific endpoint/outcome being measure (free-text)
                comments (str): comments (free-text)

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epidemiology/api/outcome/"
        return self.session.post(url, data).json()

    def update_outcome(self, outcome_id: int, data: dict) -> dict:
        """
        Update an existing outcome

        Args:
            outcome_id (int): outcome ID
            data: fields to update in the outcome
                See "create_outcome" docstring for example fields.

        Returns:
            dict: The resulting object, if update was successful
        """

        url = f"{self.session.root_url}/epidemiology/api/outcome/{outcome_id}/"
        return self.session.patch(url, data).json()

    def delete_outcome(self, outcome_id: int) -> Response:
        """
        Delete an outcome

        Args:
            outcome_id (int): outcome ID

        Returns:
            Response: The response object.
        """
        url = f"{self.session.root_url}/epidemiology/api/outcome/{outcome_id}/"
        return self.session.delete(url)

    def get_adjustment_factor(self, adjustment_factor_id: int) -> dict:
        """
        Retrieves data for a single adjustment factor

        Args:
            adjustment_factor_id (int): adjustment factor ID

        Returns:
            dict: adjustment factor data
        """
        url = f"{self.session.root_url}/epidemiology/api/adjustment-factor/{adjustment_factor_id}/"
        return self.session.get(url).json()

    def create_adjustment_factor(self, data: dict) -> dict:
        """
        Create a new adjustment factor

        Args:
            data (dict): fields to create on the adjustment factor. Keys:
                design (int): id of the associated design
                name (str): unique name for the adjustment factor (free-text)
                description (str): comma-separated list of covariates, using uniform language across studies if possible (free-text)
                comments (str): general comments (free-text)

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epidemiology/api/adjustment-factor/"
        return self.session.post(url, data).json()

    def update_adjustment_factor(self, adjustment_factor_id: int, data: dict) -> dict:
        """
        Update an existing adjustment factor

        Args:
            adjustment_factor_id (int): adjustment factor ID
            data: fields to update in the adjustment factor
                See "create_adjustment_factor" docstring for example fields.

        Returns:
            dict: The resulting object, if update was successful
        """

        url = f"{self.session.root_url}/epidemiology/api/adjustment-factor/{adjustment_factor_id}/"
        return self.session.patch(url, data).json()

    def delete_adjustment_factor(self, adjustment_factor_id: int) -> Response:
        """
        Delete an adjustment factor

        Args:
            adjustment_factor_id (int): adjustment factor ID

        Returns:
            Response: The response object.
        """
        url = f"{self.session.root_url}/epidemiology/api/adjustment-factor/{adjustment_factor_id}/"
        return self.session.delete(url)

    def get_data_extraction(self, data_extraction_id: int) -> dict:
        """
        Retrieves data for a single data extraction

        Args:
            data_extraction_id (int): data extraction ID

        Returns:
            dict: data extraction data
        """
        url = f"{self.session.root_url}/epidemiology/api/data-extraction/{data_extraction_id}/"
        return self.session.get(url).json()

    def create_data_extraction(self, data: dict) -> dict:
        """
        Create a new data extraction

        Args:
            data (dict): fields to create on the data extraction. Keys:
                design (int): id of the associated design
                outcome_id (int): id of the associated outcome
                exposure_level_id (int): id of the associated exposure level
                factors_id (int): id of the associated adjustment factors
                sub_population (str): subgroup within the study population (free-text)
                outcome_measurement_timing (str): age or other timing, "cross-sectional", etc. (free-text)
                effect_estimate_type (str): type of effect estimate (predefined choices: 'Odds Ratio'/'OR', 'Absolute Risk %'/'AR', etc.)
                effect_estimate (float): value of effect estimate
                ci_lcl (float): lower bound
                ci_ucl (float): upper bound
                ci_type (str): lower/upper bound type (predefined choices: 'P90', '5th/95h percentile', etc.)
                units (str): bound units (free-text)
                variance_type (str): type of variance estimate (predefined choices: 'SD', 'SE', 'NA', etc.)
                variance (float): value of variance estimate
                n (int): n
                p_value (str): p-value (free-text)
                significant (str): was the data extraction statistically significant? (predefined choices: 'NR', 'Yes', etc.)
                group (str): results group for linking sets of results (free-text)
                exposure_rank (int): value for ordering linked sets of results
                exposure_transform (str): exposure transform (predefined choices: 'log10', 'squared', 'other', etc.)
                outcome_transform (str): outcome transform (predefined choices: 'log10', 'squared', 'other', etc.)
                confidence (str): overall confidence rating for the endpoint being extracted (free-text)
                adverse_direction (str): direction of effect that would be adverse if observed (predefined choices: 'unknown', 'up', 'any', etc.)
                data_location (str): e.g. table number (free-text)
                effect_description (str): description of the effect estimate with units, including comparison being made. (free-text)
                statistical_method (str): brief description of the statistical analysis method (free-text)
                comments (str): general comments (free-text)

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epidemiology/api/data-extraction/"
        return self.session.post(url, data).json()

    def update_data_extraction(self, data_extraction_id: int, data: dict) -> dict:
        """
        Update an existing data extraction

        Args:
            data_extraction_id (int): data extraction ID
            data: fields to update in the data extraction
                See "create_data_extraction" docstring for example fields.

        Returns:
            dict: The resulting object, if update was successful
        """

        url = f"{self.session.root_url}/epidemiology/api/data-extraction/{data_extraction_id}/"
        return self.session.patch(url, data).json()

    def delete_data_extraction(self, data_extraction_id: int) -> Response:
        """
        Delete an data extraction

        Args:
            data_extraction_id (int): data extraction ID

        Returns:
            Response: The response object.
        """
        url = f"{self.session.root_url}/epidemiology/api/data-extraction/{data_extraction_id}/"
        return self.session.delete(url)
