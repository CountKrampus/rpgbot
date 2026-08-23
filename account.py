import os
import getpass
import keyring
from config import KEYRING_SERVICE, ACCOUNT_FILE


def get_accounts():
    accounts = []
    try:
        if os.path.exists(ACCOUNT_FILE):
            with open(ACCOUNT_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    name = line.strip()
                    if name and name not in accounts:
                        accounts.append(name)
    except Exception:
        pass
    return accounts


def save_account_name(username):
    accounts = get_accounts()
    if username not in accounts:
        accounts.append(username)
    with open(ACCOUNT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(accounts) + "\n")


def remove_account_name(username):
    accounts = [a for a in get_accounts() if a != username]
    try:
        with open(ACCOUNT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(accounts) + ("\n" if accounts else ""))
    except Exception:
        pass
    try:
        keyring.delete_password(KEYRING_SERVICE, username)
    except Exception:
        pass


def get_saved_password(username):
    try:
        return keyring.get_password(KEYRING_SERVICE, username)
    except Exception:
        return None


def save_password(username, password):
    keyring.set_password(KEYRING_SERVICE, username, password)


def add_account():
    print("\n" + "=" * 60 + "\nADD ACCOUNT\n" + "=" * 60)
    username = input("Username/ID: ").strip()
    if not username:
        print("✗ Username cannot be empty.")
        return None
    password = getpass.getpass("Password: ")
    if not password:
        print("✗ Password cannot be empty.")
        return None
    save_password(username, password)
    save_account_name(username)
    print(f"\n✓ Account '{username}' saved.")
    print("✓ Password stored securely in Windows Credential Manager.")
    return username


def account_selector():
    while True:
        accounts = get_accounts()
        print("\n" + "=" * 60 + "\nACCOUNT SELECTOR\n" + "=" * 60)
        if not accounts:
            print("No saved accounts.\n1. Add account\n2. Exit")
            choice = input("\nChoose: ").strip()
            if choice == "1":
                account = add_account()
                if account:
                    return account
            elif choice == "2":
                return None
            continue

        for i, account in enumerate(accounts, 1):
            print(f"{i}. {account}")
        add_number, remove_number, exit_number = len(accounts) + 1, len(accounts) + 2, len(accounts) + 3
        print(f"{add_number}. Add account\n{remove_number}. Remove account\n{exit_number}. Exit")
        choice = input("\nChoose: ").strip()
        try:
            number = int(choice)
        except ValueError:
            print("✗ Invalid choice.")
            continue
        if 1 <= number <= len(accounts):
            return accounts[number - 1]
        if number == add_number:
            add_account()
        elif number == remove_number:
            for i, account in enumerate(accounts, 1):
                print(f"{i}. {account}")
            try:
                n = int(input("\nAccount to remove: ").strip())
                if 1 <= n <= len(accounts):
                    account = accounts[n - 1]
                    remove_account_name(account)
                    print(f"✓ Removed '{account}'.")
            except ValueError:
                print("✗ Invalid choice.")
        elif number == exit_number:
            return None
