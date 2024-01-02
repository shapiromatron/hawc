from io import BytesIO, StringIO
from pathlib import Path

import pandas as pd
from playwright.sync_api import Page
from playwright.sync_api._context_manager import PlaywrightContextManager as pcm

from .session import HawcSession


class BaseClient:
    """
    Base client class.

    Initiates with a given HawcSession object.
    """

    def __init__(self, session: HawcSession):
        self.session = session

    def _csv_to_df(self, csv: str) -> pd.DataFrame:
        """
        Takes a CSV string and returns the pandas DataFrame representation of it.

        Args:
            csv (str): CSV string

        Returns:
            pd.DataFrame: DataFrame from CSV
        """
        csv_io = StringIO(csv)
        return pd.read_csv(csv_io)


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


class InteractiveHawcClient:
    """
    A context manager for downloading assessment visuals.
    """

    def __init__(self, client: BaseClient):
        self.client = client

    def __enter__(self):
        self.playwright = pcm().start()
        self.web_browser = self.playwright.chromium.launch(headless=True)
        self.page = self.web_browser.new_page()
        if token := self.client.session._session.headers.get("Authorization"):
            self.page.set_extra_http_headers({"Authorization": str(token)})
        return self

    def download_visual(self, id: int, is_tableau: bool = False, fn: PathLike = None) -> BytesIO:
        """Download a single visualization given a visual ID

        Args:
            id (int): The visual ID
            is_tableau (bool): Is the visual a tableau visual (default False)
            fn (PathLike, optional): If a path or string is specified, the PNG is written to
                that location. If None (default), no data is written to a Path.

        Returns:
            BytesIO: the PNG representation of the visual, in bytes.
        """
        url = f"{self.client.session.root_url}/summary/visual/{id}/"
        self.page.goto(url)
        data = fetch_png(self.page, is_tableau)
        write_to_file(data, fn)

        return data

    def download_data_pivot(self, id: int, fn: PathLike = None) -> BytesIO:
        """Download a single data pivot given a data pivot ID

        Args:
            id (int): The data pivot ID
            fn (PathLike, optional): If a path or string is specified, the a PNG is written to
                that location. If None (default), no data is written to a Path.

        Returns:
            BytesIO: the PNG representation of the data pivot, in bytes.
        """
        url = f"{self.client.session.root_url}/summary/data-pivot/{id}/"
        self.page.goto(url)
        data = fetch_png(self.page)
        write_to_file(data, fn)
        return data

    def __exit__(self, *args) -> None:
        self.playwright.stop()
