"""
Performance optimization for long training sessions
- Memory management
- Connection pooling
- Response caching
- Battle result parsing optimization
"""

import gc
import psutil
import os
from collections import deque

class PerformanceOptimizer:
    def __init__(self):
        self.memory_threshold = 500  # MB
        self.last_gc = 0
        self.gc_interval = 100  # battles
        self.response_cache = deque(maxlen=10)  # Keep last 10 responses
        self.process = psutil.Process(os.getpid())
    
    def get_memory_usage(self):
        """Get current memory usage in MB"""
        try:
            return self.process.memory_info().rss / 1024 / 1024
        except:
            return 0
    
    def optimize_memory(self, battle_count):
        """Clean up memory periodically"""
        if battle_count % self.gc_interval == 0:
            memory_before = self.get_memory_usage()
            gc.collect()
            memory_after = self.get_memory_usage()
            print(f"  [MEMORY] {memory_before:.1f}MB -> {memory_after:.1f}MB")
            
            if memory_after > self.memory_threshold:
                print(f"  [WARNING] High memory usage: {memory_after:.1f}MB")
    
    def cache_response(self, url, content):
        """Cache recent responses to avoid re-fetching"""
        self.response_cache.append({'url': url, 'content': content})
    
    def get_cached_response(self, url):
        """Get cached response if available"""
        for item in self.response_cache:
            if item['url'] == url:
                return item['content']
        return None

class ConnectionPoolManager:
    """Reuse connections to reduce overhead"""
    def __init__(self):
        self.session = None
        self.max_retries = 3
        self.timeout = 10
    
    def set_session(self, session):
        self.session = session
        # Configure connection pooling
        adapter_kwargs = {
            'pool_connections': 10,
            'pool_maxsize': 10,
            'max_retries': self.max_retries
        }
        from requests.adapters import HTTPAdapter
        for protocol in ('http://', 'https://'):
            self.session.mount(protocol, HTTPAdapter(**adapter_kwargs))
    
    def get(self, url, **kwargs):
        """Optimized GET with pooling"""
        if not self.session:
            raise RuntimeError("Session not set")
        
        kwargs.setdefault('timeout', self.timeout)
        return self.session.get(url, **kwargs)

class BattleResultParser:
    """Optimized battle result extraction"""
    
    @staticmethod
    def extract_battle_result(html):
        """Extract battle result from HTML efficiently"""
        try:
            # Look for battle result patterns
            if "won" in html.lower():
                # Extract XP if possible
                import re
                xp_match = re.search(r'(\d+)\s*(?:XP|xp|experience)', html)
                xp = int(xp_match.group(1)) if xp_match else 0
                return {'won': True, 'xp': xp}
            elif "lost" in html.lower():
                return {'won': False, 'xp': 0}
        except:
            pass
        return None
