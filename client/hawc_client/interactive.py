from io import BytesIO
from pathlib import Path

from playwright._impl._api_structures import SetCookieParam
from playwright.async_api import Page, expect
from playwright.async_api._context_manager import PlaywrightContextManager as pcm

from .client import BaseClient
from .exceptions import HawcClientException


async def remove_dj_toolbar(page: Page):
    if await page.evaluate("document.querySelector('#djDebug')"):
        await page.evaluate("document.querySelector('#djDebug').remove()")


async def fetch_png(page: Page) -> BytesIO:
    """Helper method to download a PNG from a visualization page

    Args:
        page (Page): a page instance

    Returns:
        BytesIO: The PNG image, in bytes
    """
    await page.wait_for_load_state("load")
    await expect(page.locator(".is-loading")).to_have_count(0)
    await remove_dj_toolbar(page)
    # Check for an error
    await expect(page.get_by_test_id("visual-error")).to_have_count(0, timeout=10)

    viz_type = await page.evaluate(
        "document.querySelector('meta[name=hawc-viz-type]').dataset.vizType"
    )
    match viz_type:
        case (
            "data pivot"
            | "animal bioassay endpoint aggregation"
            | "animal bioassay endpoint crossview"
            | "risk of bias heatmap"
            | "study evaluation heatmap"
            | "risk of bias barchart"
            | "study evaluation barchart"
            | "literature tagtree"
            | "exploratory heatmap"
        ):
            download_button = page.locator("button", has=page.locator("i.fa-download"))
            download_confirm = page.locator("text=Download as a PNG")
        case "embedded external website":
            download_button = page.frame_locator("iframe").locator(
                'div[role="button"]:has-text("Download")'
            )
            download_confirm = page.frame_locator("iframe").locator('button:has-text("Image")')
        case "plotly":
            download_button = None
            download_confirm = page.locator(".js-plotly-plot .modebar-btn").first
        case "static image":
            b = await page.locator("#visual-image img").screenshot(type="png")
            return BytesIO(b)
        case _:
            raise ValueError(f"Unknown visual type: {viz_type}")

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

    def __init__(self, client: BaseClient, headless: bool = True, timeout: float | None = None):
        self.client = client
        self.headless = headless
        self.timeout = timeout

    async def __aenter__(self):
        self.playwright = await pcm().start()
        browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await browser.new_context()
        if self.timeout:
            self.context.set_default_timeout(self.timeout)
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
