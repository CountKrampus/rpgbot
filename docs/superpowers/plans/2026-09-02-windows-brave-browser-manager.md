# Windows Brave BrowserManager Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wrap the existing Windows Brave Selenium path in `BrowserManager` without changing startup, profiles, locks, or login behavior.

**Architecture:** Add `BrowserManager` inside the current `browser.py` (no `browser/` package). Move the bodies of `setup_driver`, `close_driver`, `restart_driver`, and `is_driver_alive` onto classmethods `create` / `close` / `restart` / `is_alive`. Keep the old function names as one-line wrappers. Point `main.py` at the manager. Do not add Chrome, Android, CDP, settings keys, or portable `BASE_DIR`.

**Tech Stack:** Python 3, stdlib `unittest` + `unittest.mock`, existing Selenium Brave code in `browser.py`.

**Spec:** `docs/superpowers/specs/2026-09-02-windows-brave-browser-manager-design.md`

---

## File structure

| File | Responsibility |
|---|---|
| `browser.py` | Existing Brave/Windows browser module. Add `BrowserManager`; wrappers delegate to it. Internals (`find_brave`, `_create_driver`, locks, `BASE_DIR`) stay as they are. |
| `main.py` | Call `BrowserManager.create` / `close` instead of `setup_driver` / `close_driver`. |
| `tests/test_browser_manager.py` | Unit tests; no live browser. |
| `tests/__init__.py` | Empty file so `python -m unittest` can discover the package if needed. |

Do not create `browser/manager.py`. Do not modify `login.py`, automation modules, `settings.py`, `database_updater.py`, or `check_rare.py`.

Run tests from the repo root:

```bash
python -m unittest tests.test_browser_manager -v
```

Expected on a completed cycle: all tests PASS. None of them launch Brave.

---

### Task 1: Unit tests for existing name/path helpers

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_browser_manager.py`

These tests lock current `sanitize_instance_name` / `get_profile_path` behavior so the later move cannot change folders or lock names.

- [ ] **Step 1: Create the tests package files**

Create empty `tests/__init__.py`.

Create `tests/test_browser_manager.py`:

```python
import unittest
from pathlib import Path
from unittest.mock import patch
from tempfile import TemporaryDirectory

import browser


class TestSanitizeInstanceName(unittest.TestCase):

    def test_none_becomes_default(self):
        self.assertEqual(
            browser.sanitize_instance_name(None),
            "default",
        )

    def test_empty_becomes_default(self):
        self.assertEqual(
            browser.sanitize_instance_name("   "),
            "default",
        )

    def test_unsafe_characters_replaced(self):
        self.assertEqual(
            browser.sanitize_instance_name('gold:is/duck'),
            "gold_is_duck",
        )

    def test_plain_account_unchanged(self):
        self.assertEqual(
            browser.sanitize_instance_name("goldisduck"),
            "goldisduck",
        )


