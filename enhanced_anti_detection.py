"""
Enhanced anti-detection module with realistic human-like behavior patterns.
Implements mouse movement, timing variance, behavioral patterns, and fingerprint rotation.
"""

import time
import random
import math
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class BezierCurveMovement:
    """Generate realistic mouse movement using Bezier curves."""
    
    @staticmethod
    def calculate_bezier_point(p0, p1, p2, p3, t):
        """Calculate point on cubic Bezier curve."""
        mt = 1 - t
        mt3 = mt ** 3
        mt2 = mt ** 2
        t3 = t ** 3
        t2 = t ** 2
        
        x = mt3 * p0[0] + 3 * mt2 * t * p1[0] + 3 * mt * t2 * p2[0] + t3 * p3[0]
        y = mt3 * p0[1] + 3 * mt2 * t * p1[1] + 3 * mt * t2 * p2[1] + t3 * p3[1]
        
        return (int(x), int(y))
    
    @staticmethod
    def move_to_element(driver, element, start_pos=None):
        """Move mouse to element using realistic Bezier curve."""
        try:
            location = element.location
            size = element.size
            
            # Target: center of element with small random offset
            target_x = location['x'] + size['width'] / 2 + random.randint(-10, 10)
            target_y = location['y'] + size['height'] / 2 + random.randint(-10, 10)
            
            # Starting position (current mouse position or random)
            if start_pos is None:
                start_x = random.randint(0, driver.get_window_size()['width'])
                start_y = random.randint(0, driver.get_window_size()['height'])
            else:
                start_x, start_y = start_pos
            
            # Control points for Bezier curve
            cp1_x = start_x + random.randint(-100, 100)
            cp1_y = start_y + random.randint(-100, 100)
            cp2_x = target_x + random.randint(-100, 100)
            cp2_y = target_y + random.randint(-100, 100)
            
            # Generate curve points and move mouse
            actions = ActionChains(driver)
            steps = random.randint(20, 40)  # Variable number of steps
            
            for i in range(steps):
                t = i / steps
                point = BezierCurveMovement.calculate_bezier_point(
                    (start_x, start_y),
                    (cp1_x, cp1_y),
                    (cp2_x, cp2_y),
                    (target_x, target_y),
                    t
                )
                actions.move_to_element_with_offset(element, 0, 0)
                time.sleep(random.uniform(0.01, 0.03))  # Micro-delays
            
            return (target_x, target_y)
        except Exception as e:
            print(f"Bezier movement error: {e}")
            return None


class BehavioralVariance:
    """Implement human-like behavioral variance patterns."""
    
    def __init__(self):
        self.session_start = time.time()
        self.action_count = 0
        self.last_break_time = time.time()
        self.last_activity_time = time.time()
        self.fatigue_level = 0.0  # 0.0 to 1.0
        
    def get_action_delay(self):
        """Get realistic action delay with variance."""
        # Base delay with variance
        base_delay = random.gauss(0.35, 0.15)  # Mean 0.35s, stddev 0.15s
        base_delay = max(0.1, min(0.8, base_delay))  # Clamp to 0.1-0.8s
        
        # Add fatigue effect (gets slower over time)
        fatigue_factor = 1.0 + (self.fatigue_level * 0.5)  # Up to 50% slower
        
        # Random spike (occasional lag simulation)
        if random.random() < 0.05:  # 5% chance
            base_delay += random.uniform(1.0, 3.0)
        
        return base_delay * fatigue_factor
    
    def get_think_time(self):
        """Realistic thinking time before major actions."""
        # Humans think before important decisions
        think_time = random.gauss(2.5, 1.2)  # Mean 2.5s, high variance
        think_time = max(0.5, min(8.0, think_time))  # Clamp to 0.5-8s
        
        return think_time
    
    def get_break_time(self):
        """Determine if user needs a break and how long."""
        actions_since_break = self.action_count - int(self.last_break_time)
        
        # Break every 50-150 actions
        if actions_since_break > random.randint(50, 150):
            # Break duration: 10-60 seconds
            break_duration = random.gauss(25, 15)  # Mean 25s
            break_duration = max(5, min(120, break_duration))  # Clamp
            
            self.last_break_time = self.action_count
            return break_duration
        
        return 0
    
    def update_fatigue(self):
        """Update fatigue based on session time."""
        elapsed_hours = (time.time() - self.session_start) / 3600
        
        # Fatigue increases with session length
        # Fatigue = 1.0 after 8 hours
        self.fatigue_level = min(1.0, elapsed_hours / 8.0)
    
    def record_action(self):
        """Record that an action was taken."""
        self.action_count += 1
        self.last_activity_time = time.time()
        self.update_fatigue()


