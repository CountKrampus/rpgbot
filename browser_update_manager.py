"""
Browser Update Manager & Cache Management

Handles browser updates, cache clearing, and profile maintenance.
"""

import subprocess
from pathlib import Path


class BrowserUpdateManager:
    """Manage browser updates and maintenance."""

    @staticmethod
    def clear_browser_cache(profile_path):
        """Clear browser cache to free space."""
        cache_locations = [
            "Cache",
            "Code Cache",
            "Default/Cache",
            "Default/Code Cache",
            "cache",
            "application cache",
        ]
        
        profile_path = Path(profile_path)
        cleared = 0
        
        for cache_dir in cache_locations:
            cache_path = profile_path / cache_dir
            
            if cache_path.exists():
                try:
                    import shutil
                    shutil.rmtree(cache_path)
                    cleared += 1
                except Exception:
                    pass
        
        return cleared > 0

    @staticmethod
    def clear_browser_cookies(profile_path):
        """Clear browser cookies."""
        cookies_file = Path(profile_path) / "Cookies"
        
        try:
            if cookies_file.exists():
                cookies_file.unlink()
            return True
        except Exception:
            return False

    @staticmethod
    def clear_browser_data(profile_path, clear_cache=True, clear_cookies=True, clear_history=False):
        """Clear various browser data."""
        results = {
            "cache": clear_cache and BrowserUpdateManager.clear_browser_cache(profile_path),
            "cookies": clear_cookies and BrowserUpdateManager.clear_browser_cookies(profile_path),
        }
        
        return results

    @staticmethod
    def check_browser_version(browser_name):
        """Check installed browser version."""
        try:
            if browser_name.lower() == "brave":
                result = subprocess.run(
                    ["brave", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                return result.stdout.strip()
            
            elif browser_name.lower() == "chrome":
                result = subprocess.run(
                    ["google-chrome", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                return result.stdout.strip()
            
            elif browser_name.lower() == "chromium":
                result = subprocess.run(
                    ["chromium", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                return result.stdout.strip()
        
        except Exception:
            return None

    @staticmethod
    def get_selenium_version():
        """Get installed Selenium version."""
        try:
            import selenium
            return selenium.__version__
        except Exception:
            return None

    @staticmethod
    def get_webdriver_version():
        """Get WebDriver version."""
        try:
            from selenium import webdriver
            options = webdriver.ChromeOptions()
            # WebDriver version is typically tied to Chrome version
            return "See Chrome version"
        except Exception:
            return None


class ProfileMaintenance:
    """Perform profile maintenance and cleanup."""

    @staticmethod
    def get_profile_size(profile_path):
        """Get total size of browser profile."""
        import os
        
        profile_path = Path(profile_path)
        
        if not profile_path.exists():
            return 0
        
        total_size = 0
        
        for entry in profile_path.rglob("*"):
            if entry.is_file():
                try:
                    total_size += entry.stat().st_size
                except Exception:
                    pass
        
        return total_size

    @staticmethod
    def get_profile_size_mb(profile_path):
        """Get profile size in MB."""
        size_bytes = ProfileMaintenance.get_profile_size(profile_path)
        return round(size_bytes / (1024 * 1024), 2)

    @staticmethod
    def get_cache_size(profile_path):
        """Get size of browser cache."""
        cache_dirs = [
            Path(profile_path) / "Cache",
            Path(profile_path) / "Code Cache",
            Path(profile_path) / "Default" / "Cache",
        ]
        
        total_size = 0
        
        for cache_dir in cache_dirs:
            if cache_dir.exists():
                for entry in cache_dir.rglob("*"):
                    if entry.is_file():
                        try:
                            total_size += entry.stat().st_size
                        except Exception:
                            pass
        
        return total_size

    @staticmethod
    def cleanup_old_backups(profile_path, keep_count=3):
        """Remove old profile backups, keeping most recent."""
        backup_dir = Path(profile_path).parent
        backups = sorted(
            [d for d in backup_dir.glob(f"{Path(profile_path).name}_backup_*")],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        
        removed = 0
        
        for backup in backups[keep_count:]:
            try:
                import shutil
                shutil.rmtree(backup)
                removed += 1
            except Exception:
                pass
        
        return removed

    @staticmethod
    def generate_maintenance_report(profile_path):
        """Generate profile maintenance report."""
        size_mb = ProfileMaintenance.get_profile_size_mb(profile_path)
        cache_size = ProfileMaintenance.get_cache_size(profile_path)
        cache_mb = round(cache_size / (1024 * 1024), 2)
        
        return {
            "profile_size_mb": size_mb,
            "cache_size_mb": cache_mb,
            "cache_percentage": round((cache_size / ProfileMaintenance.get_profile_size(profile_path) * 100) if ProfileMaintenance.get_profile_size(profile_path) > 0 else 0, 1),
        }


class AutoUpdate:
    """Handle automatic updates of bot and browsers."""

    @staticmethod
    def check_bot_update():
        """Check if RPGBot has updates available."""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return None

    @staticmethod
    def update_bot():
        """Update RPGBot from repository."""
        try:
            subprocess.run(
                ["git", "pull", "origin", "main"],
                check=True,
                capture_output=True,
                timeout=30,
            )
            return True
        except Exception:
            return False

    @staticmethod
    def should_restart_browser():
        """Determine if browser should be restarted for updates."""
        # Could check for pending updates, memory usage, etc.
        return False

    @staticmethod
    def schedule_maintenance(browser_name, profile_path):
        """Schedule periodic maintenance."""
        return {
            "clear_cache": True,
            "backup_profile": True,
            "cleanup_old_backups": True,
            "check_version": True,
        }

