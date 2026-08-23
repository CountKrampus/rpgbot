import time
import random
from selenium.webdriver.common.by import By
from config import MINES_URL, WAIT_LONG
from helpers import safe_click, wait_for_document_ready
from search import find_encounter_fight, click_encounter_fight
from capture import capture_encounter


def find_mine_button(driver):
    selectors = [
        (By.CSS_SELECTOR, "button.mine-button"),
        (By.XPATH, "//button[contains(@class,'mine-button') and .//img[contains(@src,'pickaxe')]]"),
        (By.XPATH, "//button[.//img[contains(@src,'pickaxe')] and contains(normalize-space(.),'Mine')]")
    ]
    for by, xp in selectors:
        try:
            for el in driver.find_elements(by, xp):
                if el.is_displayed() and el.is_enabled(): return el
        except Exception: pass
    return None


def click_mine(driver):
    end = time.time() + WAIT_LONG
    while time.time() < end:
        el = find_mine_button(driver)
        if el:
            time.sleep(random.uniform(.5, 1))
            if safe_click(driver, el):
                print("  ✓ Mine clicked."); return True
        time.sleep(.3)
    return False


def area_cleared_detected(driver):
    try: text = driver.find_element(By.TAG_NAME, 'body').text.lower()
    except Exception: return False
    return any(x in text for x in ('area cleared','mine area cleared','mining area cleared','you have cleared','area has been cleared'))


def handle_area_cleared(driver):
    if not area_cleared_detected(driver): return False
    print("⚠ Mining area completion detected.")
    for xp in ["//button[normalize-space()='OK']", "//input[@value='OK']", "//button[normalize-space()='Continue']", "//input[@value='Continue']"]:
        try:
            for el in driver.find_elements(By.XPATH, xp):
                if el.is_displayed() and el.is_enabled() and safe_click(driver, el):
                    time.sleep(1); return True
        except Exception: pass
    return True


def click_mining_continue(driver):
    for xp in ["//button[normalize-space()='Continue']", "//input[@value='Continue']"]:
        try:
            for el in driver.find_elements(By.XPATH, xp):
                if el.is_displayed() and el.is_enabled() and safe_click(driver, el):
                    print("  ✓ Continue clicked."); time.sleep(1); return True
        except Exception: pass
    return False


def handle_mining_encounter(driver, catch_pokemon):
    if not find_encounter_fight(driver): return False
    print("\n  Pokémon encounter while mining!")
    if not catch_pokemon:
        driver.get(MINES_URL); wait_for_document_ready(driver); time.sleep(1); return True
    if not click_encounter_fight(driver): return False
    if not capture_encounter(driver): return False
    click_mining_continue(driver)
    if '/mines' not in driver.current_url:
        driver.get(MINES_URL); wait_for_document_ready(driver); time.sleep(1)
    return True


def miner_mode(driver):
    print("\n" + "=" * 60 + "\nA-MINER\n" + "=" * 60)
    choice = input("\n1. Mine and catch Pokémon\n2. Mine only\n\nChoose: ").strip()
    catch = choice != '2'
    driver.get(MINES_URL); wait_for_document_ready(driver); time.sleep(random.uniform(1.5,2.5))
    mine_count = 0
    while True:
        mine_count += 1; print(f"\n=== Mine #{mine_count} ===")
        if click_mine(driver):
            time.sleep(random.uniform(1.2,2.0))
        else:
            if handle_area_cleared(driver): print("✓ Mining area completed."); break
            if handle_mining_encounter(driver, catch): continue
            print("⚠ Mine button unavailable."); time.sleep(1); continue
        if find_encounter_fight(driver):
            if not handle_mining_encounter(driver, catch): print("✗ Mining encounter handling failed."); return
            continue
        if handle_area_cleared(driver): print("✓ Mining area completed."); break
        print("  ✓ Mining result processed."); time.sleep(random.uniform(.8,1.4))
