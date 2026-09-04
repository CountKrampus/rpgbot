"""Queued automation workflow for sequential time-limited tasks."""

import json
import time
from pathlib import Path

from cancellation import is_cancel_requested
from config import BASE_URL
from mining import miner_mode
from search import (
    MAPS,
    get_exclusive_maps,
    open_exclusive_area,
    open_map,
    run_searches,
)
from training import train_mode
from utils import wait_for_document_ready


QUEUE_PRESETS_FILE = str(Path(__file__).resolve().with_name("queue_presets.json"))


class QueuePlan(list):
    """A queue list with runtime-only repeat metadata."""

    repeats = 1


def load_queue_presets():
    """Load named queue presets, returning an empty mapping on bad/missing data."""
    try:
        with open(QUEUE_PRESETS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_queue_preset(name, queue):
    """Persist a named queue preset using the project's JSON settings convention."""
    name = str(name).strip()
    if not name or not isinstance(queue, (list, tuple)):
        return False
    presets = load_queue_presets()
    presets[name] = list(queue)
    try:
        with open(QUEUE_PRESETS_FILE, "w", encoding="utf-8") as file:
            json.dump(presets, file, indent=2)
        return True
    except OSError:
        return False


def load_queue_preset(name):
    """Return one preset, or ``None`` when it does not exist or is invalid."""
    preset = load_queue_presets().get(str(name).strip())
    return QueuePlan(preset) if isinstance(preset, list) else None


def delete_queue_preset(name):
    """Delete a named preset and report whether it was removed."""
    presets = load_queue_presets()
    name = str(name).strip()
    if name not in presets:
        return False
    del presets[name]
    try:
        with open(QUEUE_PRESETS_FILE, "w", encoding="utf-8") as file:
            json.dump(presets, file, indent=2)
        return True
    except OSError:
        return False


def _read_minutes(label):
    while True:
        value = input(f"\n{label} (minutes): ").strip()
        try:
            minutes = float(value)
        except ValueError:
            print("✗ Enter a positive number of minutes.")
            continue
        if minutes > 0:
            return minutes
        print("✗ Enter a positive number of minutes.")


def _choose_map(driver):
    print("\nSEARCH MAP")
    exclusive_maps = get_exclusive_maps(driver)
    choices = [
        {"name": name, "is_exclusive": False, "area": None}
        for name in MAPS
    ]
    choices.extend(
        {
            "name": area["name"],
            "is_exclusive": True,
            "area": area,
        }
        for area in exclusive_maps
    )

    for index, choice in enumerate(choices, 1):
        name = choice["name"]
        suffix = " (exclusive)" if choice["is_exclusive"] else ""
        print(f"{index:2}. {name}{suffix}")

    while True:
        value = input(
            f"\nChoose map (1-{len(choices)}): "
        ).strip()
        try:
            index = int(value)
        except ValueError:
            index = 0
        if 1 <= index <= len(choices):
            return choices[index - 1]
        print(f"✗ Please enter a number from 1 to {len(choices)}.")


def _format_step(step):
    if step["type"] == "train":
        label = "Training"
    elif step["type"] == "mine":
        label = "Mining"
    else:
        label = f"Searching {step['map']['name']}"
    return f"{label} for {step['minutes']:g} minute(s)"


def _choose_step(queue, prompt):
    if not queue:
        print("✗ Add at least one step first.")
        return None
    while True:
        value = input(f"\n{prompt} (1-{len(queue)}): ").strip()
        try:
            index = int(value)
        except ValueError:
            index = 0
        if 1 <= index <= len(queue):
            return index - 1
        print(f"✗ Please enter a number from 1 to {len(queue)}.")


def _edit_queue(queue, driver):
    index = _choose_step(queue, "Choose step to edit")
    if index is None:
        return
    step = queue[index]
    step["minutes"] = _read_minutes("Run for")
    if step["type"] == "search":
        step["map"] = _choose_map(driver)
    elif step["type"] == "mine":
        step["catch"] = input(
            "Catch Pokémon while mining? [Y/n]: "
        ).strip().lower() not in ("n", "no")


def _move_step(queue, direction):
    index = _choose_step(queue, f"Choose step to move {direction}")
    if index is None:
        return
    target = index - 1 if direction == "up" else index + 1
    if not 0 <= target < len(queue):
        print(f"✗ Step is already at the {direction} boundary.")
        return
    queue[index], queue[target] = queue[target], queue[index]


def _show_queue(queue):
    print("\nQUEUE PLAN")
    if not queue:
        print("  (empty)")
        return

    for index, step in enumerate(queue, 1):
        print(f"  {index}. {_format_step(step)}")


def _read_repeats():
    while True:
        value = input("\nRepeat queue how many times? [1]: ").strip()
        if not value:
            return 1
        try:
            repeats = int(value)
        except ValueError:
            repeats = 0
        if repeats > 0:
            return repeats
        print("✗ Enter a positive whole number.")


def _choose_preset():
    presets = load_queue_presets()
    if not presets:
        print("✗ No saved queue presets.")
        return None
    names = list(presets)
    for index, name in enumerate(names, 1):
        print(f"  {index}. {name}")
    while True:
        value = input(f"\nChoose preset (1-{len(names)}): ").strip()
        try:
            index = int(value)
        except ValueError:
            index = 0
        if 1 <= index <= len(names):
            return load_queue_preset(names[index - 1])
        print(f"✗ Please enter a number from 1 to {len(names)}.")


def _build_queue(driver):
    queue = QueuePlan()

    while True:
        _show_queue(queue)
        print("\nQUEUE BUILDER")
        print("  1. Add Training")
        print("  2. Add Search")
        print("  3. Add Mining")
        print("  4. Edit step")
        print("  5. Move step up")
        print("  6. Move step down")
        print("  7. Remove step")
        print("  8. Start queue")
        print("  9. Save preset")
        print(" 10. Load preset")
        print(" 11. Delete preset")
        print(" 12. Cancel")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            queue.append({
                "type": "train",
                "minutes": _read_minutes("Train for"),
            })
        elif choice == "2":
            queue.append({
                "type": "search",
                "minutes": _read_minutes("Search for"),
                "map": _choose_map(driver),
            })
        elif choice == "3":
            queue.append({
                "type": "mine",
                "minutes": _read_minutes("Mine for"),
                "catch": input(
                    "Catch Pokémon while mining? [Y/n]: "
                ).strip().lower() not in ("n", "no"),
            })
        elif choice == "4":
            _edit_queue(queue, driver)
        elif choice == "5":
            _move_step(queue, "up")
        elif choice == "6":
            _move_step(queue, "down")
        elif choice == "7":
            index = _choose_step(queue, "Choose step to remove")
            if index is not None:
                removed = queue.pop(index)
                print(f"Removed {_format_step(removed)}.")
        elif choice == "8":
            if queue:
                queue.repeats = _read_repeats()
                return queue
            print("✗ Add at least one step first.")
        elif choice == "9":
            name = input("\nPreset name: ").strip()
            if save_queue_preset(name, queue):
                print(f"Saved preset '{name}'.")
            else:
                print("✗ Could not save preset.")
        elif choice == "10":
            loaded = _choose_preset()
            if loaded is not None:
                queue[:] = loaded
                print("Preset loaded.")
        elif choice == "11":
            name = input("\nPreset name to delete: ").strip()
            if delete_queue_preset(name):
                print(f"Deleted preset '{name}'.")
            else:
                print("✗ Preset not found.")
        elif choice == "12":
            return None
        else:
            print("✗ Invalid choice.")


def _format_duration(seconds):
    seconds = max(0, int(seconds))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def _failure_action(step):
    while True:
        choice = input(
            f"Failure in {_format_step(step)}. "
            "[R]etry, [S]kip, or s[T]op? "
        ).strip().lower()
        if choice in ("r", "retry"):
            return "retry"
        if choice in ("s", "skip"):
            return "skip"
        if choice in ("t", "stop", ""):
            return "stop"
        print("✗ Choose retry, skip, or stop.")


def _run_step(driver, step, duration):
    if step["type"] == "train":
        train_mode(driver, duration_seconds=duration)
        return
    if step["type"] == "mine":
        miner_mode(
            driver,
            queued_duration_seconds=duration,
            queued_catch_pokemon=step["catch"],
        )
        return
    map_info = step["map"]
    driver.get(f"{BASE_URL}/legendary_areas")
    wait_for_document_ready(driver)
    if map_info["is_exclusive"]:
        opened = open_exclusive_area(driver, map_info["area"])
    else:
        opened = open_map(driver, map_info["name"])
    if not opened:
        raise RuntimeError(f"Could not open {map_info['name']}")
    run_searches(
        driver,
        map_info["name"],
        searches=10**9,
        is_exclusive=map_info["is_exclusive"],
        area=map_info["area"],
        duration_seconds=duration,
    )


def _run_queue(driver, queue, repeats=1):
    total_steps = len(queue) * repeats
    total_seconds = sum(step["minutes"] * 60 for step in queue) * repeats
    started = time.monotonic()
    completed = 0
    for cycle in range(repeats):
        for step in queue:
            if is_cancel_requested():
                return
            while True:
                elapsed = time.monotonic() - started
                remaining = max(0, total_seconds - elapsed)
                print(
                    f"\nQueue progress: {completed + 1}/{total_steps} "
                    f"(elapsed {_format_duration(elapsed)}, "
                    f"remaining {_format_duration(remaining)})"
                )
                try:
                    _run_step(driver, step, step["minutes"] * 60)
                    break
                except Exception as error:
                    print(f"✗ {error}")
                    action = _failure_action(step)
                    if action == "retry":
                        continue
                    if action == "stop":
                        return
                    break
            completed += 1


def queue_mode(driver):
    """Build and run a manually ordered sequence of timed tasks."""
    queue = _build_queue(driver)
    if not queue:
        print("Queue cancelled.")
        return

    _show_queue(queue)
    if input("Start queue? [y/N]: ").strip().lower() not in ("y", "yes"):
        print("Queue cancelled.")
        return

    _run_queue(driver, queue, max(1, int(getattr(queue, "repeats", 1))))
