import platformdirs
import pathlib
import json
import os

APP_NAME = "KitsuHomeStudioTools"
APP_AUTHOR = "HomeStudioPipe"


DEFAULT_CONFIG = {
    "StudioFolder" : ""
}

def get_config_dir() -> pathlib.Path:
    """
    Finds the platform-specific config directory.
    - Windows: C:/Users/User/AppData/Local/KitsuHomeStudioTools
    - macOS:   ~/Library/Application Support/KitsuHomeStudioTools
    - Linux:   ~/.config/KitsuHomeStudioTools
    """
    config_dir = pathlib.Path(platformdirs.user_data_dir(APP_NAME, APP_AUTHOR))
    
    # Create the directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def get_config_file_path():
    return get_config_dir() / "config.json"

def load_config() -> dict:
    
    config_file_path = get_config_file_path()

    config = DEFAULT_CONFIG.copy()

    try:
        if config_file_path.exists():
            with open(config_file_path, 'r') as f:
                saved_config = json.load(f)

                config.update(saved_config)
    except json.JSONDecodeError:
        print("Warning: Config file is corrupted. Using default configuration.")
        save_config(config)
    except Exception as e:
        print(f"Error loading config: {e}")
    return config

def save_config(config_data):
    config_path = get_config_file_path()

    try:
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        print(f"Error saving config file: {e}")
