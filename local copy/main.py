from account import account_selector, get_saved_password
from browser import setup_driver
from login import login
from menus.main_menu import main_menu
import settings


def main():
    driver = None

    try:

        account = account_selector()

        if not account:
            return

        password = get_saved_password(
            account
        )

        if not password:

            print(
                "✗ No saved password found. "
                "Please remove and re-add the account."
            )

            return

        driver = setup_driver()

        if not login(
            driver,
            account,
            password,
        ):

            print(
                "✗ Login failed."
            )

            return

        settings.apply_settings(
            settings.load_settings()
        )

        main_menu(driver)

    except KeyboardInterrupt:

        print(
            "\nStopped by user."
        )

    except Exception as e:

        print(
            f"\nUnexpected error: {e}"
        )

    finally:

        if driver:

            try:
                driver.quit()

            except Exception:
                pass


if __name__ == "__main__":
    main()