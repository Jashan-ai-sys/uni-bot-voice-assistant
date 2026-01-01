"""
API Key Rotation System
Automatically rotates between multiple Google API keys to avoid quota limits.
"""

import os
from dotenv import load_dotenv
import random

load_dotenv()

class APIKeyRotator:
    def __init__(self):
        # Load all API keys from .env
        self.api_keys = []
        
        # Primary key
        primary_key = os.getenv("GOOGLE_API_KEY")
        if primary_key:
            self.api_keys.append(primary_key)
        
        # Additional keys (add these to your .env file)
        for i in range(1, 6):  # Support up to 5 backup keys
            backup_key = os.getenv(f"GOOGLE_API_KEY_{i}")
            if backup_key:
                self.api_keys.append(backup_key)
        
        self.current_index = 0
        self.failed_keys = set()
    
    def get_key(self):
        """Get the current API key"""
        if not self.api_keys:
            raise ValueError("No API keys configured!")
        
        # Filter out failed keys
        available_keys = [k for k in self.api_keys if k not in self.failed_keys]
        
        if not available_keys:
            # Reset failed keys if all have failed
            self.failed_keys.clear()
            available_keys = self.api_keys
        
        # Return current key
        return available_keys[self.current_index % len(available_keys)]
    
    def rotate(self):
        """Rotate to next API key"""
        self.current_index += 1
        print(f"🔄 Rotated to API key #{self.current_index % len(self.api_keys) + 1}")
    
    def mark_failed(self, key):
        """Mark a key as failed (quota exceeded)"""
        self.failed_keys.add(key)
        print(f"❌ Marked key as failed. {len(self.failed_keys)}/{len(self.api_keys)} keys exhausted")
        self.rotate()
    
    def get_random_key(self):
        """Get a random API key (for load balancing)"""
        available_keys = [k for k in self.api_keys if k not in self.failed_keys]
        if not available_keys:
            self.failed_keys.clear()
            available_keys = self.api_keys
        return random.choice(available_keys)

# Global instance
rotator = APIKeyRotator()

def get_api_key():
    """Get current API key"""
    return rotator.get_key()

def rotate_key():
    """Rotate to next key"""
    rotator.rotate()
    return rotator.get_key()

def mark_key_failed(key):
    """Mark key as quota exceeded"""
    rotator.mark_failed(key)
    return rotator.get_key()
