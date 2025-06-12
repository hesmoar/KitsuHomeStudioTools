import subprocess
import os
from kitsu_home_pipeline.task_manager.resolve_utils import setup_resolve
from PySide6.QtWidgets import QMessageBox
import time
import tempfile
import shutil
import json

def launch_resolve(software_path, task_context):
    print("Launching DaVinci Resolve...")
    try:
        #subprocess.Popen([r"C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe"])
        subprocess.Popen([software_path])
        create_context_file(task_context)
        
        time.sleep(35)

        #setup_resolve()
    except FileNotFoundError:
        QMessageBox.warning(f"Error: {software_path} not found. Please check the path.")
    except Exception as e:
        QMessageBox.warning(f"Error Failed to launch software:{e}")

def launch_krita(software_path, task_context):
    print("Launching Krita...")
    try:
        #subprocess.Popen([r"C:\Program Files\Krita (x64)\bin\krita.exe"])
        subprocess.Popen([software_path])
        create_context_file(task_context)
    except FileNotFoundError:
        QMessageBox.warning(f"Error: {software_path} not found. Please check the path.")
    except Exception as e:
        QMessageBox.warning(f"Error Failed to launch software:{e}")

def launch_nuke(software_path):
    print("Launching Nuke...")


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