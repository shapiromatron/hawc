import warnings
from io import BytesIO, StringIO
from pathlib import Path

import pandas as pd
from playwright._impl._api_structures import SetCookieParam
from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api._context_manager import PlaywrightContextManager as pcm

from .exceptions import HawcClientException
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


async def fetch_png(page: Page, is_tableau: bool = False) -> BytesIO:
    """Helper method to download a PNG from a visualization page

    Args:
        page (Page): a page instance
        is_tableau (bool, optional): If the visual is a Tableau image (default False)

    Returns:
        BytesIO: The PNG image, in bytes
    """
    try:
        if await page.wait_for_selector("#djHideToolBarButton", strict=True, timeout=1000):
            await page.locator("#djHideToolBarButton").click()
    except PlaywrightTimeoutError:
        pass

    if is_tableau:
        download_button = page.frame_locator("iframe").locator(
            'div[role="button"]:has-text("Download")'
        )
        download_confirm = page.frame_locator("iframe").locator('button:has-text("Image")')
    else:
        download_button = page.locator("button", has=page.locator("i.fa-download"))
        download_confirm = page.locator("text=Download as a PNG")
    await download_button.click()
    async with page.expect_download() as download_info:
        await download_confirm.click()
    download = await download_info.value
    path = await download.path()
    if path is None:
        raise ValueError("Download failed")
    return BytesIO(path.read_bytes())


PathLike = Path | str | None


def write_to_file(data: BytesIO, path: PathLike):
    """Write to a file, given a path-like object"""
    if path is None:
        return
    if isinstance(path, str):
        path = Path(path)
    path.write_bytes(data.getvalue())


class InteractiveHawcClient:
    """
    A context manager for downloading assessment visuals.
    """

    def __init__(self, client: BaseClient, headless: bool = True):
        self.client = client
        self.headless = headless

    async def __aenter__(self):
        self.playwright = await pcm().start()
        browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await browser.new_context()
        self.page = await self.context.new_page()
        # if client has a token, establish a cookie-based session
        if token := self.client.session._session.headers.get("Authorization"):
            await self.page.set_extra_http_headers({"Authorization": str(token)})
            await self.page.goto(f"{self.client.session.root_url}/user/api/validate-token/?login=1")
            await self.page.set_extra_http_headers({})
        # if client is already in a cookie-based session, copy the cookies
        else:
            cookies = [
                SetCookieParam(name=k, value=v, url=self.client.session.root_url)
                for k, v in self.client.session._session.cookies.items()
            ]
            if cookies == []:
                warnings.warn(
                    "Unable to login. Unable to access unpublished assessments or visuals.",
                    stacklevel=1,
                )
                return self
            await self.context.add_cookies(cookies)
        return self

    async def __aexit__(self, *args) -> None:
        await self.context.close()
        await self.playwright.stop()

    async def download_visual(
        self, id: int, is_tableau: bool = False, fn: PathLike = None
    ) -> BytesIO:
        """Download a PNG visualization given a visual ID

        Args:
            id (int): The visual ID
            is_tableau (bool): Is the visual a tableau visual (default False)
            fn (PathLike, optional): If a path or string is specified, the PNG is written to
                that location. If None (default), no data is written to a Path.

        Returns:
            BytesIO: the PNG representation of the visual, in bytes.
        """
        url = f"{self.client.session.root_url}/summary/visual/{id}/"
        # ensure response is OK before waiting
        response = await self.page.goto(url)
        if response and not response.ok:
            raise HawcClientException(response.status, response.status_text)
        data = await fetch_png(self.page, is_tableau)
        write_to_file(data, fn)
        return data

    async def download_data_pivot(self, id: int, fn: PathLike = None) -> BytesIO:
        """Download a PNG data pivot given a data pivot ID

        Args:
            id (int): The data pivot ID
            fn (PathLike, optional): If a path or string is specified, the a PNG is written to
                that location. If None (default), no data is written to a Path.

        Returns:
            BytesIO: the PNG representation of the data pivot, in bytes.
        """
        url = f"{self.client.session.root_url}/summary/data-pivot/{id}/"
        # ensure response is OK before waiting
        response = await self.page.goto(url)
        if response and not response.ok:
            raise HawcClientException(response.status, response.status_text)
        data = await fetch_png(self.page)
        write_to_file(data, fn)
        return data
