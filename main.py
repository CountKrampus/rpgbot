from account import account_selector, get_saved_password
from browser import setup_driver
from login import login
from training import train_mode
from search import search_mode
from mining import miner_mode


def main_menu(driver):
    while True:
        print("\n" + "=" * 60 + "\nECLIPSE RPG AUTOMATION\n" + "=" * 60)
        print("\n1. I want to train\n2. I want to search\n3. A-Miner\n4. Exit")
        choice = input("\nChoose: ").strip()
        if choice == '1': train_mode(driver)
        elif choice == '2': search_mode(driver)
        elif choice == '3': miner_mode(driver)
        elif choice == '4': break
        else: print("✗ Invalid choice.")


def main():
    driver = None
    try:
        account = account_selector()
        if not account: return
        password = get_saved_password(account)
        if not password:
            print("✗ No saved password found. Please remove and re-add the account.")
            return
        driver = setup_driver()
        if not login(driver, account, password):
            print("✗ Login failed."); return
        main_menu(driver)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        if driver:
            try: driver.quit()
            except Exception: pass


if __name__ == '__main__':
    main()
