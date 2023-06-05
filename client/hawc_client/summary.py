from io import BytesIO
from pathlib import Path

import pandas as pd
from playwright.sync_api import Page

from .client import BaseClient


def fetch_png(page: Page) -> BytesIO:
    download_button = page.locator("button", has=page.locator("i.fa-download"))
    download_confirm = page.locator("text=Download as a PNG")
    # todo check for external site
    if False:
        download_button = page.frame_locator("iframe").locator(
            'div[role="button"]:has-text("Download")'
        )
        download_confirm = page.frame_locator("iframe").locator('button:has-text("Image")')
    download_button.click()
    with page.expect_download() as download_info:
        download_confirm.click()
        download = download_info.value
        return BytesIO(download.path().read_bytes())


PathLike = Path | str | None


def write_to_file(data: BytesIO, path: PathLike):
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

    def download_visual(self, id: int, fn: PathLike = None) -> BytesIO:
        url = f"{self.session.root_url}/summary/visual/{id}/"
        page = self.session.create_ui_page()
        page.goto(url)
        data = fetch_png(page)
        write_to_file(data, fn)
        return data

    def download_data_pivot(self, id: int, fn: Path | str | None = None) -> BytesIO:
        url = f"{self.session.root_url}/summary/data-pivot/{id}/"
        page = self.session.create_ui_page()
        page.goto(url)
        data = fetch_png(page)
        write_to_file(data, fn)
        return data
