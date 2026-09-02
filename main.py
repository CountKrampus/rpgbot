from account import account_selector, get_saved_password
from browser import setup_driver, close_driver
from login import login
from menus.main_menu import main_menu
import settings
from break_timer import initialize_break_timer


def main():
    driver = None
    account = None

    try:

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
        # Each account gets its own persistent Brave profile
        # and account lock, allowing different accounts to run
        # simultaneously without profile conflicts.
        driver = setup_driver(account)

        if not login(
            driver,
            account,
            password,
        ):

            print(
                "Γ£ù Login failed."
            )

            return

        settings.apply_settings(
            settings.load_settings()
        )

        initialize_break_timer()

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

        if driver is not None:

            try:
                close_driver(
                    driver,
                    account,
                )

            except Exception:
                pass

        elif account is not None:

            # If setup_driver() acquired the lock but failed
            # before returning a driver, make sure the lock
            # is cleaned up.
            try:
                from browser import release_instance_lock

                release_instance_lock(
                    account
                )

            except Exception:
                pass


if __name__ == "__main__":
    main()