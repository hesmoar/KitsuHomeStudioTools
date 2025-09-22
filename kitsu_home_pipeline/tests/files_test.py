import os
import shutil
from pathlib import Path

path_A = r"P:/1_Proyectos"
path_B = r"K:/KitsuProjects"
path_C = r"W:/SomethingElse"

def collect_published_files(src_directory):
    published_files = {}
    ignored_files = {"desktop.ini", ".ds_store", "thumbs.db"}
    src = Path(src_directory)
    #if src.exists() and src.is_dir():
    if os.path.exists(src_directory) and os.path.isdir(src_directory):
        print(f"Scanning directory: {src_directory}")
        try:
            with os.scandir(src_directory) as entries:
                for entry in entries:
                    if entry.is_file() and entry.name.lower() not in ignored_files:
                        published_files[entry.name] = entry.path
                        print(f"Found published file {entry.name}")
                    else:
                        print(f"This is not a file {entry.name}")
        except Exception as e:
            print(f"Error scanning directory {src_directory}")
    else:
        print(f"Source directory does not exist {src_directory}")

    print("Collected files: ")
    for name, path in published_files.items():
        print(f"{name}: {path}")

    return published_files

collect_published_files(path_C)
                