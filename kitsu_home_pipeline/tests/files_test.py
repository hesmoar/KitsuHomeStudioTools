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


src_directory = r"X:\KitsuProjects\epic\Publish\Shot\SH999\rnd\epic_SH999_rnd_v005.png"
dst_directory = r"X:\KitsuProjects\epic\Publish\Shot\sh1000\rnd\epic_SH999_rnd_v003.kra"

def move_preview_to_publish(src_directory, dst_directory):
    src = Path(src_directory)
    dst = Path(dst_directory)

    print(f"Source path: {src}")
    print(f"Destination path: {dst}")

    _, preview_ext = os.path.splitext(src)
    preview_extension = preview_ext.lstrip(".")

    print(f"This is the original extension: {preview_extension}")

    filename = os.path.basename(dst)
    basename = os.path.splitext(filename)[0]
    print(f"This is the file name: {filename}")
    print(f"This is the base name: {basename}")
    new_filename = os.path.join(basename + "." + preview_extension)
    print(f"This is the new file name: {new_filename}")

    file_version = new_filename.split("_v")[-1].split(".")[0]
    print(f"This is the file version: {file_version}")

    new_folder_name = f"v{file_version}"
    print(f"New folder name: {new_folder_name}")

    dst_parent = dst.parent
    print(f"Destination parent folder: {dst_parent}")
    preview_folder = Path(dst_parent, new_folder_name, new_filename)

    print(f"Preview NEW path: {preview_folder}")



    if not dst.exists():
        print(f"Copying preview to publish: {preview_folder}")
        #shutil.copy2(src, preview_folder)
        print("Preview file copy succesfull")
    else:
        print("Preview file already in publish. Skipping Copy.")

move_preview_to_publish(src_directory, dst_directory)
                