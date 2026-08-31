from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from helpers import wait_for_document_ready


def setup_driver():
    options = Options()

    # ========================================================
    # PERSISTENT SELENIUM CHROME PROFILE
    # ========================================================

    options.add_argument(
        r"--user-data-dir=F:\New folder\eclipse\selenium_chrome_profile"
    )

    options.add_argument(
        "--profile-directory=Default"
    )

    # ========================================================
    # CHROME SETTINGS
    # ========================================================

    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument(
        "--disable-blink-features=AutomationControlled"
    )

    options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"]
    )

    options.add_experimental_option(
        "useAutomationExtension",
        False
    )

    # ========================================================
    # DISABLE PASSWORD SAVE PROMPTS
    # ========================================================

    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    }

    options.add_experimental_option(
        "prefs",
        prefs
    )

    # ========================================================
    # START CHROME
    # ========================================================

    driver = webdriver.Chrome(
        options=options
    )

    driver.set_page_load_timeout(60)

    return driver

    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        })
    except Exception:
        pass

    return driver
