from selenium.common.exceptions import WebDriverException


def remove_debug_menu(chrome_driver):
    # only run for actual local host
    if "localhost" in chrome_driver.current_url:
        try:
            chrome_driver.execute_script('document.getElementById("djDebug").remove();')
        except WebDriverException:
            # this can happen if the djDebug menu is missing just quitely eat don't fail tests
            pass
