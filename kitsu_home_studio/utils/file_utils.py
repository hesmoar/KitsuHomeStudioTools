"""
File utility functions
"""

import os
import json
import tempfile
import shutil
from pathlib import Path

def create_context_file(task_context: dict) -> str:
    """Create a context file with task information."""
    temp_dir = os.path.join(tempfile.gettempdir(), "KitsuTaskManager", "Context")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = os.path.join(temp_dir, "Kitsu_task_context.json")

    with open(temp_file, "w") as f:
        json.dump(task_context, f, indent=4)
    
    return temp_file

def clean_up_temp_files() -> None:
    """Clean up temporary files."""
    temp_dir = os.path.join(tempfile.gettempdir(), "KitsuTaskManager")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

def get_software_path(executable_name: str) -> str:
    """Get the path to a software executable."""
    # Check PATH
    for path in os.environ["PATH"].split(os.pathsep):
        executable_path = os.path.join(path, executable_name)
        if os.path.exists(executable_path):
            return executable_path
    
    # Check common installation paths
    common_paths = [
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        r"C:\Users\%USERNAME%\AppData\Local\Programs",
    ]
    
    for base_path in common_paths:
        for root, dirs, files in os.walk(base_path):
            if executable_name in files:
                return os.path.join(root, executable_name)
            if root.count(os.sep) - base_path.count(os.sep) >= 2:
                del dirs[:]
    
    return None 