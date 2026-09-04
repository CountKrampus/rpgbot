from account import account_selector, get_saved_password
from browser import BrowserManager, release_instance_lock
from login import login
from menus.main_menu import main_menu
import settings
from break_timer import initialize_break_timer


def main():
    driver = None
    account = None

    try:

        settings.apply_settings(
            settings.load_settings()
        )

        account = account_selector()

        if not account:
            return

        password = get_saved_password(
            account
        )

        if not password:

            print(
                "Γ£ù No saved password found. "
                "Please remove and re-add the account."
            )

            return

        # Use the selected account name as the instance ID.
        # Each account gets its own persistent browser profile
        # and account lock, allowing different accounts to run
        # simultaneously without profile conflicts.
        # 
        # Load browser preference from settings (defaults to "auto" if not set)
        loaded_settings = settings.load_settings()
        browser_choice = loaded_settings.get("browser_name", "auto")
        
        driver = BrowserManager.create(
            account,
            browser_name=browser_choice,
        )

        if not login(
            driver,
            account,
            password,
        ):

            print(
                "Γ£ù Login failed."
            )

            return

        initialize_break_timer()

        main_menu(driver, account)

    except KeyboardInterrupt:

        print(
            "\nStopped by user."
        )

    except Exception as e:

        print(
            f"\nUnexpected error: {e}"
        )

    finally:

        if driver is not None:

            try:
                BrowserManager.close(
                    driver,
                    account,
                )

            except Exception:
                pass

        elif account is not None:

            # If create() acquired the lock but failed
            # before returning a driver, make sure the lock
            # is cleaned up.
            try:
                release_instance_lock(
                    account
                )

            except Exception:
                pass


if __name__ == "__main__":
    main()