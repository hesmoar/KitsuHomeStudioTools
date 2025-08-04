import os
import tempfile
import json
import shutil
import pprint
from pathlib import Path

test_path = r"D:\HecberryStuff\PAINANI STUDIOS\1_Proyectos\Active\1_Animaorquesta\PipeTest\RenderTest\Clips\moveTest"
new_renders_to_publish = []

json_file_path = r"C:\Users\Usuario\Documents\Dev\KitsuHomeStudioTools\kitsu_home_pipeline\UI\publisher\file_tree.json"
file_path = r"C:\Users\Usuario\AppData\Local\Temp\KitsuTaskManager\Context\Kitsu_task_context.json"



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

def get_context_from_json(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            context_data = json.load(file)
            #pprint.pprint(context_data)
            return context_data
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None



task_context = get_context_from_json(get_temp_dir())



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


# Functions for file paths
def map_kitsu_context_to_filetree(context):
    entity_type = context.get("task_type_for_entity", "").lower()

    base = {
        "Project_short_name": context.get("project_code", ""),
        "Project_name": context.get("project_name", ""),
        "Entity_Name": context.get("entity_name", ""),
        "TaskType": context.get("task_type_name", ""),
        "TaskType_Short_Name": context.get("task_code", ""),
        "task_type_for_entity": context.get("task_type_for_entity", ""),
        "AssetType": context.get("asset_type", ""),
        "Asset": context.get("asset", ""),
        "Version": "001",      
    }


    if entity_type == "shot":
        base.update({
            "Sequence": context.get("sequence", ""),
            "Shot": context.get("entity_name", ""),  # or context.get("shot", "")
        })
    elif entity_type == "asset":
        base.update({
            "Entity_Type": context.get("entity_type_name", "")
        })
    return base

def get_user_mountpoint():

    return os.environ.get("KITSU_PROJECTS_ROOT", "/mnt/kitsuProjects/")


def replace_placeholders(template, values, style=None):
    for key, value in values.items():
        if value is not None and value != "":
            template = template.replace(f"<{key}>", str(value))
        else:
            template = template.replace(f"<{key}>", "")
    
    import re
    template = re.sub(r'<[^>]+>', '', template) 
    
    if style == "lowercase":
        template = template.lower()
    elif style == "uppercase":
        template = template.upper()
    
    template = template.replace("//", "/").replace("__", "_").strip("_").strip("/")

    return template
#replace_placeholders()

def generate_paths(json_file_path, context, path_types=("working", "output")):
    with open(json_file_path, 'r') as file:
        file_tree = json.load(file)
        #pprint.pprint(file_tree)
    user_mountpoint = get_user_mountpoint()
    context["KITSU_PROJECTS_ROOT"] = user_mountpoint
    all_paths = {}
    for path_type in path_types:
        file_tree_section = file_tree.get(path_type)
        if not file_tree_section:
            raise ValueError(f"Invalid path_type: {path_type}")
        style = file_tree_section["folder_path"].get("style", None)
        mountpoint = replace_placeholders(file_tree_section["mountpoint"], context, style)
        

        folder_paths = {
            key: replace_placeholders(template, context, style)
            for key, template in file_tree_section["folder_path"].items()
            if key != "style"       
        }
        file_names = {
            key: replace_placeholders(template, context, style)
            for key, template in file_tree_section["file_name"].items()
            if key != "style"
        }

        full_paths = {
            key: str(Path(mountpoint) / folder_paths[key] / file_names[key])
            for key in folder_paths
        }
        all_paths[path_type] = full_paths
    print("These are the full paths")
    pprint.pprint(full_paths)
    return all_paths


def current_context_path():
    filetree_context = map_kitsu_context_to_filetree(task_context)
    all_paths = generate_paths(json_file_path, filetree_context)
    entity_type = filetree_context.get("task_type_for_entity", "").lower()
    print(f"This is the entity type: {entity_type}")
    if entity_type in all_paths["working"]:
        working_dir = all_paths["working"].get(entity_type)
        print(f"This is the working directory: {working_dir}")
    if entity_type in all_paths["output"]:
        output_dir = all_paths["output"].get(entity_type)
        print(f"This is the output directory: {output_dir}")
    else:
        working_dir = None
        print(f"Unknown entity type: {entity_type}")
    
    return working_dir, output_dir

#map_kitsu_context_to_filetree(task_context)
current_context_path()

#TODO: Something is broken here, please fix this when you come back