"""
Immediate cancellation support - stops bot right away instead of finishing battle
"""

import os
import signal
import threading

class ImmediateCancel:
    """Handle immediate cancellation (Ctrl+C)"""
    
    def __init__(self):
        self.cancel_requested = False
        self.setup_signal_handler()
    
    def setup_signal_handler(self):
        """Setup Ctrl+C handler"""
        signal.signal(signal.SIGINT, self._handle_sigint)
    
    def _handle_sigint(self, signum, frame):
        """Handle Ctrl+C immediately"""
        self.cancel_requested = True
        print("\n\n⚠️  IMMEDIATE STOP REQUESTED")
        print("   Stopping after current action...")
        print("   (Press Ctrl+C again to force quit)")
        
        # If pressed again, force exit
        signal.signal(signal.SIGINT, self._force_quit)
    
    def _force_quit(self, signum, frame):
        """Force quit on second Ctrl+C"""
        print("\n\n❌ FORCE QUIT")
        exit(0)
    
    def is_cancelled(self):
        """Check if cancel was requested"""
        return self.cancel_requested
    
    def reset(self):
        """Reset cancel flag"""
        self.cancel_requested = False

# Global instance
_immediate_cancel = ImmediateCancel()

def is_immediate_cancel_requested():
    """Check if immediate cancel was requested"""
    return _immediate_cancel.is_cancelled()

def reset_immediate_cancel():
    """Reset immediate cancel flag"""
    _immediate_cancel.reset()

def request_immediate_cancel():
    """Request immediate cancel"""
    _immediate_cancel.cancel_requested = True
