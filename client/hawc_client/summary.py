from io import BytesIO
from pathlib import Path

import pandas as pd
from playwright.sync_api import Page

from .client import BaseClient


def fetch_png(page: Page, is_tableau: bool = False) -> BytesIO:
    """Helper method to download a PNG from a visualization page

    Args:
        page (Page): a page instance
        is_tableau (bool, optional): If the visual is a Tableau image (default False)

    Returns:
        BytesIO: The PNG image, in bytes
    """
    if is_tableau:
        download_button = page.frame_locator("iframe").locator(
            'div[role="button"]:has-text("Download")'
        )
        download_confirm = page.frame_locator("iframe").locator('button:has-text("Image")')
    else:
        download_button = page.locator("button", has=page.locator("i.fa-download"))
        download_confirm = page.locator("text=Download as a PNG")
    download_button.click()
    with page.expect_download() as download_info:
        download_confirm.click()
        download = download_info.value
        return BytesIO(download.path().read_bytes())


PathLike = Path | str | None


def write_to_file(data: BytesIO, path: PathLike):
    """Write to a file, given a path-like object

    Args:
        data (BytesIO): _description_
        path (PathLike): _description_
    """
    match path:
        case Path():
            path.write_bytes(data.getvalue())
            return
        case str():
            Path(path).write_bytes(data.getvalue())
            return
        case None:
            return
        case _:
            raise ValueError("Unknown type", path)


