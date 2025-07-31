   # In file_utils.py
import os
import tempfile
import json
from pathlib import Path

def get_temp_dir(subfolder: str = None) -> Path:
       temp_base = Path(tempfile.gettempdir())
       if subfolder:
           temp_path = temp_base / subfolder
           temp_path.mkdir(parents=True, exist_ok=True)
           return temp_path
       return temp_base

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