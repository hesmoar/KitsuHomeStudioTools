"""
Test script for Kitsu Home Studio package
"""

from kitsu_home_studio.core.auth import load_credentials, save_credentials
from kitsu_home_studio.integrations.resolve import ResolveIntegration
from kitsu_home_studio.integrations.krita import KritaIntegration
from kitsu_home_studio.utils.file_utils import get_software_path
from kitsu_home_studio.task_manager.gui import show_login_screen

def test_credentials():
    """Test if credentials are loaded correctly."""
    credentials = load_credentials()
    if credentials:
        print("Credentials loaded successfully:")
        print(f"Kitsu URL: {credentials['kitsu_url']}")
        print(f"Username: {credentials['username']}")
    else:
        print("No credentials found. Please run the task manager and log in first.")
        show_login_screen()

def test_software_integrations():
    """Test software integrations."""
    # Test Resolve integration
    resolve_path = get_software_path("Resolve.exe")
    if resolve_path:
        print(f"Resolve found at: {resolve_path}")
        resolve = ResolveIntegration(resolve_path)
        print(f"Resolve version: {resolve.get_version()}")
    else:
        print("Resolve not found")

    # Test Krita integration
    krita_path = get_software_path("krita.exe")
    if krita_path:
        print(f"Krita found at: {krita_path}")
        krita = KritaIntegration(krita_path)
        print(f"Krita version: {krita.get_version()}")
    else:
        print("Krita not found")

if __name__ == "__main__":
    print("Testing Kitsu Home Studio package...")
    print("\nTesting credentials:")
    test_credentials()
    print("\nTesting software integrations:")
    test_software_integrations() 