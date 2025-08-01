from kitsu_home_pipeline.utils.auth import kitsu_auto_login
from kitsu_home_pipeline.utils.kitsu_utils import get_file_tree, update_file_tree, get_project_info

project_name = "AnimaOrquesta_Test"
json_file = r"C:\Users\Usuario\Documents\Dev\KitsuHomeStudioTools\kitsu_home_pipeline\UI\publisher\file_tree.json"

#print(f"Using JSON file: {json_file}")

kitsu_auto_login()

#project = get_project_info(project_name)

#update_file_tree(json_file, project.get("id"))

get_file_tree("AnimaOrquesta_Test")