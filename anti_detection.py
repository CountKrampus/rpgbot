"""
Anti-detection and human-like behavior
- Random delays between actions
- Realistic mouse movements
- Varied click patterns
- Session rotation
"""

import random
import time

class HumanLikeBehavior:
    def __init__(self):
        self.base_delay = 0.5
        self.max_delay = 3.0
        self.variance = 0.3
    
    def random_delay(self):
        """Add human-like random delay"""
        # Most delays are quick, some are longer
        if random.random() < 0.1:  # 10% of time, longer delay
            delay = random.uniform(2.0, self.max_delay)
        else:
            delay = random.uniform(self.base_delay, self.base_delay * 2)
        
        time.sleep(delay)
    
    def get_random_interval(self, min_seconds, max_seconds):
        """Get random interval with human variance"""
        base = random.uniform(min_seconds, max_seconds)
        variance = base * self.variance * random.uniform(-1, 1)
        return max(0.1, base + variance)
    
    def simulate_thinking(self):
        """Simulate user thinking/hesitation"""
        if random.random() < 0.2:  # 20% chance of thinking
            time.sleep(random.uniform(0.5, 2.0))
    
    def get_random_user_agent(self):
        """Return random user agent"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        ]
        return random.choice(user_agents)

class SessionRotation:
    """Rotate sessions to avoid detection"""
    
    def __init__(self, max_age_minutes=60):
        self.max_age = max_age_minutes * 60
        self.session_created = time.time()
    
    def should_refresh(self):
        """Check if session should be refreshed"""
        age = time.time() - self.session_created
        return age > self.max_age
    
    def refresh_session(self, driver):
        """Refresh session to get new cookies"""
        try:
            # Visit home page to get fresh session
            driver.get("https://eclipserpg.com")
            time.sleep(random.uniform(1, 2))
            
            # Clear cache
            driver.delete_all_cookies()
            
            self.session_created = time.time()
            return True
        except:
            return False

class BehaviorPattern:
    """Track and vary behavior patterns"""
    
    def __init__(self):
        self.actions = []
        self.patterns = {
            'attack_speed': self.get_random_attack_speed(),
            'click_style': random.choice(['precise', 'sloppy', 'normal']),
            'pause_style': random.choice(['nervous', 'confident', 'thoughtful'])
        }
    
    def get_random_attack_speed(self):
        """Vary attack speed like different players"""
        speeds = ['fast', 'normal', 'slow', 'very_slow']
        weights = [0.2, 0.5, 0.2, 0.1]
        return random.choices(speeds, weights=weights)[0]
    
    def log_action(self, action_type):
        """Log user action"""
        self.actions.append({
            'type': action_type,
            'timestamp': time.time()
        })
    
    def get_action_frequency(self, action_type):
        """Get frequency of specific action"""
        actions_of_type = [a for a in self.actions if a['type'] == action_type]
        return len(actions_of_type) / max(1, len(self.actions))

class DetectionAvoidance:
    """Avoid common detection patterns"""
    
    @staticmethod
    def get_realistic_headers():
        """Get realistic HTTP headers"""
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    @staticmethod
    def add_random_delay_to_requests(session):
        """Add random delays to requests to avoid pattern detection"""
        original_request = session.request
        
        def delayed_request(*args, **kwargs):
            time.sleep(random.uniform(0.1, 0.5))
            return original_request(*args, **kwargs)
        
        session.request = delayed_request
        return session
    
    @staticmethod
    def rotate_ip_if_available():
        """Rotate IP if proxy is available"""
        # This would use a proxy service if configured
        pass
