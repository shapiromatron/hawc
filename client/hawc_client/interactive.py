from io import BytesIO
from pathlib import Path

from playwright._impl._api_structures import SetCookieParam
from playwright.async_api import Page, expect
from playwright.async_api._context_manager import PlaywrightContextManager as pcm

from .client import BaseClient
from .exceptions import HawcClientException


async def fetch_png(page: Page) -> BytesIO:
    """Helper method to download a PNG from a visualization page

    Args:
        page (Page): a page instance

    Returns:
        BytesIO: The PNG image, in bytes
    """
    download_button = None

    await page.wait_for_load_state("load")
    await expect(page.locator(".is-loading")).to_be_hidden()

    # has plotly
    if await page.evaluate("document.querySelector('.visualization .js-plotly-plot') !== null"):
        await page.locator(".js-plotly-plot").hover()
        async with page.expect_download() as download_info:
            await page.locator(".js-plotly-plot .modebar-btn").first.click(force=True)
        download = await download_info.value
        path = await download.path()
        if path is None:
            raise ValueError("Download failed")
        return BytesIO(path.read_bytes())

    # has tableau
    elif await page.evaluate("document.querySelector('.tableau-viz') !== null"):
        download_button = page.frame_locator("iframe").locator(
            'div[role="button"]:has-text("Download")'
        )
        download_confirm = page.frame_locator("iframe").locator('button:has-text("Image")')

    # has d3-based image
    elif await page.evaluate(
        "document.querySelector('.visualization svg') || document.querySelector('#dp_display > svg') !== null"
    ):
        download_button = page.locator("button", has=page.locator("i.fa-download"))
        download_confirm = page.locator("text=Download as a PNG")

    # has image
    elif await page.evaluate("document.querySelector('#visual-image img') !== null"):
        b = await page.locator("#visual-image img").screenshot(type="png")
        return BytesIO(b)

    else:
        raise ValueError("Cannot find an image to download.")

    if download_button:
        await download_button.click()
    async with page.expect_download() as download_info:
        await download_confirm.click()
    download = await download_info.value
    path = await download.path()
    if path is None:
        raise ValueError("Download failed")
    return BytesIO(path.read_bytes())


PathLike = Path | str | None


def write_to_file(data: BytesIO, path: PathLike) -> None:
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
        cookies = [
            SetCookieParam(name=k, value=v, url=self.client.session.root_url)
            for k, v in self.client.session._session.cookies.items()
        ]
        if not cookies:
            raise HawcClientException(
                403,
                "No cookies found on client session;\nwhen setting authorization token; set login to True",
            )
        await self.context.add_cookies(cookies)
        return self

    async def __aexit__(self, *args) -> None:
        await self.context.close()
        await self.playwright.stop()

    async def download_visual(self, id: int, fn: PathLike = None) -> BytesIO:
        """Download a PNG visualization given a visual ID

        Args:
            id (int): The visual ID
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
        data = await fetch_png(self.page)
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
        # attempt to fetch PNG
        data = await fetch_png(self.page)
        write_to_file(data, fn)
        return data
