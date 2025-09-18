import gazu
import pprint
import os
import tempfile
import shutil
import json
from kitsu_home_pipeline.utils.context_from_json import get_context_from_json 


def get_user_projects():
    project_names = []
    projects ={}
    user_active_projects = gazu.user.all_open_projects()
    #print("User active projects: ")
    #pprint.pprint(user_active_projects)
    for project in user_active_projects:
        #print(f"Project Name: {project["name"]}")
        #print(f"Project ID: {project["id"]}")
        project_names.append(project["name"])
        projects[project["name"]] = project["id"]
    #pprint.pprint(projects)
    return project_names

def get_project_code():
    projects = get_user_projects()
    project_codes = {}
    for project in projects:
        project_info = gazu.project.get_project_by_name(project)
        if project_info:
            project_codes[project] = project_info.get("code", "")
    return project_codes

def get_project_info(project_name=None):
    if not project_name:
        print("No project name provided)")
        return None
    else:
        project_info = gazu.project.get_project_by_name(project_name)
        if project_info:
            pprint.pprint(project_info)
            return project_info
        else:
            print(f"Project {project_name} not found.")
            return None

def get_project_short_name(project):
    project_dict = gazu.project.get_project_by_name(project)

    project_shortname = project_dict.get("code")

    return project_shortname

def project_context(file_path):
    project = get_context_from_json(file_path)
    project_name = project.get("project_name")
    print(f"Project name that comes from the context json: {project_name}")
    kitsu_auto_login()
    project_dict = gazu.project.get_project_by_name(project_name)
    if project_dict:
        project_id = project_dict.get("id")
        print(f"Project ID: {project_id}")
        return project_id, project_name
        #pprint.pprint(project_dict)

def get_task_short_name(task_id):
    task_dict = gazu.task.get_task(task_id)

    task_short_name = task_dict["task_type"].get("short_name")

    return task_short_name


def get_user_tasks_for_project(user_email, project_name):
    person = gazu.person.get_person_by_email(user_email)
    tasks = gazu.task.all_tasks_for_person(person)
    entity_names = []
    entity_types = []
    task_details = []
# This is where we first get the info for the task context.
    for task in tasks:
        if task["project_name"] == project_name:
            #print("This is a task")
            #pprint.pprint(task)
            if task["entity_name"] not in entity_names:
                entity_names.append(task["entity_name"])
                entity_types.append(task["entity_type_name"])
                #print(f"Entity Name: {task["entity_name"]}")
            task_details.append({
                "entity_name": task["entity_name"],
                "task_type_name": task["task_type_name"],
                "due_date": task["due_date"],
                "status": task["task_status_short_name"],
                "entity_type_name": task["entity_type_name"],
                "task_id": task["id"],
                "task_code": get_task_short_name(task["id"]),
                "project_code": get_project_short_name(task["project_name"]),
                "project_id": task["project_id"],
                "task_type_for_entity": task["task_type_for_entity"],
                "sequence": task.get("sequence_name", "")
            })


    return entity_names, task_details, entity_types


def get_preview_thumbnail(task_id):
    try:
        temp_dir = os.path.join(tempfile.gettempdir(), r"KitsuTaskManager\Thumbnails")
        os.makedirs(temp_dir, exist_ok=True)

        preview_files = gazu.files.get_all_preview_files_for_task(task_id)
        if preview_files:
            preview_thumbnail_path = os.path.join(temp_dir, f"{task_id}")#_preview.png")
            gazu.files.download_preview_file_cover(preview_files[0]["id"], preview_thumbnail_path)
            return preview_thumbnail_path
        else:
            print(f"No preview files found for task ID: {task_id}")
            return None
    except Exception as e:
        print(f"Error getting preview thumbnail for task ID {task_id}: {e}")
        return None

def get_user_avatar(user_email):
    try:
        temp_dir = os.path.join(tempfile.gettempdir(), r"KitsuTaskManager\Thumbnails")
        os.makedirs(temp_dir, exist_ok=True)
        person = gazu.person.get_person_by_email(user_email)
        if person:
            person_avatar_path = os.path.join(temp_dir, f"{person["first_name"]}")
            gazu.files.download_person_avatar(person, person_avatar_path)
            return person_avatar_path
        else:
            print(f"No person found with email: {user_email}")
            return None
    except Exception as e:
        print(f"Error getting user avatar for email {user_email}: {e}")
        return None


