"""
Test the interactive client (iclient) for downloading images from a live website.

Initial approaches attempted to use this within the CI/CD, but due to issues with getting a live
server running and then running async methods within the django test suite coupled with playwright,
it became too problematic.

To run this script, start the django webserver using the hawc-fixture environment. Make sure that
the django debug toolbar is not enabled:

```bash
export "DJANGO_SETTINGS_MODULE=hawc.main.settings.unittest"
createdb -U hawc-fixture
python manage.py load_test_db
python scripts/test_interactive_client.py
```
"""
import asyncio
from collections.abc import Callable
from io import BytesIO
from sys import stdout

from hawc_client import HawcClient


def green_text(txt: str) -> str:
    """Make text green in stdout."""
    return f"\033[92m{txt}\033[0m"


async def check(method: Callable, id: int):
    """Run check and assert a file is returned and no exception"""
    error_msg = f"Test failed: {method.__name__}({id})"
    fn = f"{method.__name__}-{id}.png"
    resp = await method(id, fn=fn)
    assert isinstance(resp, BytesIO), error_msg
    assert len(resp.getvalue()) > 0, error_msg
    stdout.write(".")
    stdout.flush()


async def test_iclient():
    stdout.write("Starting client\n")
    client = HawcClient("http://127.0.0.1:8000")
    client.set_authentication_token("cef32b9abcbe1a6e9c8460099403e9cd77e12c79", login=True)
    async with client.interactive(headless=True) as iclient:
        stdout.write("Client startup complete; running tests\n")
        # taken from assessment #2 (public) - Chemical X
        await check(iclient.download_visual, 6)  # tagtree
        await check(iclient.download_visual, 3)  # risk of bias heatmap
        await check(iclient.download_visual, 4)  # crossview

        await check(iclient.download_data_pivot, 1)  # bioassay endpoint
        await check(iclient.download_data_pivot, 2)  # bioassay endpoint group

        # taken from assessment #1 (private) - Chemical Z
        # check permissions work
        await check(iclient.download_visual, 1)  # risk of bias heatmap

        stdout.write(green_text("\nComplete - all assertions passed!\n"))


if __name__ == "__main__":
    asyncio.run(test_iclient())
