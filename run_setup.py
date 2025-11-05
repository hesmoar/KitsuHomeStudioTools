import pathlib
import sys
from kitsu_home_pipeline.utils import config  # Assuming config.py is in a 'utils' folder
import os

def prompt_for_studio_folder() -> str | None:
    """
    Keeps asking the user for the Studio Folder path until
    a valid, existing directory is provided.
    
    Returns the valid path as a string, or None if the user cancels.
    """
    print("--- KitsuHomeStudioTools Setup ---")
    print("We need to know the location of your main 'Studio' folder.")
    print("This is the root directory where all your projects are stored.")
    print("(Type 'q' or 'quit' to exit setup)\n")

    while True:
        # 1. Get input from the user
        user_input = input("Enter Studio Folder path: ").strip()

        # 2. Check for quit command
        if user_input.lower() in ('q', 'quit'):
            print("Setup cancelled.")
            return None

        # 3. Validate the path
        if not user_input:
            print("Path cannot be empty. Please try again.")
            continue
            
        try:
            # Create a Path object to check it
            abs_path_str = os.path.abspath(user_input)
            studio_path = pathlib.Path(abs_path_str)


            if not studio_path.exists():
                print(f"Error: Path not found.")
                print(f"We could not find: {studio_path}")
                print("Please check the path and try again.")
                continue

            #if not studio_path.is_dir():
            #    print(f"Error: This is a file, not a directory.")
            #    print("Please provide the path to a folder.")
            #    continue

            # 4. Success!
            # Convert to absolute path and string for consistent saving
            valid_path = abs_path_str
            print(f"Studio folder set to: {valid_path}\n")
            return valid_path

        except Exception as e:
            # Catch any other unexpected path errors
            print(f"An unexpected error occurred: {e}")
            print("Please try again.")


def run_configuration_setup():
    """
    Main setup function.
    
    This loads the config. If the 'StudioFolder' is not set,
    it will run the setup prompt to get it from the user.
    """
    
    # 1. Load the current config (merges defaults with saved file)
    print("Loading configuration...")
    app_config = config.load_config()

    # 2. Check if the key setting is missing
    studio_folder = app_config.get("StudioFolder")
    
    if studio_folder:
        print(f"Configuration already set.")
        print(f"Studio Folder: {studio_folder}")
        print("To change this, edit the config.json file directly.")
        # In a real app, you might have a 'force' flag
        # e.g., if 'force' in sys.argv: ...
        return True

    # 3. The setting is missing, so run the prompt
    print("Configuration is missing. Starting first-time setup...")
    new_path = prompt_for_studio_folder()

    if new_path:
        # 4. User provided a valid path. Update the config dict.
        app_config["StudioFolder"] = new_path
        
        # 5. Save the updated dict back to config.json
        config.save_config(app_config)
        print("Configuration saved successfully!")
        return True
    else:
        # User cancelled the prompt
        print("Setup was not completed. The application may not work.")
        print("Please run setup again when you are ready.")
        return False


if __name__ == "__main__":
    run_configuration_setup()