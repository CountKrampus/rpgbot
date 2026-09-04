"""
Session Manager - Browser Session Persistence & Recovery

Manages browser session state, crash detection, and recovery.
Allows resuming automation after browser crashes.
"""

import json
import time
from pathlib import Path
from datetime import datetime


class SessionManager:
    """Manage browser session state and recovery."""

    SESSION_TIMEOUT = 3600  # 1 hour default timeout

    @staticmethod
    def get_session_file(instance_name):
        """Get session state file path for an account."""
        from platform_detection import PlatformDetector
        
        data_dir = PlatformDetector.get_data_dir()
        session_file = data_dir / f"{instance_name}_session.json"
        return session_file

    @classmethod
    def start_session(cls, instance_name, browser_type="brave"):
        """Start a new browser session and record it."""
        
        session_data = {
            "instance_name": instance_name,
            "browser_type": browser_type,
            "start_time": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "status": "active",
            "crash_count": 0,
            "automation_data": {},
        }
        
        session_file = cls.get_session_file(instance_name)
        
        try:
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            return session_data
        except Exception as e:
            print(f"Warning: Could not save session state: {e}")
            return session_data

    @classmethod
    def load_session(cls, instance_name):
        """Load existing session state."""
        session_file = cls.get_session_file(instance_name)
        
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None

    @classmethod
    def update_session(cls, instance_name, data_update):
        """Update session state with new data."""
        session_file = cls.get_session_file(instance_name)
        
        try:
            # Load existing session
            if session_file.exists():
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
            else:
                session_data = {"instance_name": instance_name}
            
            # Update with new data
            session_data.update(data_update)
            session_data["last_activity"] = datetime.now().isoformat()
            
            # Save
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            return session_data
        except Exception as e:
            print(f"Warning: Could not update session state: {e}")
            return None

    @classmethod
    def record_crash(cls, instance_name):
        """Record a browser crash."""
        session = cls.load_session(instance_name)
        
        if not session:
            return
        
        session["crash_count"] = session.get("crash_count", 0) + 1
        session["last_crash"] = datetime.now().isoformat()
        session["status"] = "crashed"
        
        cls.update_session(instance_name, session)

    @classmethod
    def can_recover_session(cls, instance_name, max_crashes=3, timeout_seconds=3600):
        """Check if session can be recovered after crash."""
        session = cls.load_session(instance_name)
        
        if not session:
            return False
        
        # Check crash count
        if session.get("crash_count", 0) >= max_crashes:
            return False
        
        # Check timeout
        try:
            last_activity = datetime.fromisoformat(
                session.get("last_activity", "")
            )
            elapsed = (datetime.now() - last_activity).total_seconds()
            
            if elapsed > timeout_seconds:
                return False
        except (ValueError, TypeError):
            return False
        
        return True

    @classmethod
    def resume_session(cls, instance_name):
        """Resume a crashed session."""
        session = cls.load_session(instance_name)
        
        if not session:
            return None
        
        # Reset crash flag but keep crash count
        session["status"] = "resuming"
        session["resume_time"] = datetime.now().isoformat()
        
        cls.update_session(instance_name, session)
        
        return session

    @classmethod
    def end_session(cls, instance_name):
        """End and clean up session."""
        session_file = cls.get_session_file(instance_name)
        
        try:
            if session_file.exists():
                session_file.unlink()
            return True
        except Exception:
            return False

    @classmethod
    def get_session_stats(cls, instance_name):
        """Get session statistics for debugging."""
        session = cls.load_session(instance_name)
        
        if not session:
            return None
        
        try:
            start = datetime.fromisoformat(session.get("start_time", ""))
            last_activity = datetime.fromisoformat(
                session.get("last_activity", "")
            )
            
            uptime = (last_activity - start).total_seconds()
            
            return {
                "instance": instance_name,
                "status": session.get("status", "unknown"),
                "uptime_seconds": uptime,
                "crash_count": session.get("crash_count", 0),
                "browser": session.get("browser_type", "unknown"),
                "last_activity": session.get("last_activity", "unknown"),
            }
        except Exception:
            return None


class ProfileRecovery:
    """Recover corrupted browser profiles."""

    @staticmethod
    def backup_profile(profile_path):
        """Create backup of browser profile before session."""
        from pathlib import Path
        import shutil
        
        profile_path = Path(profile_path)
        
        if not profile_path.exists():
            return None
        
        backup_dir = profile_path.parent / f"{profile_path.name}_backup_{int(time.time())}"
        
        try:
            shutil.copytree(profile_path, backup_dir)
            return backup_dir
        except Exception as e:
            print(f"Warning: Could not backup profile: {e}")
            return None

    @staticmethod
    def restore_profile(profile_path, backup_path):
        """Restore browser profile from backup."""
        from pathlib import Path
        import shutil
        
        profile_path = Path(profile_path)
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            return False
        
        try:
            # Remove corrupted profile
            if profile_path.exists():
                shutil.rmtree(profile_path)
            
            # Restore from backup
            shutil.copytree(backup_path, profile_path)
            return True
        except Exception as e:
            print(f"Error: Could not restore profile: {e}")
            return False

    @staticmethod
    def detect_corruption(profile_path):
        """Detect if profile is corrupted."""
        from pathlib import Path
        
        profile_path = Path(profile_path)
        
        if not profile_path.exists():
            return False
        
        # Check for lock files indicating crash
        lock_files = [
            profile_path / "SingletonLock",
            profile_path / ".chrome_lock",
            profile_path / "Preferences.lock",
        ]
        
        for lock_file in lock_files:
            if lock_file.exists():
                return True
        
        return False

    @staticmethod
    def cleanup_locks(profile_path):
        """Remove lock files from crashed session."""
        from pathlib import Path
        
        profile_path = Path(profile_path)
        
        lock_files = [
            profile_path / "SingletonLock",
            profile_path / ".chrome_lock",
            profile_path / "Preferences.lock",
        ]
        
        for lock_file in lock_files:
            try:
                if lock_file.exists():
                    lock_file.unlink()
            except Exception:
                pass


class CrashDetector:
    """Detect and handle browser crashes."""

    @staticmethod
    def is_driver_alive(driver):
        """Check if WebDriver is still responsive."""
        try:
            driver.current_url
            return True
        except Exception:
            return False

    @staticmethod
    def monitor_driver(driver, instance_name, check_interval=30):
        """Monitor driver health and detect crashes."""
        import threading
        
        def check_health():
            while True:
                try:
                    if not CrashDetector.is_driver_alive(driver):
                        SessionManager.record_crash(instance_name)
                        break
                    time.sleep(check_interval)
                except Exception:
                    break
        
        # Start monitor thread
        monitor = threading.Thread(target=check_health, daemon=True)
        monitor.start()
        return monitor

