import gazu
import os
import keyring


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


#connect_to_kitsu()