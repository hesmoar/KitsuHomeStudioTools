#!/usr/bin/env python3
"""
Script to check and fix Kitsu configuration in keyring
"""

import keyring
import sys

def check_kitsu_config():
    """Check current Kitsu configuration in keyring"""
    print("🔍 Checking current Kitsu configuration...")
    
    try:
        url = keyring.get_password("kitsu", "url")
        email = keyring.get_password("kitsu", "email")
        password = keyring.get_password("kitsu", "password")
        
        print(f"Current URL: {url}")
        print(f"Current Email: {email}")
        print(f"Password set: {'Yes' if password else 'No'}")
        
        if url == "gazu.change.serverhost" or not url:
            print("\n❌ Problem detected: Invalid or missing Kitsu URL!")
            print("The URL 'gazu.change.serverhost' is a placeholder and won't work.")
            return False
        else:
            print("\n✅ Kitsu configuration looks good!")
            return True
            
    except Exception as e:
        print(f"❌ Error checking keyring: {e}")
        return False

def fix_kitsu_config():
    """Fix Kitsu configuration by setting correct values"""
    print("\n🔧 Let's fix your Kitsu configuration...")
    
    # Get correct values from user
    print("Please enter your Kitsu server information:")
    
    # Get Kitsu server URL
    while True:
        url = input("Kitsu Server URL (e.g., http://your-kitsu-server.com): ").strip()
        if url and not url.startswith("gazu.change"):
            break
        print("❌ Please enter a valid Kitsu server URL (not the placeholder)")
    
    # Get email
    email = input("Email: ").strip()
    if not email:
        print("❌ Email is required")
        return False
    
    # Get password
    password = input("Password: ").strip()
    if not password:
        print("❌ Password is required")
        return False
    
    # Save to keyring
    try:
        keyring.set_password("kitsu", "url", url)
        keyring.set_password("kitsu", "email", email)
        keyring.set_password("kitsu", "password", password)
        
        print("\n✅ Kitsu configuration saved successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error saving to keyring: {e}")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("🔧 Kitsu Configuration Fixer")
    print("=" * 50)
    
    # Check current config
    if check_kitsu_config():
        print("\nYour configuration looks good! The error might be temporary.")
        choice = input("Do you want to update it anyway? (y/n): ").lower()
        if choice != 'y':
            return
    else:
        print("\nConfiguration needs to be fixed.")
    
    # Fix config
    if fix_kitsu_config():
        print("\n🎉 Configuration updated! Try running your app again.")
    else:
        print("\n❌ Failed to update configuration.")

if __name__ == "__main__":
    main() 