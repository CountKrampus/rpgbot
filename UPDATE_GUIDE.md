# RPGBot Auto-Update Guide

## Overview

The `update.py` script automatically updates RPGBot from GitHub using git. It's the easiest way to stay current with the latest features and bug fixes.

---

## Quick Start

### One-Time Setup (First Time Only)

If you downloaded the bot as a ZIP file, you need to set up git first:

```bash
# 1. Backup your settings
cp settings.json settings.json.backup

# 2. Clone the repo
git clone https://github.com/CountKrampus/rpgbot.git

# 3. Restore your settings
cp settings.json.backup settings.json
```

If you already cloned with git, you're ready to go!

### Update the Bot

```bash
# Simple: Update and restart
python update.py

# Check only (don't update)
python update.py --check

# Update without restarting
python update.py --no-restart

# Show help
python update.py --help
```

---

## What It Does

### `python update.py` (Full Update)

1. ✅ Checks if git is installed
2. ✅ Fetches latest changes from GitHub
3. ✅ Shows what's new
4. ✅ Asks for confirmation
5. ✅ Pulls the updates
6. ✅ Restarts the bot

**Time:** 30-60 seconds

### `python update.py --check` (Check Only)

1. ✅ Checks if updates are available
2. ✅ Shows new commits
3. ✅ Does NOT update anything
4. ✅ Does NOT restart bot

**Time:** 5-10 seconds

### `python update.py --no-restart` (Update Without Restart)

1. ✅ Same as full update
2. ✅ Does NOT restart bot
3. ✅ You restart manually later

---

## Features

### Smart Update Checking
- Fetches latest from GitHub
- Compares with your current version
- Shows commit history of new changes
- Clear message if already up to date

### Safe Updates
- ✅ Never touches your `settings.json` (preserved)
- ✅ Your settings are always safe
- ✅ Asks for confirmation before updating
- ✅ Handles errors gracefully

### Update Logging
- Keeps `.update_log` with last 20 updates
- Tracks timestamp, success/failure, commit
- Useful for troubleshooting

### Helpful Error Messages
- Clear error if git not found
- Merge conflict detection
- Timeout detection
- Network error handling

---

## Usage Examples

### Scenario 1: Regular Update

```bash
$ python update.py

============================================================
RPGBOT AUTO-UPDATE SYSTEM
============================================================

============================================================
CHECKING FOR UPDATES
============================================================

📡 Fetching latest changes from GitHub...
✅ Fetch successful

Current version: adcc553
Latest version:  39cbb73

🎉 Update available!

New commits:
  • Fix: Remove duplicate/wrong imports in settings_menu.py
  • Cleanup: Remove duplicate files and old backups

------------------------------------------------------------
Update now? (yes/no): yes

============================================================
UPDATING BOT
============================================================

📥 Pulling latest changes...
✅ Update successful!
  Fast-forward
   menus/settings_menu.py | 2 -
   1 file changed, 2 deletions(-)

============================================================
RESTARTING BOT
============================================================

Starting bot...
[Bot starts normally]
```

### Scenario 2: Already Up to Date

```bash
$ python update.py

============================================================
RPGBOT AUTO-UPDATE SYSTEM
============================================================

============================================================
CHECKING FOR UPDATES
============================================================

📡 Fetching latest changes from GitHub...
✅ Fetch successful

Current version: adcc553
Latest version:  adcc553

✅ You're already up to date!

✅ All done! Your bot is up to date.
```

### Scenario 3: Check Without Updating

```bash
$ python update.py --check

============================================================
CHECKING FOR UPDATES
============================================================

📡 Fetching latest changes from GitHub...
✅ Fetch successful

Current version: adcc553
Latest version:  adcc553

✅ You're already up to date!
```

### Scenario 4: Update Without Restarting

```bash
$ python update.py --no-restart

[same as above, but ends with:]

✅ Update complete! Bot will start on next run.
Run: python main.py
```

---

## Troubleshooting

### "Not a git repository!"

**Problem:** You downloaded bot as ZIP, not cloned with git

**Solution:**
```bash
# One-time setup:
cp settings.json settings.json.backup
git clone https://github.com/CountKrampus/rpgbot.git
cp settings.json.backup settings.json
```

### "Merge conflict detected!"

**Problem:** You modified bot files locally, which conflict with updates

**Solution:**
```bash
# Option 1: Keep your changes (don't update)
# Option 2: Discard your changes and get latest
git stash          # Save your changes
python update.py   # Try updating again

# Option 3: Compare and merge manually
git diff           # See what's different
# Fix conflicts, then:
git add .
git commit -m "Merged my changes"
python update.py
```

### "Update timed out"

**Problem:** Internet is slow or GitHub is down

**Solution:**
- Check your internet connection
- Try again in a few minutes
- GitHub status: https://www.githubstatus.com

### "command 'python' not found"

**Problem:** Python not in PATH or uses different name

