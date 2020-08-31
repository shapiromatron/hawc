import os

import helium as h
import pytest

def remove_debug_menu(chrome_driver):
    # only run for actual local host
    if "localhost" in chrome_driver.current_url:
        try:
            chrome_driver.execute_script("document.getElementById(\"djDebug\").remove();")
        except:
            # eat any errors as this shouldn't flunk the test
            pass
        