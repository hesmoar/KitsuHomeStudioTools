import os
import re
import tempfile
import json
import shutil
import pprint
from pathlib import Path



test_path = r"D:\HecberryStuff\PAINANI STUDIOS\1_Proyectos\Active\1_Animaorquesta\PipeTest\RenderTest\Clips\moveTest"
new_renders_to_publish = []

#json_file_path = r"C:\Users\Usuario\Documents\Dev\KitsuHomeStudioTools\kitsu_home_pipeline\UI\publisher\file_tree.json"
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

def get_context_from_json():

    try:
        json_file_path = get_context_file_path()
        with open(json_file_path, 'r') as file:
            context_data = json.load(file)
            #pprint.pprint(context_data)
            return context_data
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None


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
def map_kitsu_context_to_filetree():
    context_dict = get_context_from_json()
    entity_type = context_dict.get("task_type_for_entity", "").lower()

    base = {
        "project.code": context_dict.get("project_code", ""),
        "project.name": context_dict.get("project_name", ""),
        "entity.name": context_dict.get("entity_name", ""),
        "TaskType": context_dict.get("task_type_name", ""),
        "task_type.short_name": context_dict.get("task_code", ""),
        "task_type_for_entity": context_dict.get("task_type_for_entity", ""),
        "AssetType": context_dict.get("asset_type", ""),
        "Asset": context_dict.get("asset", ""),
        "Version": "001",      
    }


    if entity_type == "shot":
        base.update({
            "Sequence": context_dict.get("sequence", ""),
            "Shot": context_dict.get("entity_name", ""),  # or context_dict.get("shot", "")
        })
    elif entity_type == "asset":
        base.update({
            "Entity_Type": context_dict.get("entity_type", "")
        })
    pprint.pprint(base)
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

def generate_paths(context, path_types=("working", "output")):
    from kitsu_home_pipeline.utils.kitsu_utils import get_file_tree
    project_name = context.get("Project_name")
    print(f"This is the project: {project_name}")
    file_tree = get_file_tree(project_name)
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

def network_drive_detected(drive_letter):
    drive_path = f"{drive_letter.upper()}:\\"
    print(f"Checking for drive: {drive_path}")
    if os.path.exists(drive_path):
        print(f"Network drive {drive_letter} detected")
        return drive_path
    else:
        print(f"Network drive {drive_letter} not detected.")
        return None

def current_context_path():
    filetree_context = map_kitsu_context_to_filetree()
    all_paths = generate_paths(filetree_context)
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

def create_main_directory(base_drive, root_folder, projects):

    root_path = Path(base_drive) / root_folder
    for project in projects:
        project_path = Path(root_path) / project
        subfolders = ["Publish", "Working"]
        for subfolder in subfolders:
            folder_path = project_path / subfolder
            subSubfolders = ["Asset", "Shot"]
            for subSubfolder in subSubfolders:
                subfolder_path = folder_path / subSubfolder
                if not subfolder_path.exists():
                    print(f"Creating main directory on {subfolder_path}...")
                    subfolder_path.mkdir(parents=True, exist_ok=True)
                    print(f"Main directory created at: {subfolder_path}")
                else:
                    print(f"Main directory already exists at: {subfolder_path}")

    #print(f"THIS IS THE SUBFOLDER PATH: {subfolder_path}")
    return subfolder_path

def create_entity_directory(root_path, project, entity_type, task_code, entity_name):
    project_path = Path(root_path) / project
    if entity_type.lower() == "shot":
        #entity_path = Path()
        #subfolders = [entity_name, task_code]
        print("Creating directory for shot")
        base_folder = "Shot"

    elif entity_type.lower() == "asset":
        print("Creating  directory for asset")
        base_folder = "Asset"

    else:
        print(f"Unknown entity type: {entity_type}")
        return None, None
    
    publish_path = project_path / "Publish" / base_folder / entity_name / task_code
    working_path = project_path / "Working" / base_folder / entity_name / task_code
    
    for full_path in [publish_path, working_path]:
        try:
            print(f"Creating directory: {full_path}...")
            full_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creating directory {full_path}: {e}")
            #print(f"Directory already exists: {full_path}")
    return str(publish_path), str(working_path)

def move_working_to_publish(src_directory, dst_directory):
    src = Path(src_directory)
    dst = Path(dst_directory)

    if not dst.exists():
        print(f"Copying file to publish: {dst}")
        shutil.copy2(src, dst)
        print("File Copy succesfull")
    else:
        print("File already in publish. Skipping Copy.")

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
    version_folder = dst_parent / new_folder_name
    version_folder.mkdir(parents=True, exist_ok=True)


    preview_folder = version_folder / new_filename

    print(f"Preview NEW path: {preview_folder}")



    if not preview_folder.exists():
        print(f"Copying preview to publish: {preview_folder}")
        shutil.copy2(src, preview_folder)
        print("Preview file copy succesfull")
    else:
        print("Preview file already in publish. Skipping Copy.")

def create_file_name(project_code, entity_name, task_code):
    base_name = f"{project_code}_{entity_name}_{task_code}"

    print(f"This is the filename: {base_name} ")
    return base_name



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

def create_working_from_publish(published_file_path, working_directory):
    #This function should do the following: from the published directory using the get unique filename function it should increase the version number by 1, then copy that file into the working_directory
    #published_directory = Path(published_directory)
    publish_dir = os.path.dirname(published_file_path)
    full_filename = os.path.basename(published_file_path).split(".")[0]
    base_name, extension = os.path.splitext(full_filename)
    clean_basename = re.split(r'_v\d{3}$', base_name)[0]
    #extension = extension.lstrip(".")
    print("This is the published file information: ")
    print(f"Full file name: {full_filename}")
    print(f"Extension: {extension}")
    print(f"base_name: {base_name}")
    _, new_filename = get_unique_filename(clean_basename, publish_dir, extension)

    source_file = published_file_path
    destination_path = os.path.join(working_directory, new_filename)
    
    print(f"Creating working file: {destination_path} from publish: {source_file} ")

    #if new_path:
    #    print(f"Creating working file:{new_filename} at {new_path}")

def open_file_location(file_path):
    if os.path.exists(file_path):
        folder_path = os.path.dirname(file_path)
        os.startfile(folder_path)
    else:
        print(f"File does not exist: {file_path}")


def get_unique_filename(base_name, directory, extension=""):
    """Generate a unique filename with an incremental version number."""
    if not os.path.exists(directory):
        print(f"Error: Export directory '{directory}' does not exist.")
        return None, None
    extension = f".{extension}" if extension else ""
    existing_versions = [ 
        int(filename[len(base_name) + 2 : -len(extension)] )
        for filename in os.listdir(directory)
        if filename.startswith(base_name) and filename.endswith(extension)
        and filename[len(base_name) + 2 : -len(extension)].isdigit()
    ]

    version = max(existing_versions, default=0) + 1
    filename = f"{base_name}_v{version:03d}{extension}"
    full_file_path = os.path.join(directory, filename)
    print(f"This is the full file path CHECK NOW!: {full_file_path}")
    return os.path.join(directory, filename), filename

      