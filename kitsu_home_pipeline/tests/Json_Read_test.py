
import json
import os
import pprint
from kitsu_home_pipeline.UI.publisher.kitsu_project_context import get_context_from_json

json_file_path = r"C:\Users\Usuario\Documents\Dev\KitsuHomeStudioTools\kitsu_home_pipeline\UI\publisher\file_tree.json"
file_path = r"C:\Users\Usuario\AppData\Local\Temp\KitsuTaskManager\Context\Kitsu_task_context.json"

task_context = get_context_from_json(file_path)

pprint.pprint(task_context)


def read_file_tree_json(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            context_data = json.load(file)
            #pprint.pprint(context_data)
        return context_data

    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None
    

def map_kitsu_context_to_filetree(context):
    return {
        "Project_short_name": context.get("project_code", ""),
        "Project_name": context.get("project_name", ""),
        "Entity_Type": context.get("entity_type_name", ""),
        "Entity_Name": context.get("entity_name", ""),
        "TaskType": context.get("task_type_name", ""),
        "TaskType_Short_Name": context.get("task_code", ""),
        "Sequence": context.get("sequence", ""),
        "Shot": context.get("entity_name", ""),  # or context.get("shot", "")
        "AssetType": context.get("asset_type", ""),
        "Asset": context.get("asset", ""),
        "Version": "001",      
    }

def replace_placeholders(template, values, style=None):
    for key, value in values.items():
        template = template.replace(f"<{key}>", value)
    
    if style == "lowercase":
        template = template.lower()
    elif style == "uppercase":
        template = template.upper()

    return template
#replace_placeholders()

def generate_paths(json_file_path, context, path_type="working"):
    with open(json_file_path, 'r') as file:
        file_tree = json.load(file)
        #pprint.pprint(file_tree)
    file_tree_section = file_tree.get(path_type)
    #print(f"THIS IS FILE TREE SECTION: {file_tree_section}")
    if not file_tree_section:
        raise ValueError(f"Invalid path_type: {path_type}")
    style = file_tree_section["folder_path"].get("style", None)
    folder_paths = {}
    for key, template in file_tree_section["folder_path"].items():
        if key != "style":
            folder_paths[key] = replace_placeholders(template, context, style)
    mountpoint = replace_placeholders(file_tree_section["mountpoint"], context, style)
    file_name = replace_placeholders(file_tree_section["file_name"], context, style)
    print(f"File name: {file_name}")
    full_paths = {key: os.path.join(mountpoint, folder_paths[key]) for key in folder_paths}
    print("These are the full paths")
    pprint.pprint(full_paths)
    return full_paths


filetree_context = map_kitsu_context_to_filetree(task_context)
full_working_path = generate_paths(json_file_path, filetree_context, path_type="working")
full_output_path = generate_paths(json_file_path, filetree_context, path_type="output")

entity_type = filetree_context.get("Entity_Type", "").lower()
print(f"This is the entity type: {entity_type}")

if entity_type in full_working_path:
    working_dir = full_working_path[entity_type]
    print(f"This is the working directory: {working_dir}")
else:
    working_dir = None
    print(f"Unknown entity type: {entity_type}")

if entity_type in full_output_path:
    output_dir = full_output_path[entity_type]
    print(f"This is the output directory: {output_dir}")
else:
    output_dir = None
    print(f"Unknown entity type: {entity_type}")