class SummaryClient(BaseClient):
    """
    Client class for summary requests.
    """

    def create_visual(self, data: dict) -> dict:
        """Create a new visual

        Args:
            data (dict): Required metadata for object creation.
                - title (str): Visual title
                - slug (str): Visual identifier/URL base
                - visual_type (int): Constant representing visual type
                - published (bool): visual is published for public view
                - settings (dict): object settings (must be valid JSON)
                - assessment (int): assessment ID
                - prefilters (dict): object prefilters (must be valid JSON)
                - caption (str): Visual caption
                - sort_order (str): how results are sorted

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/summary/api/visual/"
        return self.session.post(url, data=data).json()

    def update_visual(self, visual_id: int, data: dict) -> dict:
        """Create a new visual

        Args:
            id (int): Visual identifier
            data (dict): Metadata to update
                - title (str): Visual title
                - slug (str): Visual identifier/URL base
                - visual_type (int): Constant representing visual type
                - published (bool): visual is published for public view
                - settings (dict): object settings (must be valid JSON)
                - assessment (int): assessment ID
                - prefilters (dict): object prefilters (must be valid JSON)
                - caption (str): Visual caption
                - sort_order (str): how results are sorted

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/summary/api/visual/{visual_id}/"
        return self.session.patch(url, data=data).json()

    def delete_visual(self, visual_id: int):
        """Delete a visual.

        Args:
            visual_id (int): ID of the visual to delete

        Returns:
            None: If the operation is successful there is no return value.
            If the operation is unsuccessful, an error will be raised.
        """
        url = f"{self.session.root_url}/summary/api/visual/{visual_id}/"
        self.session.delete(url)

    def get_visual(self, visual_id: int):
        """Get a visual.

        Args:
            visual_id (int): ID of the visual to read

        Returns:
            dict: The result object, if get was successful
        """
        url = f"{self.session.root_url}/summary/api/visual/{visual_id}/"
        return self.session.get(url)

    def visual_list(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves a visual list for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: Visual list
        """
        url = f"{self.session.root_url}/summary/api/visual/?assessment_id={assessment_id}"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def create_datapivot(self, data: dict) -> dict:
        """Create a new data pivot (query)

        Args:
            data (dict): Required metadata for object creation.
                - title (str): Visual title
                - slug (str): Visual identifier/URL base
                - evidence_type (int): Constant representing type of evidence used in data pivot
                     (see hawc.apps.study.constants.StudyType)
                - export_style (int): Constant representing how the level at which data are aggregated,
                     and therefore which columns and types of data are presented in the export, for use
                     in the visual (see hawc.apps.summary.constants.ExportStyle)
                - preferred_units: List of preferred dose-values IDs, in order of preference.
                     If empty, dose-units will be random for each endpoint
                     presented. This setting may used for comparing
                     percent-response, where dose-units are not needed, or for
                     creating one plot similar, but not identical, dose-units.
                - published (bool): datapivot is published for public view
                - settings (str): JSON of object settings
                - assessment (int): assessment ID
                - prefilters (str): JSON of object prefilters
                - caption (str): Data pivot caption

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/summary/api/data_pivot_query/"
        return self.session.post(url, data=data).json()

    def update_datapivot(self, datapivot_id: int, data: dict) -> dict:
        """Update an existing data pivot (query)

        Args:
            id (int): Data pivot identifier
            data (dict): Required metadata for object creation.
                - title (str): Visual title
                - slug (str): Visual identifier/URL base
                - evidence_type (int): Constant representing type of evidence used in data pivot
                     (see hawc.apps.study.constants.StudyType)
                - export_style (int): Constant representing how the level at which data are aggregated,
                     and therefore which columns and types of data are presented in the export, for use
                     in the visual (see hawc.apps.summary.constants.ExportStyle)
                - preferred_units: List of preferred dose-values IDs, in order of preference.
                     If empty, dose-units will be random for each endpoint
                     presented. This setting may used for comparing
                     percent-response, where dose-units are not needed, or for
                     creating one plot similar, but not identical, dose-units.
                - published (bool): datapivot is published for public view
                - settings (str): JSON of object settings
                - assessment (int): assessment ID
                - prefilters (str): JSON of object prefilters
                - caption (str): Data pivot caption

        Returns:
            dict: The resulting object, if update was successful
        """
        url = f"{self.session.root_url}/summary/api/data_pivot_query/{datapivot_id}/"
        return self.session.patch(url, data=data).json()

    def get_datapivot(self, datapivot_id: int):
        """Get a data pivot (query).

        Args:
            visual_id (int): ID of the visual to read

        Returns:
            dict: object, if successful

        """
        url = f"{self.session.root_url}/summary/api/data_pivot_query/{datapivot_id}/"
        return self.session.get(url)

    def delete_datapivot(self, datapivot_id: int):
        """Delete a data pivot (query).

        Args:
            visual_id (int): ID of the visual to delete

        Returns:
            None: If the operation is successful there is no return value.
            If the operation is unsuccessful, an error will be raised.
        """
        url = f"{self.session.root_url}/summary/api/data_pivot_query/{datapivot_id}/"
        self.session.delete(url)

    def datapivot_list(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves a data pivot list for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: Data Pivot list
        """
        url = f"{self.session.root_url}/summary/api/data_pivot/?assessment_id={assessment_id}"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def table_list(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves a table list for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: Data Pivot list
        """
        url = f"{self.session.root_url}/summary/api/summary-table/?assessment_id={assessment_id}"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def download_visual(
        self, id: int, is_tableau: bool = False, fn: PathLike = None, page: Page | None = None
    ) -> BytesIO:
        """Download a single visualization given a visual ID

        Args:
            id (int): The visual ID
            is_tableau (bool): Is the visual a tableau visual (default False)
            fn (PathLike, optional): If a path or string is specified, the a PNG is written to
                that location. If None (default), no data is written to a Path.
            page (Page, optional): an existing Page, if one exists

        Returns:
            BytesIO: the PNG representation of the visual, in bytes.
        """
        url = f"{self.session.root_url}/summary/visual/{id}/"
        reuse_page = page is not None
        if page is None:
            page = self.session.create_ui_page()
        page.goto(url)
        data = fetch_png(page, is_tableau)
        write_to_file(data, fn)
        if not reuse_page:
            page.close()
        return data

    def download_data_pivot(
        self, id: int, fn: PathLike = None, page: Page | None = None
    ) -> BytesIO:
        """Download a single data pivot given a data pivot ID

        Args:
            id (int): The data pivot ID
            fn (PathLike, optional): If a path or string is specified, the a PNG is written to
                that location. If None (default), no data is written to a Path.
            page (Page, optional): an existing Page, if one exists

        Returns:
            BytesIO: the PNG representation of the data pivot, in bytes.
        """
        url = f"{self.session.root_url}/summary/data-pivot/{id}/"
        reuse_page = page is not None
        if page is None:
            page = self.session.create_ui_page()
        page.goto(url)
        data = fetch_png(page)
        write_to_file(data, fn)
        if not reuse_page:
            page.close()
        return data

    def download_all_visuals(self, assessment_id: int) -> list[dict]:
        """Download all visuals for an assessment

        Args:
            id (int): The data pivot ID

        Returns:
            list[dict]: a list of visualizations
        """
        visuals = self.visual_list(assessment_id)
        dp = self.datapivot_list(assessment_id)
        visuals = pd.concat([visuals, dp]).to_dict(orient="records")
        page = self.session.create_ui_page()
        for visual in visuals:
            if "data pivot" in visual["visual_type"].lower():
                visual["png"] = self.download_data_pivot(visual["id"], page=page)
            else:
                is_tableau = "embedded external website" in visual["visual_type"].lower()
                visual["png"] = self.download_visual(visual["id"], is_tableau=is_tableau, page=page)
        return visuals