class TestGetProfilePath(unittest.TestCase):

    def test_profile_uses_instance_prefix(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "selenium_profiles"
            with patch.object(browser, "PROFILE_ROOT", root):
                path = browser.get_profile_path("goldisduck")
                self.assertEqual(
                    path,
                    root / "instance_goldisduck",
                )
                self.assertTrue(path.is_dir())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests — they should PASS (existing behavior)**

Run: `python -m unittest tests.test_browser_manager -v`

Expected: all `TestSanitizeInstanceName` and `TestGetProfilePath` tests PASS. If any FAIL, stop and fix the test to match current `browser.py`; do not change sanitizer behavior.

- [ ] **Step 3: Commit**

```bash
git add tests/__init__.py tests/test_browser_manager.py
git commit -m "test: lock Brave instance name and profile path behavior"
```

---

### Task 2: Failing tests for BrowserManager and wrappers

**Files:**
- Modify: `tests/test_browser_manager.py`

- [ ] **Step 1: Add failing tests**

Append these classes to `tests/test_browser_manager.py` (keep the Task 1 imports; `patch` is already imported):

```python
class TestBrowserManagerIsAlive(unittest.TestCase):

    def test_none_driver_is_not_alive(self):
        self.assertFalse(
            browser.BrowserManager.is_alive(None)
        )

    def test_is_driver_alive_delegates(self):
        with patch.object(
            browser.BrowserManager,
            "is_alive",
            return_value=True,
        ) as mock_alive:
            result = browser.is_driver_alive("driver")
            mock_alive.assert_called_once_with("driver")
            self.assertTrue(result)


class TestBrowserManagerWrappers(unittest.TestCase):

    def test_setup_driver_delegates_to_create(self):
        with patch.object(
            browser.BrowserManager,
            "create",
            return_value="driver",
        ) as mock_create:
            result = browser.setup_driver("goldisduck")
            mock_create.assert_called_once_with("goldisduck")
            self.assertEqual(result, "driver")

    def test_close_driver_delegates_to_close(self):
        with patch.object(
            browser.BrowserManager,
            "close",
        ) as mock_close:
            browser.close_driver("driver", "goldisduck")
            mock_close.assert_called_once_with(
                "driver",
                "goldisduck",
            )

    def test_restart_driver_delegates_to_restart(self):
        with patch.object(
            browser.BrowserManager,
            "restart",
            return_value="new-driver",
        ) as mock_restart:
            result = browser.restart_driver(
                "driver",
                "goldisduck",
            )
            mock_restart.assert_called_once_with(
                "driver",
                "goldisduck",
            )
            self.assertEqual(result, "new-driver")


class TestBrowserManagerRestartUsesCreateAndClose(unittest.TestCase):

    def test_restart_calls_close_then_create(self):
        with patch.object(
            browser.BrowserManager,
            "close",
        ) as mock_close, patch.object(
            browser.BrowserManager,
            "create",
            return_value="new-driver",
        ) as mock_create, patch.object(
            browser.time,
            "sleep",
        ):
            result = browser.BrowserManager.restart(
                "driver",
                "goldisduck",
            )
            mock_close.assert_called_once_with(
                "driver",
                "goldisduck",
            )
            mock_create.assert_called_once_with(
                "goldisduck",
            )
            self.assertEqual(result, "new-driver")
```

`test_restart_calls_close_then_create` patches `browser.time.sleep` so the 1-second pause in current `restart_driver` does not slow the test. If `time` is imported as `import time` in `browser.py` (it is), the patch target is `browser.time.sleep`.

- [ ] **Step 2: Run tests — they should FAIL**

Run: `python -m unittest tests.test_browser_manager -v`

Expected: Task 1 tests still PASS. New tests FAIL with `AttributeError: module 'browser' has no attribute 'BrowserManager'` (or similar). Do not implement yet.

- [ ] **Step 3: Commit**

```bash
git add tests/test_browser_manager.py
git commit -m "test: require BrowserManager create/close/restart wrappers"
```

---

### Task 3: Add BrowserManager and move function bodies

**Files:**
- Modify: `browser.py`

**Rule:** Copy existing function bodies **verbatim**. Do not change Brave paths, options, retries, lock logic, print/ANSI output, or `BASE_DIR`.

- [ ] **Step 1: Insert `BrowserManager` above the current `# SETUP DRIVER` section**

Place the class immediately before `def setup_driver` (currently around line 817). Give it the four classmethods. Implementation mapping:

1. `BrowserManager.is_alive` — body of current `is_driver_alive` (lines 706–723). Keep `is_driver_alive` in place for now; you will replace it in Step 2.

2. `BrowserManager.create` — body of current `setup_driver` (from `instance_name = sanitize_instance_name` through the final `raise RuntimeError(...)`).

3. `BrowserManager.close` — body of current `close_driver`.

4. `BrowserManager.restart` — same as current `restart_driver`, except it must call the classmethods, not the public wrappers:

```python
    @classmethod
    def restart(cls, driver, instance=None):
        """
        Restart Brave for an account.

        The persistent profile is preserved.

        The caller should perform the application's login
        procedure again if the website session was lost.
        """

        instance_name = sanitize_instance_name(
            instance
        )

        _section(
            "BROWSER RECOVERY"
        )

        _warning(
            f"Restarting Brave instance '{instance_name}'..."
        )

        cls.close(
            driver,
            instance_name,
        )

        time.sleep(
            1
        )

        new_driver = cls.create(
            instance_name
        )

        _success(
            "Browser recovery completed."
        )

        return new_driver
```

Keep the same docstring tone and ANSI helpers (`_section`, `_warning`, `_success`) as the current `restart_driver`.

Skeleton for the other methods (bodies are the existing functions, unchanged):

```python
class BrowserManager:
    """Windows Brave Selenium lifecycle. Eclipse modules receive a driver."""

    @classmethod
    def is_alive(cls, driver):
        if driver is None:
            return False
        try:
            _ = driver.current_url
            return True
        except Exception:
            return False

    @classmethod
    def create(cls, instance=None):
        # verbatim body of current setup_driver()
        ...

    @classmethod
    def close(cls, driver, instance=None):
        # verbatim body of current close_driver()
        ...

    @classmethod
    def restart(cls, driver, instance=None):
        # use cls.close / cls.create as shown above
        ...
```

- [ ] **Step 2: Replace the old functions with wrappers**

Replace `setup_driver`, `close_driver`, `restart_driver`, and `is_driver_alive` so they only delegate. Do not leave a second copy of the Brave startup loop.

```python
def is_driver_alive(driver):
    return BrowserManager.is_alive(driver)


def setup_driver(instance=None):
    return BrowserManager.create(instance)


def close_driver(driver, instance=None):
    return BrowserManager.close(driver, instance)


def restart_driver(driver, instance=None):
    return BrowserManager.restart(driver, instance)
```

Keep `wait_for_browser` as it is. It already calls `is_driver_alive`; after this step that goes through `BrowserManager.is_alive`.

Keep `find_brave`, `_create_driver`, lock helpers, and `release_instance_lock` as module-level functions. `create` / `close` still call them the same way `setup_driver` / `close_driver` did.

- [ ] **Step 3: Run tests — they should PASS**

Run: `python -m unittest tests.test_browser_manager -v`

Expected: all tests PASS.

If `test_restart_calls_close_then_create` fails because `close` is not called with the sanitized name, the test uses `"goldisduck"` which sanitizes to itself — match the actual `cls.close` / `cls.create` arguments in `restart`. Do not pass extra kwargs that the current functions do not use.

- [ ] **Step 4: Commit**

```bash
git add browser.py
git commit -m "feat: add BrowserManager around existing Brave startup"
```

---

### Task 4: Point main.py at BrowserManager

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Change imports and start/close calls**

Replace the top of `main.py`:

```python
from account import account_selector, get_saved_password
from browser import BrowserManager, release_instance_lock
from login import login
from menus.main_menu import main_menu
import settings
from break_timer import initialize_break_timer
```

Replace startup:

```python
        driver = BrowserManager.create(account)
```

Replace the `finally` close path:

```python
        if driver is not None:

            try:
                BrowserManager.close(
                    driver,
                    account,
                )

            except Exception:
                pass

        elif account is not None:

            try:
                release_instance_lock(
                    account
                )

            except Exception:
                pass
```

Do not change login, settings, or `main_menu`. Keep the failed-startup lock cleanup on `release_instance_lock` (spec: that helper stays standalone).

- [ ] **Step 2: Run unit tests again**

Run: `python -m unittest tests.test_browser_manager -v`

Expected: PASS (main.py is not imported by these tests).

- [ ] **Step 3: Manual Windows regression**

On the Windows 11 machine with Brave installed:

1. From the repo root run `python main.py`.
2. Select a saved account.
3. Confirm the existing “BROWSER STARTUP” / Brave profile messages still appear.
4. Confirm Eclipse login still works.
5. Exit the bot.
6. Confirm Brave closes and `.instance.lock` under that account’s `selenium_profiles` folder is gone.

If login fails or Brave does not start, revert `main.py` / `browser.py` and fix before committing.

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: start and stop Brave through BrowserManager"
```

---

## Self-review

**Spec coverage**

| Spec item | Task |
|---|---|
| `BrowserManager.create/close/restart/is_alive` in `browser.py` | Task 3 |
| Wrappers `setup_driver` / `close_driver` / `restart_driver` / `is_driver_alive` | Task 3 |
| `restart` calls `cls.close` then `cls.create` | Task 2 test + Task 3 |
| `main.py` uses manager | Task 4 |
| `release_instance_lock` still used on failed startup | Task 4 |
| No `browser=` / `platform=` | Not added in any task |
| Frozen Brave internals | Task 3 verbatim-move rule |
| Unit tests without live browser | Tasks 1–2 |
| Manual Windows login regression | Task 4 Step 3 |
| Leave `database_updater.py` / `check_rare.py` / settings alone | No tasks touch them |

**Placeholders:** none. Restart sleep is patched at `browser.time.sleep`.

**API names:** `create`, `close`, `restart`, `is_alive` — consistent across spec, tests, and `main.py`.