def clean_up_thumbnails():
    temp_dir = os.path.join(tempfile.gettempdir(), "KitsuTaskManagerThumbnails")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


# Project file tree structure --------------------------------------------------

def update_file_tree(json_file, project_id):
    #json_file_tree = r"P:\pipeline\file_tree_test.json"
    #project_id = "eee1775d-015b-4876-92ac-27f781d3b763"
    try:
        with open(json_file, 'r') as file:
            file_tree = json.load(file)
            pprint.pprint(file_tree)

        project_File_tree = gazu.files.update_project_file_tree(project_id, file_tree)

        pprint.pprint(project_File_tree)
    
    except Exception as e:
        print(f"Error loading the json file {e}")


def get_file_tree(project_name):
    project_dict = get_project_info(project_name)
    if project_dict:
        prj_file_tree = project_dict.get("file_tree")
        if prj_file_tree:
            print("This is the projects file tree: ")
            pprint.pprint(prj_file_tree)
            return prj_file_tree
        else:
            print("This project does not have a file tree")
    else:
        print("Project not found")

#TODO: Status should not use the short name, maybe also give the option for the user to change it
def get_review_status():
    project_statuses = gazu.task.all_task_statuses()
    for status in project_statuses:
        if status.get("short_name") == 'wfa':
            pending_status = status

    return pending_status


#TODO: Add functions to create working files and output files as well as preview file.
def create_working_file(task_context, software, comment, person, path):
    """print("Creating a working file! YAY")

    print("These are the values for the working file: ")
    print("this is the task")
    pprint.pprint(task_context)

    print("This is the software: ")
    pprint.pprint(software)

    print("this is the comment: ")
    print(comment)
    print("This is the author: ")
    pprint.pprint(person)

    print("🔍 Checking template substitutions:")
    print("Project short name:", task_context["project"]["code"])
    print("Task type short name:", task_context["task_type"]["short_name"])
    print("Entity name:", task_context["entity"]["name"])
    print("Sequence name:", task_context["sequence"]["name"])
"""
    
    publish_working_file = gazu.files.new_working_file(
        task=task_context,
        name='main',
        mode='working',
        software=software,
        comment=comment,
        person=person,
        revision=0,
        sep='/',
    )

    print("This is the working file created: ")
    pprint.pprint(publish_working_file)

def working_file_path(task_context, software):

    working_file_path = gazu.files.build_working_file_path(
        task=task_context,
        name="main",
        mode="working",
        software=software,
        revision=1,
        sep="/"
    )
    print("This is the generated path for working file: ")
    print(working_file_path)

#def output_file_path(entity):
#    output_file_path = gazu.files.build_entity_output_file_path(
#        entity,
#        output_type=,
#        task_type=,
#        name="main",
#        mode="output",
#        representation="",
#        revision=0,
#        nb_elements=1,
#        sep="/"
#    )

def create_output_file():
    print("Creating an output file YAY YAY!")

def create_preview_file(task_context, person, comment, file_path):
    print("Creating a preview file YAY YAY YAY")
    pnd_status = get_review_status()

    #print("These are the values for the preview file: ")
    #print("this is the task")
    #pprint.pprint(task_context)
    #print("This is the status: ")
    #pprint.pprint(pnd_status)
    #print("this is the comment: ")
    #print(comment)
    #print("This is the author: ")
    #pprint.pprint(person)
    #print("This is the file: ")
    #print(file_path)

    publish_preview = gazu.task.publish_preview(
        task=task_context,
        task_status=pnd_status,
        comment=comment,
        person=person,
        preview_file_path=file_path,
        set_thumbnail=True

    )
    print("This is the preview published and its data: ")
    pprint.pprint(publish_preview)

def publish_new_version():
    """This function should call all 3 previous functions, publishing the working file,
    output file and preview file into kitsu."""
    pass


"""
entity_name - Group by this second
entity_type_name - Group by this first
project_name - Filter by this first

For the context needed from the task manager we need the following info: 

- User ID
- Project ID
- Task ID
- Asset ID
- Shot ID

"""

if __name__ == "__main__":
    create_preview_file()
