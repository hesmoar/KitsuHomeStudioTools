import os
import tempfile
import json
import shutil
from pathlib import Path

def get_temp_dir() -> Path:
       temp_base = Path(tempfile.gettempdir())
       subfolder = "KitsuTaskManager"
       print(f"Temporary base directory: {temp_base}")
       if subfolder:
           temp_path = temp_base / subfolder
           print(temp_path)
           temp_path.mkdir(parents=True, exist_ok=True)
           print(f"Temporary directory created at: {temp_path}")
           return temp_path

def get_context_file_path() -> Path:
    """Get the path to the context file in the temporary directory."""
    temp_dir = get_temp_dir()

    context_file_path = temp_dir / "Context" / "Kitsu_task_context.json"
    print(context_file_path)
    if context_file_path.exists():
        print(f"Context file exists at: {context_file_path}")

    return context_file_path


def create_context_file(task_context):
    temp_dir = os.path.join(tempfile.gettempdir(), r"KitsuTaskManager\Context")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = os.path.join(temp_dir, "Kitsu_task_context.json")

    with open(temp_file, "w") as f:
        json.dump(task_context, f, indent=4)
    print(f"Context file created at {temp_file}")

def clean_up_temp_files():
    temp_dir = os.path.join(tempfile.gettempdir(), "KitsuTaskManager")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def get_unique_filename(base_name, directory, extension=""):
    """Generate a unique filename with an incremental version number."""
    directory = Path(directory)
    if not directory.exists():
        print(f"Error: Export directory '{directory}' does not exist.")
        return None, None
    extension = f".{extension}" if extension else ""
    pattern = f"{base_name}_v*{extension}"
    existing_versions = [ 
        int(f.stem[len(base_name) + 2 :].split("_")[0])
        for f in directory.glob(pattern)
        if f.stem[len(base_name) + 2 :].split("_")[0].isdigit()
    ]

    version = max(existing_versions, default=0) + 1
    filename = f"{base_name}_v{version:03d}{extension}"
    full_file_path = directory / filename
    return str(full_file_path), filename
