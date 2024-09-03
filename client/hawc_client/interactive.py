import time
from io import BytesIO
from pathlib import Path

from playwright._impl._api_structures import SetCookieParam
from playwright.async_api import Page, TimeoutError, expect
from playwright.async_api._context_manager import PlaywrightContextManager as pcm

from .client import BaseClient
from .exceptions import ContentUnavailable, HawcClientException


async def remove_dj_toolbar(page: Page):
    if await page.evaluate("document.querySelector('#djDebug')"):
        await page.evaluate("document.querySelector('#djDebug').remove()")


async def get_tableau_image(page) -> BytesIO:
    download_button = page.frame_locator("iframe").locator(
        'div[role="button"]:has-text("Download")'
    )
    download_confirm = page.frame_locator("iframe").locator('button:has-text("Image")')
    await download_button.click()
    async with page.expect_download() as download_info:
        await download_confirm.click()
    download = await download_info.value
    path = await download.path()
    return BytesIO(path.read_bytes())


async def get_plotly_image(page) -> BytesIO:
    download_confirm = page.locator(".js-plotly-plot .modebar-btn").first
    async with page.expect_download() as download_info:
        await download_confirm.click()
    download = await download_info.value
    path = await download.path()
    return BytesIO(path.read_bytes())


async def get_static_image(page) -> BytesIO:
    b = await page.locator("#visual-image img").screenshot(type="png")
    return BytesIO(b)


async def get_svg_image(page, timeout_ms) -> BytesIO:
    error_alert = page.get_by_test_id("error")
    download_button = page.locator("button", has=page.locator("i.fa-download"))
    download_confirm = page.locator("text=Download as a PNG")

    try:
        await expect(download_button.or_(error_alert)).to_be_visible(timeout=timeout_ms)
    except AssertionError as err:
        raise TimeoutError(f"Timeout - exceeded {timeout_ms}ms") from err

    if await error_alert.is_visible():
        error_text = await error_alert.inner_text()
        raise ContentUnavailable(400, error_text)

    # wait 1 second; the tagtree has startup animations
    time.sleep(1)

    await download_button.click()
    async with page.expect_download() as download_info:
        await download_confirm.click()
    download = await download_info.value
    path = await download.path()
    return BytesIO(path.read_bytes())


async def fetch_png(page: Page, timeout_ms: int) -> BytesIO:
    """Helper method to download a PNG from a visualization page

    Args:
        page (Page): a page instance
        timeout_ms (int): timeout, in milliseconds

    Returns:
        BytesIO: The PNG image, in bytes
    """
    await page.wait_for_load_state("load")
    await expect(page.locator(".is-loading")).to_have_count(0)
    await remove_dj_toolbar(page)

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
            return await get_svg_image(page, timeout_ms)
        case "embedded external website":
            return await get_tableau_image(page)
        case "plotly":
            return await get_plotly_image(page)
        case "static image":
            return await get_static_image(page)
        case _:
            raise ValueError(f"Unknown visual type: {viz_type}")


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

    def __init__(self, client: BaseClient, headless: bool = True, timeout: float = 60):
        """Start an interactive HAWC client to process content.

        Args:
            client (BaseClient): the current client; requires `login=True` to process content
                which requires authentication.
            headless (bool): Run in headless mode; defaults to True.
            timeout (float): Timeout, in seconds; defaults to 60
        """
        self.client = client
        self.headless = headless
        self.timeout = timeout * 1000  # convert from s to ms

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
        self.page.set_default_timeout(self.timeout)
        data = await fetch_png(self.page, self.timeout)
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
        self.page.set_default_timeout(self.timeout)
        data = await fetch_png(self.page, self.timeout)
        write_to_file(data, fn)
        return data
