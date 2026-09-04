# Windows Chrome, Chromium, and Auto Detect (Cycle B)

**Date:** 2026-09-02  
**Status:** Implemented on branch `windows-chrome-chromium-auto`

## Goal

Windows RPGBot can launch Brave, Chrome, or Chromium through `BrowserManager.create()`, with Auto Detect defaulting to Brave when it is installed so existing profiles keep working.

## Behavior

- `browser_name`: `auto` | `brave` | `chrome` | `chromium` (invalid values become `auto`)
- `browser_allow_fallback`: default `false`. Auto Detect always walks Brave → Chrome → Chromium. Explicit Brave/Chrome/Chromium does **not** switch unless fallback is enabled.
- Discovery: known Program Files / Program Files (x86) / LocalAppData paths, then `PATH`.
- Brave profiles stay at `selenium_profiles/instance_<account>/`.
- Chrome/Chromium use `selenium_profiles/<browser>/instance_<account>/`.
- Account locks stay on the legacy Brave instance folder so one account cannot run twice.
- Settings menu: Advanced → Browser Settings.
- `main.py` applies settings **before** browser startup so the chosen browser is used on first launch.

## Out of scope

Android, Termux, CDP, attach-to-existing, headless, portable `BASE_DIR`.

## Diagnostics (Phase 5)

`BrowserManager.test(driver)` runs Python/Selenium/detection checks, then (if a live session exists) opens a temporary tab, loads a local HTML probe, and verifies navigation, JavaScript, CSS, XPath, WebDriverWait, and typing/clicking. The Eclipse tab is restored afterward.

Settings → Advanced → Browser Settings → Test Browser.
