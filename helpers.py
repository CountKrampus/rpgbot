import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException, WebDriverException, TimeoutException
from config import WAIT_LONG


def normalize(text):
    if text is None:
        return ""
    return " ".join(text.split()).strip().lower()


def human_like_click(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center'});", element)
        ActionChains(driver).move_to_element(element).pause(random.uniform(0.15, 0.35)).click().perform()
        return True
    except Exception:
        try:
            driver.execute_script("arguments[0].click();", element)
            return True
        except Exception:
            return False


def safe_click(driver, element):
    try:
        return human_like_click(driver, element)
    except (StaleElementReferenceException, ElementClickInterceptedException, WebDriverException):
        return False


def wait_for_document_ready(driver, timeout=WAIT_LONG):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") in ("interactive", "complete")
        )
    except Exception:
        pass


def page_contains(driver, text):
    try:
        return normalize(text) in normalize(driver.page_source)
    except Exception:
        return False


def visible_enabled(elements):
    for element in elements:
        try:
            if element.is_displayed() and element.is_enabled():
                yield element
        except StaleElementReferenceException:
            continue


def wait_and_click_exact_text(driver, text, tags="button|input|a", timeout=WAIT_LONG):
    xpath = f"//{tags}[normalize-space(.)={repr(text)}]"
    try:
        element = WebDriverWait(driver, timeout).until(
            lambda d: next(iter(visible_enabled(d.find_elements(By.XPATH, xpath))), None)
        )
        return safe_click(driver, element) if element else False
    except Exception:
        return False