class HeaderFingerprint:
    """Rotate HTTP headers to avoid detection."""
    
    ACCEPT_LANGUAGES = [
        'en-US,en;q=0.9',
        'en-US,en;q=0.8,es;q=0.6',
        'en-US,en;q=0.7,fr;q=0.5',
        'en;q=0.9,en-US;q=0.8',
    ]
    
    ACCEPT_ENCODINGS = [
        'gzip, deflate, br',
        'gzip, deflate',
        'deflate, gzip',
    ]
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    ]
    
    @staticmethod
    def get_random_headers():
        """Get randomized HTTP headers."""
        return {
            'User-Agent': random.choice(HeaderFingerprint.USER_AGENTS),
            'Accept-Language': random.choice(HeaderFingerprint.ACCEPT_LANGUAGES),
            'Accept-Encoding': random.choice(HeaderFingerprint.ACCEPT_ENCODINGS),
            'Sec-Fetch-Dest': random.choice(['document', 'empty']),
            'Sec-Fetch-Mode': random.choice(['navigate', 'cors']),
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': random.choice(['max-age=0', 'no-cache']),
        }


class BotDetectionAvoidance:
    """Detect and avoid common bot detection signatures."""
    
    def __init__(self):
        self.action_timing_history = []
        self.xp_gain_history = []
        self.capture_rate_history = []
        self.last_check_time = time.time()
        
    def log_action_timing(self, duration):
        """Log action timing for analysis."""
        self.action_timing_history.append(duration)
        if len(self.action_timing_history) > 100:
            self.action_timing_history.pop(0)
    
    def log_xp_gain(self, xp_amount):
        """Log XP gains to detect impossible rates."""
        self.xp_gain_history.append((time.time(), xp_amount))
        # Remove entries older than 1 hour
        current_time = time.time()
        self.xp_gain_history = [(t, xp) for t, xp in self.xp_gain_history 
                                if current_time - t < 3600]
    
    def log_capture(self, success):
        """Log capture attempts."""
        self.capture_rate_history.append(success)
        if len(self.capture_rate_history) > 100:
            self.capture_rate_history.pop(0)
    
    def get_timing_variance(self):
        """Calculate variance in action timing."""
        if len(self.action_timing_history) < 10:
            return None
        
        mean = sum(self.action_timing_history) / len(self.action_timing_history)
        variance = sum((x - mean) ** 2 for x in self.action_timing_history) / len(self.action_timing_history)
        
        return {
            'mean': mean,
            'variance': variance,
            'stddev': math.sqrt(variance),
            'min': min(self.action_timing_history),
            'max': max(self.action_timing_history),
        }
    
    def get_xp_rate(self):
        """Calculate XP gain rate (per hour)."""
        if not self.xp_gain_history:
            return 0
        
        total_xp = sum(xp for _, xp in self.xp_gain_history)
        time_span = time.time() - self.xp_gain_history[0][0]
        
        if time_span < 60:  # Less than 1 minute
            return 0
        
        hours = time_span / 3600
        return total_xp / hours if hours > 0 else 0
    
    def get_capture_rate(self):
        """Calculate capture success rate."""
        if not self.capture_rate_history:
            return 0
        
        successes = sum(1 for x in self.capture_rate_history if x)
        return successes / len(self.capture_rate_history)
    
    def check_for_detection_signatures(self):
        """Check for common bot detection signatures."""
        signatures = {
            'timing': self._check_timing_signature(),
            'xp_rate': self._check_xp_signature(),
            'capture_rate': self._check_capture_signature(),
        }
        
        return signatures
    
    def _check_timing_signature(self):
        """Check if timing looks too uniform."""
        variance_data = self.get_timing_variance()
        if variance_data is None:
            return None
        
        # Humans have high variance (stddev 0.2+)
        # Bots have low variance (stddev < 0.1)
        is_suspicious = variance_data['stddev'] < 0.08
        
        return {
            'suspicious': is_suspicious,
            'stddev': variance_data['stddev'],
            'recommendation': 'Add more timing variance' if is_suspicious else 'Timing looks human'
        }
    
    def _check_xp_signature(self):
        """Check if XP gains look too perfect."""
        xp_rate = self.get_xp_rate()
        
        # Humans have variable XP (some battles better than others)
        # Perfect consistency is suspicious
        
        if not self.xp_gain_history or len(self.xp_gain_history) < 5:
            return None
        
        xp_gains = [xp for _, xp in self.xp_gain_history]
        mean_xp = sum(xp_gains) / len(xp_gains)
        variance = sum((x - mean_xp) ** 2 for x in xp_gains) / len(xp_gains)
        
        # Humans have coefficient of variation > 0.1
        # Bots have CV < 0.05 (too perfect)
        cv = math.sqrt(variance) / mean_xp if mean_xp > 0 else 0
        is_suspicious = cv < 0.05
        
        return {
            'suspicious': is_suspicious,
            'coefficient_of_variation': cv,
            'rate_per_hour': xp_rate,
            'recommendation': 'XP gains too uniform' if is_suspicious else 'XP variation looks natural'
        }
    
    def _check_capture_signature(self):
        """Check if capture rate is too high."""
        capture_rate = self.get_capture_rate()
        
        if len(self.capture_rate_history) < 10:
            return None
        
        # Humans typically have 60-75% capture rate
        # Perfect capture (>90%) or too low (<40%) is suspicious
        is_suspicious = capture_rate > 0.90 or capture_rate < 0.40
        
        return {
            'suspicious': is_suspicious,
            'rate': capture_rate,
            'recommendation': 'Capture rate too perfect' if capture_rate > 0.90 else 
                            'Capture rate too low' if capture_rate < 0.40 else
                            'Capture rate looks natural'
        }


