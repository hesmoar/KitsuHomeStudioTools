import sys
import os


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def compare_version_values(working_file_version_input, kitsu_preview_version_input):

    working_file_version = int(working_file_version_input)
    kitsu_preview_version = int(kitsu_preview_version_input)
    
    if kitsu_preview_version == working_file_version:
        print("The working file revision matches the highest preview revision, need to add 1 to both")
        new_working_file_version = working_file_version + 1
        new_kitsu_preview_version = kitsu_preview_version + 1
        print(f"These are the new values, working file: {new_working_file_version}, and kitsu revision: {new_kitsu_preview_version}")

    elif kitsu_preview_version > working_file_version:
        print("Highest preview revision is bigger than working file, need to update to working file to match highest revision + 1")
        new_working_file_version = kitsu_preview_version + 1
        new_kitsu_preview_version = kitsu_preview_version + 1
        print(f"These are the new values, working file: {new_working_file_version}, and kitsu revision: {new_kitsu_preview_version}")

    elif kitsu_preview_version < working_file_version:
        print("Highest preview revision is smaller than working file, need to update working file to match highest revision + 1 (not sure) ")
        new_working_file_version = working_file_version
        new_kitsu_preview_version = working_file_version
        print(f"These are the new values, working file: {new_working_file_version}, and kitsu revision: {new_kitsu_preview_version}")
    return new_working_file_version, new_kitsu_preview_version