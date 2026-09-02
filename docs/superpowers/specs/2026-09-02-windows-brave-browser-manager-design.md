# Windows Brave BrowserManager (Cycle A)

**Date:** 2026-09-02  
**Repository:** CountKrampus/rpgbot (workspace: Eclipse RPG Automation)  
**Status:** Approved design for the first implementation cycle

## Problem

RPGBot already centralizes production browser startup in `browser.py`, but the public API is Brave-specific (`setup_driver`, `close_driver`). Later cycles will add Chrome, Chromium, Android/Termux, and CDP. Those backends need a stable create/close surface that Eclipse modules never have to know about.

This cycle does **not** add those backends. It only names and wraps the current Windows Brave path so Windows behavior stays identical.

## Goal

Introduce `BrowserManager` in the existing `browser.py` with:

- `create(instance=None)`
- `close(driver, instance=None)`
- `restart(driver, instance=None)`
- `is_alive(driver)`

`main.py` starts and stops the browser through `BrowserManager`. Existing functions remain as thin wrappers. Brave discovery, profiles, locks, retries, timeouts, and Selenium options do not change.

## Non-goals

- Chrome, Chromium, or auto-detect
- `browser=` / `platform=` / `mode=` arguments
- Android, Termux, CDP, attach-to-existing, headless
- Browser settings menu or `settings.json` schema changes
- Moving hardcoded `BASE_DIR = Path(r"F:\New folder\eclipse")`
- Replacing Windows `tasklist` lock checks
- New `browser/` package
- Routing `database_updater.py` or `check_rare.py` through the manager
- `requirements.txt` / Termux docs

## Current production flow (must remain)

```
main.py
  → account_selector()
  → start browser for that account
  → login.login(driver, account, password)
  → settings + main_menu(driver)
  → close browser / release lock
```

Today, start/close are `setup_driver` / `close_driver` in `browser.py`. After this cycle they are `BrowserManager.create` / `BrowserManager.close`, which perform the same work.

## Placement

Keep everything in `browser.py`.

Do not create:

```
browser/__init__.py
browser/manager.py
```

`browser.py` already owns Brave paths, per-account profiles, cross-process locks, Selenium options, startup retries, and shutdown. Extracting a package in this cycle is a restructure with no behavior change.

## API

```python
class BrowserManager:
    @classmethod
    def create(cls, instance=None):
        """Start Brave for this Eclipse account.

        Same behavior as the current setup_driver():
        acquire lock, resolve Brave, use selenium_profiles/instance_<name>,
        retry startup, return a Selenium WebDriver.
        """

    @classmethod
    def close(cls, driver, instance=None):
        """Quit the Selenium session and release the account lock.

        Same behavior as the current close_driver().
        """

    @classmethod
    def restart(cls, driver, instance=None):
        """Close then create again. Persistent profile is preserved.

        Same behavior as the current restart_driver().
        The caller still re-runs login if the website session was lost.
        """

    @classmethod
    def is_alive(cls, driver):
        """True if the Selenium session still responds.

        Same behavior as the current is_driver_alive().
        """
```

No `browser`, `platform`, or `mode` parameters. Those are added when a second backend exists.

## Compatibility wrappers

Keep these public names so any external or future caller does not break:

```python
def setup_driver(instance=None):
    return BrowserManager.create(instance)

def close_driver(driver, instance=None):
    return BrowserManager.close(driver, instance)

def restart_driver(driver, instance=None):
    return BrowserManager.restart(driver, instance)

def is_driver_alive(driver):
    return BrowserManager.is_alive(driver)
```

`BrowserManager.restart` must call `cls.close` and `cls.create`, not the wrappers, so restart logic has one path.

`release_instance_lock` remains a standalone helper. `main.py` still uses it when startup acquired a lock but never returned a driver.

## `main.py` changes

- Import `BrowserManager` (and `release_instance_lock` for the failed-startup path).
- Replace `setup_driver(account)` with `BrowserManager.create(account)`.
- Replace `close_driver(driver, account)` with `BrowserManager.close(driver, account)`.

Login, settings, and menus are unchanged. They still receive a Selenium `driver`.

## Frozen internals (verbatim)

Do not rewrite these in this cycle. Move or call them; do not “improve” them.

| Piece | Current behavior |
|---|---|
| `BASE_DIR` | Hardcoded `F:\New folder\eclipse` |
| `PROFILE_ROOT` | `BASE_DIR / "selenium_profiles"` |
| `find_brave()` | First existing of two `brave.exe` Program Files paths |
| `_create_driver()` | `webdriver.Chrome(options=)` with Brave `binary_location`, `--user-data-dir`, Default profile, notification/password prefs |
| Startup | 3 retries, 2s delay, 60s page-load timeout, `is_driver_alive` check |
| Locks | `.instance.lock` + `tasklist /FI "PID eq ..."` |
| Instance names | `sanitize_instance_name` → `instance_<name>` folder |

## Modules that must not change

Eclipse automation (`login.py`, `training.py`, `capture.py`, `mining.py`, shop/search menus) must not grow `if android` / `if brave` branches.

`database_updater.py` and `check_rare.py` keep their own Chrome `webdriver.Chrome()` helpers.

`settings.py` / `settings.json` are untouched.

## Testing

Use the stdlib `unittest` module so this cycle does not add pytest or a requirements file.

**No live Brave in CI/unit tests.** Mock Selenium.

Required tests:

1. `BrowserManager.is_alive(None)` is False (same as today).
2. `setup_driver(name)` calls `BrowserManager.create(name)` and returns its result.
3. `close_driver(driver, name)` calls `BrowserManager.close(driver, name)`.
4. `restart_driver(driver, name)` calls `BrowserManager.restart(driver, name)`.
5. `is_driver_alive(driver)` calls `BrowserManager.is_alive(driver)`.
6. Existing `sanitize_instance_name` / `get_profile_path` behavior is unchanged (None/empty → `default`; unsafe characters replaced; path is `PROFILE_ROOT / instance_<name>`).

**Manual regression (Windows, existing Brave install):**

1. Start RPGBot, select a known account, confirm Brave starts with that account’s profile.
2. Confirm login still works.
3. Quit and confirm the browser closes and the lock is released.
4. Confirm a second start reuses `selenium_profiles/instance_<account>/` (session cookies still present if they were before).

A change that only adds a class but breaks login is not done.

## Definition of done

- [ ] `BrowserManager` exists in `browser.py` with create/close/restart/is_alive
- [ ] Wrappers delegate to the manager
- [ ] `main.py` uses the manager for start/close
- [ ] Unit tests pass without launching a browser
- [ ] Windows + Brave login/shutdown still works as before
- [ ] No new browser backends, settings keys, or path migration

## Next cycle (not this spec)

Windows Chrome / Chromium / Auto Detect, then browser settings and diagnostics, then a standalone Termux Chromium proof of concept.