**Solution:**
```bash
# Try one of these:
python3 update.py
python update.py
py update.py
```

---

## Advanced Usage

### Schedule Regular Updates

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Name: "Update RPGBot"
4. Trigger: Daily at 3:00 AM
5. Action: Run `python update.py --no-restart`
6. Location: Your bot folder

**Linux/Mac (Cron):**
```bash
# Open crontab editor
crontab -e

# Add this line (update daily at 3 AM):
0 3 * * * cd /path/to/rpgbot && python update.py --no-restart
```

### Check Update Log

```bash
# View update history (last 20 updates)
cat .update_log | python -m json.tool

# Or view in your editor
code .update_log
```

### Rollback to Previous Version

```bash
# See commit history
git log --oneline

# Go back to specific commit
git checkout <commit_sha>

# Or go back one version
git checkout HEAD~1
```

---

## What Gets Updated?

These files are automatically updated:

**Core Bot:**
- main.py, search.py, capture.py, training.py
- mining.py, trade.py, account.py, utils.py
- settings.py, break_timer.py, break_check.py

**Menus:**
- menus/main_menu.py, menus/settings_menu.py
- menus/training_menu.py, menus/search_menu.py
- menus/messages_menu.py, menus/shop_menu.py

**Data:**
- eclipse_maps.db, README.md

**Protected (Never Updated):**
- ✅ settings.json (your settings)
- ✅ Local files you create

---

## What Doesn't Get Updated?

Your personal data is never touched:

- ✅ `settings.json` — Your bot settings (preserved)
- ✅ Any files you create locally
- ✅ Your local modifications (if any)
- ✅ Downloaded files in outputs/

---

## FAQ

**Q: Will my settings be lost?**
A: No! `settings.json` is in `.gitignore` and never touched.

**Q: Can I update while the bot is running?**
A: No, update.py doesn't check for this. Stop the bot first, then update.

**Q: What if update fails?**
A: The script handles errors gracefully. Your bot won't be corrupted.

**Q: Can I rollback if update breaks something?**
A: Yes! Use `git checkout <commit>` or re-run from backup.

**Q: Do I need to restart after updating?**
A: Only if you want the new features. Use `--no-restart` if you want to do it later.

**Q: How often should I update?**
A: Check regularly with `python update.py --check`. Update when new features you want are available.

**Q: What if I modified some bot files?**
A: Git will detect conflicts. You can keep your changes or use the latest version.

**Q: Is it safe to update?**
A: Yes! git handles the update safely. If something fails, your bot isn't corrupted.

---

## How It Works (Technical)

### Under the Hood

1. **Check Git:** Verify `.git` folder exists
2. **Fetch:** `git fetch origin main` (download latest info)
3. **Compare:** Check if local version differs from GitHub
4. **Show:** Display new commits since your version
5. **Confirm:** Ask user for permission
6. **Pull:** `git pull origin main` (apply updates)
7. **Restart:** Run `python main.py`

### Safety Features

- ✅ Atomic operations (either fully updates or not at all)
- ✅ Preserves `.gitignore` files (settings.json, etc)
- ✅ Handles network timeouts
- ✅ Detects merge conflicts
- ✅ Logs all updates to `.update_log`
- ✅ Asks for confirmation before destructive operations

### Version Tracking

Current version shown as git commit SHA (first 7 chars):
- `adcc553` = commit hash (unique identifier)
- Changes every time code is updated
- Used to determine if updates are available

---

## Tips & Tricks

### Keep Bot Running 24/7 With Auto-Update

Use `launcher.py` wrapper (future feature):
```bash
# Will check for updates on startup
# Auto-updates in background if available
# Restarts bot automatically
python launcher.py
```

### Update During Maintenance Window

```bash
# Update when bot is stopped, during your maintenance window
python update.py --no-restart

# Bot updated but not restarted
# Restart manually when ready:
python main.py
```

### Monitor Updates

```bash
# Check for updates without changing anything
python update.py --check

# Then update when convenient
python update.py
```

---

## Getting Help

**Problems with update.py?**
1. Read the troubleshooting section above
2. Check `.update_log` for error details
3. Run with `--check` first to see what's available
4. Check GitHub Issues: https://github.com/CountKrampus/rpgbot/issues

**Git help:**
```bash
git --version      # Check git is installed
git status         # See current state
git log --oneline  # See commit history
```

---

## Summary

| Task | Command |
|------|---------|
| Update & restart | `python update.py` |
| Check only | `python update.py --check` |
| Update, don't restart | `python update.py --no-restart` |
| Show help | `python update.py --help` |
| View update log | `cat .update_log` |
| See git history | `git log --oneline` |

---

## Next Steps

1. ✅ You have `update.py` in your bot folder
2. ✅ Run `python update.py --check` to test
3. ✅ Run `python update.py` to update when ready
4. ✅ Bookmark this guide for reference

**Happy updating!** 🚀
