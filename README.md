# RPGBot — Eclipse RPG Automation

An advanced automation bot for Eclipse RPG with comprehensive settings, break mode, account management, and intelligent hunting strategies.

## Features

- **Hunt Modes**: Search, Training, Mining, Trading automation
- **Advanced Hunting**: Target specific Pokémon via database lookup (instant, no map scanning)
- **Break Mode**: Auto-managed breaks with configurable intervals
- **Settings System**: 17+ configurable settings with persistent storage
- **Account Dashboard**: View stats, achievements, inventory management
- **Capture Control**: Ball selection, retry logic, shiny detection
- **Network Reliability**: Slow network mode, connection retries, timeouts

## Quick Start

```bash
python main.py
```

Follow the on-screen menu to:
- Configure automation settings
- Choose hunt mode (Search, Training, Mining, Trade)
- View account dashboard
- Manage captures and breaks

## Settings

All settings are configurable via the in-app menu and persisted in `settings.json`:

- **Timing**: Encounter timeout, ball delay, detection retry delay
- **Capture**: Ball order, retry limit, shiny skip
- **Mining**: Poll interval, auto-catch, auto-stop
- **Network**: Browser timeout, connection retries, slow network mode
- **Session**: Time limit, auto-logout, shiny notifications
- **Break Mode**: Interval and duration configuration

## Project Structure

```
rpgbot/
├── main.py              # Entry point
├── menus/               # Menu system
│   ├── main_menu.py
│   ├── settings_menu.py
│   ├── training_menu.py
│   ├── search_menu.py
│   └── ...
├── search.py            # Hunt mode: Search
├── training.py          # Hunt mode: Training
├── mining.py            # Hunt mode: Mining
├── trade.py             # Hunt mode: Trading
├── capture.py           # Capture encounter logic
├── account.py           # Account dashboard
├── settings.py          # Settings management
├── utils.py             # Utilities and helpers
├── break_timer.py       # Break mode system
└── eclipse_maps.db      # Map data
```

## Requirements

- Python 3.8+
- Selenium WebDriver
- Browser automation capabilities

## License

Krampus Project (CountKrampus)