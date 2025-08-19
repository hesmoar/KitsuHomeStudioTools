import gazu
import keyring
import pprint

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
    


def get_output_file_types():

    output_file_types = gazu.files.all_output_types()

    pprint.pprint(output_file_types)

kitsu_auto_login()
get_output_file_types()