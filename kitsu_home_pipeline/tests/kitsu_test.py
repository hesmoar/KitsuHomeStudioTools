#from kitsu_home_pipeline.utils.context_from_json import get_context_from_json
from kitsu_home_pipeline.utils.auth import kitsu_auto_login
import gazu
from kitsu_home_pipeline.utils.file_utils import get_temp_dir
from kitsu_home_pipeline.utils.kitsu_utils import get_project_info, get_project_framerate

import os


kitsu_auto_login()

project = "AnimaOrquesta_Test"

get_project_info(project)

get_project_framerate(project)

"""
context_temp_dir = get_temp_dir("KitsuTaskManager/Context")
context_file_path = os.path.join(context_temp_dir, "Kitsu_task_context.json")

file_path = context_file_path

def project_context():
    project = get_context_from_json(file_path)
    project_name = project.get("project_name")
    print(f"Project name that comes from the context json: {project_name}")
    kitsu_auto_login()
    project_dict = gazu.project.get_project_by_name(project_name)
    if project_dict:
        project_id = project_dict.get("id")
        print(f"Project ID: {project_id}")
        return project_id, project_name
    
#project_context()
        #pprint.pprint(project_dict)

"""