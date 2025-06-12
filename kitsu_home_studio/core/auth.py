"""
Core authentication module for Kitsu integration
"""

import os
import json
from pathlib import Path
import requests
import keyring


def get_credentials_path():
    """Get the path to the credentials file."""
    return os.path.join(os.path.expanduser("~"), ".kitsu", "credentials.json")

def load_credentials():
    """Load stored credentials if they exist."""
    try:
        # Try to get credentials from keyring first
        kitsu_url = keyring.get_password("kitsu_home_studio", "kitsu_url")
        username = keyring.get_password("kitsu_home_studio", "username")
        password = keyring.get_password("kitsu_home_studio", "password")
        
        if all([kitsu_url, username, password]):
            return {
                "kitsu_url": kitsu_url,
                "username": username,
                "password": password
            }
    except Exception as e:
        print(f"Error loading credentials from keyring: {e}")
    
    # Fallback to file-based storage if keyring fails
    credentials_path = get_credentials_path()
    if os.path.exists(credentials_path):
        with open(credentials_path, "r") as f:
            return json.load(f)
    return None

def save_credentials(credentials):
    """Save credentials to keyring and file as backup."""
    try:
        # Save to keyring
        keyring.set_password("kitsu_home_studio", "kitsu_url", credentials["kitsu_url"])
        keyring.set_password("kitsu_home_studio", "username", credentials["username"])
        keyring.set_password("kitsu_home_studio", "password", credentials["password"])
    except Exception as e:
        print(f"Error saving credentials to keyring: {e}")
        # Fallback to file-based storage
        credentials_path = get_credentials_path()
        os.makedirs(os.path.dirname(credentials_path), exist_ok=True)
        with open(credentials_path, "w") as f:
            json.dump(credentials, f)

def clear_credentials():
    """Clear stored credentials from both keyring and file."""
    try:
        # Clear from keyring
        keyring.delete_password("kitsu_home_studio", "kitsu_url")
        keyring.delete_password("kitsu_home_studio", "username")
        keyring.delete_password("kitsu_home_studio", "password")
    except Exception as e:
        print(f"Error clearing credentials from keyring: {e}")
    
    # Clear from file
    credentials_path = get_credentials_path()
    if os.path.exists(credentials_path):
        os.remove(credentials_path)

def connect_to_kitsu(kitsu_url, username, password):
    """Connect to Kitsu and verify credentials."""
    # Remove trailing /api if present
    kitsu_url = kitsu_url.rstrip("/api")
    
    # Test connection
    response = requests.get(f"{kitsu_url}/api/status")
    if response.status_code != 200:
        raise Exception("Could not connect to Kitsu server")
    
    # Test authentication
    auth_response = requests.post(
        f"{kitsu_url}/api/auth/login",
        json={"email": username, "password": password}
    )
    
    if auth_response.status_code != 200:
        raise Exception("Invalid credentials")
    
    # Save credentials if connection successful
    credentials = {
        "kitsu_url": kitsu_url,
        "username": username,
        "password": password
    }
    save_credentials(credentials)
    
    return True 