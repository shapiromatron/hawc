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
