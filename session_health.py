"""
Session health monitoring
Keeps the session alive and detects when it's about to expire
"""

import time
from helpers import page_contains

class SessionHealth:
    def __init__(self, driver):
        self.driver = driver
        self.last_check = time.time()
        self.check_interval = 300  # Check every 5 minutes
    
    def is_session_alive(self):
        """Check if session is still valid"""
        try:
            # Check if we're still logged in
            page_source = self.driver.page_source
            
            # Signs of dead session
            if "Log In" in page_source and "eclipse" not in page_source.lower():
                print("  [SESSION] Detected logout - session expired!")
                return False
            
            if "Session expired" in page_source:
                print("  [SESSION] Server says session expired!")
                return False
            
            return True
        except Exception as e:
            print(f"  [SESSION] Error checking: {e}")
            return False
    
    def refresh_session(self):
        """Keep session alive by visiting a page"""
        try:
            if time.time() - self.last_check > self.check_interval:
                print("  [SESSION] Refreshing...")
                # Visit home page to keep session alive
                self.driver.get("https://eclipserpg.com")
                self.last_check = time.time()
                print("  [SESSION] Refreshed")
                return True
        except Exception as e:
            print(f"  [SESSION] Refresh failed: {e}")
            return False
    
    def maintain_health(self):
        """Call this periodically to keep session healthy"""
        self.refresh_session()
        if not self.is_session_alive():
            return False
        return True
