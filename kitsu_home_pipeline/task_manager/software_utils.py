import subprocess
import os
from PySide6.QtWidgets import QMessageBox
import time
import tempfile
import shutil
import json
from kitsu_home_pipeline.task_manager.resolve_utils import setup_resolve
from kitsu_home_pipeline.utils.file_utils import create_context_file

def launch_resolve(software_path, task_context):
    print("Launching DaVinci Resolve...")
    try:
        #subprocess.Popen([r"C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe"])
        subprocess.Popen([software_path])
        create_context_file(task_context)
        
        time.sleep(10)

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


def get_tmp_dir():
    return os.path.join(tempfile.gettempdir(), "KitsuTaskManager")

def get_tmp_context_dir():
    context_tmp_dir = os.path.join(get_tmp_dir(), "Context")
    context_tmp_file = os.path.join(context_tmp_dir, "Kitsu_task_context.json")

    return context_tmp_file
