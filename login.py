import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config import BASE_URL, LOGIN_URL, WAIT_LONG
from helpers import normalize, page_contains, safe_click, wait_for_document_ready


def is_logged_in(driver):
    for selector in [".party-pokemon-header", ".party-pokemon-name", ".party-pokemon-level"]:
        try:
            if any(e.is_displayed() for e in driver.find_elements(By.CSS_SELECTOR, selector)):
                return True
        except Exception:
            pass
    return page_contains(driver, "Your Profile") or page_contains(driver, "Log Out")


def login(driver, username, password):
    print("\n" + "=" * 60 + "\nLOGIN\n" + "=" * 60)
    driver.get(BASE_URL)
    wait_for_document_ready(driver)
    time.sleep(1)
    if is_logged_in(driver):
        print("✓ Already logged in.")
        return True

    try:
        link = WebDriverWait(driver, WAIT_LONG).until(EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Log In']")))
        safe_click(driver, link)
    except TimeoutException:
        driver.get(LOGIN_URL)

    wait_for_document_ready(driver)
    try:
        user = WebDriverWait(driver, WAIT_LONG).until(EC.presence_of_element_located((By.ID, "L_UserID")))
        pwd = WebDriverWait(driver, WAIT_LONG).until(EC.presence_of_element_located((By.ID, "L_Password")))
        user.clear(); user.send_keys(username)
        pwd.clear(); pwd.send_keys(password)
    except TimeoutException:
        print("✗ Login form not found.")
        return False

    try:
        button = WebDriverWait(driver, WAIT_LONG).until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Login']")))
        safe_click(driver, button)
    except TimeoutException:
        print("✗ Login button not found.")
        return False

    try:
        WebDriverWait(driver, WAIT_LONG).until(is_logged_in)
        print("✓ Login successful.")
        return True
    except TimeoutException:
        print("✗ Login could not be confirmed.")
        return False
