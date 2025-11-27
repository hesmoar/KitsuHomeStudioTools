import gazu
import keyring
import sys
import requests


try:
    from Resources import prvt_config
    # Load "Baked-in" secrets
    BAKED_CF_ID = prvt_config.CF_CLIENT_ID
    BAKED_CF_SECRET = prvt_config.CF_CLIENT_SECRET
    BAKED_URL = prvt_config.KITSU_DEFAULT_URL
except ImportError:
    # Fallback if running from source without the config file
    BAKED_CF_ID = None
    BAKED_CF_SECRET = None
    BAKED_URL = None
    print("WARNING: private_config.py not found. Cloudflare tokens missing.")

def configure_gazu_headers():
    """
    Injects the baked-in tokens AND User-Agent into Gazu.
    """
    if BAKED_CF_ID and BAKED_CF_SECRET:
        # We add the User-Agent here to match the working debug script
        headers = {
            "CF-Access-Client-Id": BAKED_CF_ID,
            "CF-Access-Client-Secret": BAKED_CF_SECRET,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        gazu.client.default_client.session.headers.update(headers)
        print("Secure tunnel established (Headers & User-Agent Injected).")
        return headers # Return them so we can use them for debugging
    else:
        print("Warning: No Cloudflare tokens found.")
        return {}

def login_ui_logic(kitsu_url, user_email, user_password):
    # --- STEP 1: FIX THE URL (The 405 Fix) ---
    # We must ensure the URL ends in '/api', otherwise Gazu hits the website frontend
    if "http" in kitsu_url:
        from urllib.parse import urlparse
        parsed = urlparse(kitsu_url)
        # Rebuild just the scheme and netloc (e.g. https://site.com)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
    else:
        base_url = kitsu_url.strip().rstrip("/")

    # Force add /api if it's missing
    # Gazu needs this to talk to the backend, not the frontend
    if not base_url.endswith("/api"):
        clean_url = f"{base_url}/api"
    else:
        clean_url = base_url
    
    print(f"Connecting to API: {clean_url}")

    # --- STEP 2: SET HOST (Resets Session) ---
    gazu.client.set_host(clean_url)

    # --- STEP 3: FORCE HEADERS BACK IN (The Missing Token Fix) ---
    # We grab the session object that 'set_host' just created
    session = gazu.client.default_client.session
    
    if BAKED_CF_ID and BAKED_CF_SECRET:
        session.headers.update({
            "CF-Access-Client-Id": BAKED_CF_ID,
            "CF-Access-Client-Secret": BAKED_CF_SECRET,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        print(f"DEBUG: Re-Injected Headers. Current keys: {list(session.headers.keys())}")
    
    # --- STEP 4: EXECUTE LOGIN ---
    try:
        if gazu.log_in(user_email, user_password):
            print("Login Success!")
            # Save the clean_url (with /api) so auto-login works next time
            save_credentials(clean_url, user_email, user_password) 
            return True
        else:
            return False
    except Exception as e:
        print(f"Login Failed: {e}")
        raise e

# ----------------------------------------------------------------------

def set_env_variables(kitsu_url, kitsu_email, kitsu_password):

    print("Setting environment variables")
    print(f"KITSU_URL: {kitsu_url}")
    print(f"KITSU_EMAIL: {kitsu_email}")
    print(f"KITSU_PASSWORD: {kitsu_password}")

def save_credentials(kitsu_url, kitsu_email, kitsu_password):
    #prefix = "http://"
    #sufix = "/api"
    #simple_url = kitsu_url
    #url = prefix + simple_url + sufix
    keyring.set_password("kitsu", "password", kitsu_password)
    keyring.set_password("kitsu", "email", kitsu_email)
    keyring.set_password("kitsu", "url", kitsu_url)
    print("Credentials saved to securely")


def load_credentials():
    kitsu_url = keyring.get_password("kitsu", "url")
    kitsu_email = keyring.get_password("kitsu", "email")
    kitsu_password = keyring.get_password("kitsu", "password")

    if kitsu_url and kitsu_email and kitsu_password:
        return {
            "kitsu_url": kitsu_url,
            "username": kitsu_email,
            "password": kitsu_password
        }
    return None

def clear_credentials():
    keyring.delete_password("kitsu", "url")
    keyring.delete_password("kitsu", "email")
    keyring.delete_password("kitsu", "password")
    print("Credentials cleared")

def connect_to_kitsu(kitsu_url, kitsu_email, kitsu_password):
    save_credentials(kitsu_url, kitsu_email, kitsu_password)
    url = keyring.get_password("kitsu", "url")
    email = keyring.get_password("kitsu", "email")
    password = keyring.get_password("kitsu", "password")
    gazu.client.set_host(url)
    logged_in = gazu.log_in(email, password)
    if logged_in:
        print("Kitsu Login successful!")
    else:
        raise Exception("Kitsu Login failed!")
    
    
def kitsu_auto_login():
    url = keyring.get_password("kitsu", "url")
    email = keyring.get_password("kitsu", "email")
    password = keyring.get_password("kitsu", "password")
    gazu.client.set_host(url)
    logged_in = gazu.log_in(email, password)
    if logged_in:
        print("Kitsu Login successful!")
    else:
        raise Exception("Kitsu Login failed!")
