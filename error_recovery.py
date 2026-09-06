"""
Advanced error recovery and retry logic
- Exponential backoff
- Circuit breaker pattern
- Error classification
"""

import time
import random

class ErrorRecovery:
    def __init__(self):
        self.max_retries = 5
        self.base_delay = 1  # seconds
        self.max_delay = 60  # seconds
        self.circuit_breaker_threshold = 10
        self.consecutive_errors = 0
        self.error_history = []
    
    def retry_with_backoff(self, func, *args, **kwargs):
        """Retry function with exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                self.consecutive_errors = 0
                return result
            except Exception as e:
                self.consecutive_errors += 1
                self.error_history.append({'error': str(e), 'attempt': attempt})
                
                if self.consecutive_errors > self.circuit_breaker_threshold:
                    print(f"  [CIRCUIT BREAKER] Too many errors, shutting down")
                    raise
                
                if attempt < self.max_retries - 1:
                    delay = min(self.base_delay * (2 ** attempt) + random.uniform(0, 1), self.max_delay)
                    print(f"  [RETRY] Attempt {attempt + 1}/{self.max_retries}, waiting {delay:.1f}s...")
                    time.sleep(delay)
                else:
                    print(f"  [ERROR] Failed after {self.max_retries} attempts: {e}")
                    raise
    
    def classify_error(self, error):
        """Classify error type for better handling"""
        error_str = str(error).lower()
        
        if "timeout" in error_str or "connection" in error_str:
            return "network"
        elif "404" in error_str:
            return "not_found"
        elif "403" in error_str or "401" in error_str:
            return "auth"
        elif "500" in error_str or "502" in error_str:
            return "server"
        else:
            return "unknown"
    
    def reset_state(self):
        """Reset error tracking after successful operation"""
        self.consecutive_errors = 0

class RateLimiter:
    """Prevent hitting rate limits"""
    def __init__(self, requests_per_second=5):
        self.requests_per_second = requests_per_second
        self.min_delay = 1.0 / requests_per_second
        self.last_request = 0
    
    def wait_if_needed(self):
        """Wait if requests are too fast"""
        now = time.time()
        time_since_last = now - self.last_request
        
        if time_since_last < self.min_delay:
            delay = self.min_delay - time_since_last
            time.sleep(delay)
        
        self.last_request = time.time()
