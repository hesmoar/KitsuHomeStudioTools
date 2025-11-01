from kitsu_home_pipeline.utils.auth import kitsu_auto_login
from kitsu_home_pipeline.utils.kitsu_utils import get_file_tree, update_file_tree, get_project_info
from kitsu_home_pipeline.utils.file_utils import generate_paths, current_context_path

#project_name = "AnimaOrquesta_Test"
#project_name = "Animagedon"
project_name = "epic"
json_file = r"C:\Users\Usuario\Documents\Dev\KitsuHomeStudioTools\kitsu_home_pipeline\UI\publisher\file_tree.json"

#print(f"Using JSON file: {json_file}")

kitsu_auto_login()

project = get_project_info(project_name)

update_file_tree(json_file, project.get("id"))

#print("This is the projects new file tree: TADA!!!! ")
#get_file_tree(project_name)
#current_context_path()