import gazu
import os
import keyring

#kitsu_url = os.getenv("KITSU_URL")
#kitsu_email = os.getenv("KITSU_EMAIL")
#kitsu_password = os.getenv("KITSU_PASSWORD")

# FIXME: This should take the info from the GUI and set as env variables
def set_env_variables(kitsu_url, kitsu_email, kitsu_password):
    #os.environ["KITSU_URL"] = kitsu_url
    #os.environ["KITSU_EMAIL"] = kitsu_email
    #os.environ["KITSU_PASSWORD"] = kitsu_password
    print("Setting environment variables")
    print(f"KITSU_URL: {kitsu_url}")
    print(f"KITSU_EMAIL: {kitsu_email}")
    print(f"KITSU_PASSWORD: {kitsu_password}")

def save_credentials(kitsu_url, kitsu_email, kitsu_password):
    keyring.set_password("kitsu", "password", kitsu_password)
    keyring.set_password("kitsu", "email", kitsu_email)
    keyring.set_password("kitsu", "url", kitsu_url)
    print("Credentials saved to securely")
#if kitsu_url and kitsu_url.startswith("https://"):
#    print("Warning your KITSU_URL is using https instead of http")
# Login

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


#connect_to_kitsu()