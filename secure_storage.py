"""
Secure Storage with Platform-Aware Fallback

Uses keyring on desktop, plain text file on Termux/Android.
"""

import json
from pathlib import Path


class SecureStorage:
    """Manage credentials with platform-aware storage."""

    @staticmethod
    def is_termux():
        """Check if running in Termux."""
        return Path("/data/data/com.termux").exists()

    @classmethod
    def get_storage_path(cls):
        """Get storage path for credentials."""
        if cls.is_termux():
            # Use local file storage on Termux
            storage_dir = Path.home() / ".rpgbot"
            storage_dir.mkdir(exist_ok=True)
            return storage_dir / "credentials.json"
        else:
            # Use keyring on desktop
            return None

    @classmethod
    def save_credential(cls, username, password):
        """Save username/password."""
        
        if cls.is_termux():
            return cls._save_to_file(username, password)
        else:
            return cls._save_to_keyring(username, password)

    @classmethod
    def get_credential(cls, username):
        """Get saved password for username."""
        
        if cls.is_termux():
            return cls._get_from_file(username)
        else:
            return cls._get_from_keyring(username)

    @classmethod
    def remove_credential(cls, username):
        """Remove saved credential."""
        
        if cls.is_termux():
            return cls._remove_from_file(username)
        else:
            return cls._remove_from_keyring(username)

    @staticmethod
    def _save_to_file(username, password):
        """Save to local file (Termux)."""
        storage_path = SecureStorage.get_storage_path()
        
        try:
            # Load existing credentials
            credentials = {}
            if storage_path.exists():
                with open(storage_path, 'r') as f:
                    credentials = json.load(f)
            
            # Add/update credential
            credentials[username] = password
            
            # Save with restricted permissions
            with open(storage_path, 'w') as f:
                json.dump(credentials, f, indent=2)
            
            # Make file readable only by owner (600 permissions)
            import os
            os.chmod(storage_path, 0o600)
            
            return True
        except Exception as e:
            print(f"Error saving credential: {e}")
            return False

    @staticmethod
    def _get_from_file(username):
        """Get from local file (Termux)."""
        storage_path = SecureStorage.get_storage_path()
        
        try:
            if not storage_path.exists():
                return None
            
            with open(storage_path, 'r') as f:
                credentials = json.load(f)
            
            return credentials.get(username)
        except Exception:
            return None

    @staticmethod
    def _remove_from_file(username):
        """Remove from local file (Termux)."""
        storage_path = SecureStorage.get_storage_path()
        
        try:
            if not storage_path.exists():
                return True
            
            with open(storage_path, 'r') as f:
                credentials = json.load(f)
            
            if username in credentials:
                del credentials[username]
                
                with open(storage_path, 'w') as f:
                    json.dump(credentials, f, indent=2)
            
            return True
        except Exception:
            return False

    @staticmethod
    def _save_to_keyring(username, password):
        """Save to keyring (Desktop)."""
        try:
            import keyring
            keyring.set_password("rpgbot", username, password)
            return True
        except Exception as e:
            print(f"Error saving to keyring: {e}")
            return False

    @staticmethod
    def _get_from_keyring(username):
        """Get from keyring (Desktop)."""
        try:
            import keyring
            return keyring.get_password("rpgbot", username)
        except Exception:
            return None

    @staticmethod
    def _remove_from_keyring(username):
        """Remove from keyring (Desktop)."""
        try:
            import keyring
            keyring.delete_password("rpgbot", username)
            return True
        except Exception:
            return False

