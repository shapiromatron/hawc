"""
For all data pivots in HAWC, get an SVG and PNG for each data pivot:

```bash
export "HAWC_USERNAME=foo@bar.com"
export "HAWC_PW=foobar"

cd ~/dev/hawc/hawc
python ../scripts/scrape_data_pivots.py get-pivot-objects
python ../scripts/scrape_data_pivots.py webscrape https://hawcproject.org
```
"""
import os
import sys
import time
from pathlib import Path

import click
import django
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

FN = "data-pivots.pkl"
ROOT = str(Path(Path(__file__).parents[0] / "../hawc").resolve())
os.chdir(ROOT)
sys.path.append(ROOT)


@click.group()
def cli():
    pass


@cli.command()
def get_pivot_objects():
    os.environ["DJANGO_SETTINGS_MODULE"] = "main.settings.dev"
    django.setup()

    from summary.models import DataPivot

    data = []
    for d in DataPivot.objects.all().order_by("assessment_id"):
        data.append((d.id, d.get_absolute_url(), False, False, False, False))

    df = pd.DataFrame(data=data, columns=("id", "url", "loaded", "error", "png", "svg"))
    df.to_pickle(FN)


@cli.command()
@click.argument("base_url")
def webscrape(base_url: str):
    df = pd.read_pickle(FN)  # noqa: S301

    max_sleep = 60 * 10  # 10 min

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(2000, 1500)
    driver.implicitly_wait(max_sleep)

    url = f"{base_url}/user/login/"
    driver.get(url)

    driver.find_element_by_id("id_username").clear()
    driver.find_element_by_id("id_username").send_keys(os.environ["HAWC_USERNAME"])
    driver.find_element_by_id("id_password").clear()
    driver.find_element_by_id("id_password").send_keys(os.environ["HAWC_PW"])
    driver.find_element_by_id("submit-id-login").submit()

    for key, data in df.iterrows():
        if data.loaded is True:
            continue

        driver.implicitly_wait(max_sleep)
        url = f"{base_url}{data.url}"
        print(f"Trying {key+1} of {df.shape[0]}: {url}")
        driver.get(url)
        el = driver.find_element_by_id("dp_display")
        loading_div = driver.find_element_by_id("loading_div")
        while True:
            if not loading_div.is_displayed():
                driver.implicitly_wait(10)
                try:
                    svg = driver.find_element_by_xpath("//*[local-name()='svg']")
                    if svg:
                        df.loc[key, "loaded"] = True
                        df.loc[key, "error"] = False
                        df.loc[key, "png"] = svg.screenshot_as_png
                        df.loc[key, "svg"] = svg.get_attribute("innerHTML")

                except NoSuchElementException:
                    df.loc[key, "loaded"] = True
                    df.loc[key, "error"] = True
                    df.loc[key, "svg"] = el.get_attribute("innerHTML")

                df.to_pickle(FN)
                break

            time.sleep(0.1)


if __name__ == "__main__":
    cli()