class SessionBehavior:
    """Realistic session behavior (breaks, patterns, etc)."""
    
    def __init__(self):
        self.session_patterns = []
        self.break_schedule = self._generate_break_schedule()
        self.activity_bursts = []
        
    def _generate_break_schedule(self):
        """Generate realistic break schedule for session."""
        breaks = []
        current_time = 0
        
        # Breaks every 30-90 minutes of activity
        while current_time < 480:  # 8 hour session
            break_interval = random.randint(30, 90)
            break_duration = random.gauss(20, 10)  # Mean 20s breaks
            break_duration = max(5, min(120, break_duration))
            
            breaks.append({
                'time': current_time,
                'duration': break_duration,
            })
            
            current_time += break_interval
        
        return breaks
    
    def get_next_break(self, elapsed_minutes):
        """Get next scheduled break."""
        for break_info in self.break_schedule:
            if break_info['time'] > elapsed_minutes:
                return break_info
        
        return None
    
    def get_activity_pattern(self):
        """Get realistic activity pattern (burst/pause)."""
        # Activity isn't constant - humans have bursts and pauses
        # Pattern: 5-10 min active, 1-3 min pause
        
        if not self.activity_bursts:
            return 'active'
        
        last_pattern = self.activity_bursts[-1]
        time_since_last = time.time() - last_pattern['time']
        
        if last_pattern['type'] == 'active':
            # Check if should pause
            if time_since_last > last_pattern['duration']:
                pause_duration = random.randint(60, 180)
                self.activity_bursts.append({
                    'type': 'pause',
                    'time': time.time(),
                    'duration': pause_duration,
                })
                return 'pause'
        else:
            # Check if should resume
            if time_since_last > last_pattern['duration']:
                active_duration = random.randint(300, 600)
                self.activity_bursts.append({
                    'type': 'active',
                    'time': time.time(),
                    'duration': active_duration,
                })
                return 'active'
        
        return last_pattern['type']


# Integration helpers
def apply_human_like_delay(variance: BehavioralVariance):
    """Apply realistic human-like delay before action."""
    delay = variance.get_action_delay()
    time.sleep(delay)
    variance.record_action()


def apply_think_time():
    """Apply thinking time before major decision."""
    think_time = BehavioralVariance().get_think_time()
    time.sleep(think_time)


def get_realistic_headers():
    """Get randomized headers for requests."""
    return HeaderFingerprint.get_random_headers()


# Export main classes
__all__ = [
    'BezierCurveMovement',
    'BehavioralVariance',
    'HeaderFingerprint',
    'BotDetectionAvoidance',
    'SessionBehavior',
    'apply_human_like_delay',
    'apply_think_time',
    'get_realistic_headers',
]
