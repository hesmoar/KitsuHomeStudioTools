from kitsu_home_pipeline.utils.context_from_json import get_context_from_json
from kitsu_home_pipeline.utils.auth import kitsu_auto_login
import gazu
from kitsu_home_pipeline.utils.file_utils import get_context_file_path
import pprint
import os

context_temp_dir = get_context_file_path()#"KitsuTaskManager/Context")
context_file_path = context_temp_dir

file_path = context_file_path

def project_context():
    project = get_context_from_json(file_path)
    
    project_name = project.get("project_name")
    print(f"Project name that comes from the context json: {project_name}")

    task_id = project.get("task_id")

    kitsu_auto_login()
    """
    new_data = {
        "revision": 15,
    }

    modified_preview_file = gazu.files.update_preview('b140ffc4-6445-40ee-9c4e-431f63cb6a2b', new_data)
    """
    all_task_previews_dict = gazu.files.get_all_preview_files_for_task(task_id)
    task_previews = {}

    print("These are all the previews for this task: ")
    
    print(" ")
    pprint.pprint(all_task_previews_dict)

    for preview_in_task in all_task_previews_dict:
        preview_id = preview_in_task.get("id")
        revision = preview_in_task.get("revision")
        original_name = preview_in_task.get("original_name")

        task_previews [original_name] = {
            "revision": revision,
            "id": preview_id
        }
    
    print("These are the previews and their name, revision and ID")
    pprint.pprint(task_previews)

    working_file_revision = 79 #This one is assuming we know which one is the highest in the pool
    highest_revision = max(task_previews, key=lambda k: task_previews[k]['revision'])

    print("This is the highest revision preview file for this task: ")
    print(highest_revision)

    highest_revision_value = task_previews[highest_revision]['revision']

    if highest_revision_value == working_file_revision:
        print("The working file revision matches the highest preview revision, need to add 1 to both")
        new_working_file_revision = working_file_revision + 1
        new_highest_revision_value = highest_revision_value + 1
        print(f"These are the new values, working file: {new_working_file_revision}, and kitsu revision: {new_highest_revision_value}")
    elif highest_revision_value > working_file_revision:
        print("Highest preview revision is bigger than working file, need to update to working file to match highest revision + 1")
        new_working_file_revision = highest_revision_value + 1
        new_highest_revision_value = highest_revision_value + 1
        print(f"These are the new values, working file: {new_working_file_revision}, and kitsu revision: {new_highest_revision_value}")
    elif highest_revision_value < working_file_revision:
        print("Highest preview revision is smaller than working file, need to update working file to match highest revision + 1 (not sure) ")


"""
    project_dict = gazu.project.get_project_by_name(project_name)
    if project_dict:
        project_id = project_dict.get("id")
        print(f"Project ID: {project_id}")
        project_shots = gazu.shot.all_shots_for_project(project_id)
        if project_shots:
            for shot in project_shots:
                if shot.get("name") == "SH999":
                    shot_id = shot.get("id")
                    print("Shot SH999 found: ")
                    pprint.pprint(shot)
                    shot_previews = gazu.shot.all_previews_for_shot(shot_id)
                    
                    print("These are the preview dictionaries: ")
                    #pprint.pprint(shot_previews)
    preview_file = gazu.files.get_preview_file("d0a1696f-5c30-4d85-8dd6-25edacb6b428")
    task_type = gazu.task.get_task_type('8b3fb00d-5000-4349-8594-999bccea1c6a')
    
    
    task_type_name = gazu.task.get_task_type_by_name("Compositing")
    task_type_id = task_type_name.get("id")

    for shot_preview in shot_previews:
        if shot_preview == task_type_id:
            print("Found the matching task type for previews")
            pprint.pprint(shot_preview)

    
    
    working_files = gazu.files.get_all_working_files_for_entity(shot_id, task=None)
    if working_files:
        print("These are the working files")
    else:
        print("No working files found")
        print(" ")


    print("This is a task_type")
    pprint.pprint(task_type)

    print("This is one preview file")
    pprint.pprint(preview_file)

    new_data = {
        "revision": 15,
    }

    modified_preview_file = gazu.files.update_preview(preview_file, new_data)

    new_modified_preview_file = gazu.files.get_preview_file(modified_preview_file.get("id"))

    print("This is the modified preview file: ")
    pprint.pprint(new_modified_preview_file)
    
"""
project_context()