import gazu
import pprint
import os
import tempfile
import shutil



def get_user_projects():
    project_names = []
    projects ={}
    user_active_projects = gazu.user.all_open_projects()
    print("User active projects: ")
    #pprint.pprint(user_active_projects)
    for project in user_active_projects:
        print(f"Project Name: {project["name"]}")
        print(f"Project ID: {project["id"]}")
        project_names.append(project["name"])
        projects[project["name"]] = project["id"]
    pprint.pprint(projects)
    return project_names

def get_project_short_name(project):
    project_dict = gazu.project.get_project_by_name(project)

    project_shortname = project_dict.get("code")

    return project_shortname

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

    for task in tasks:
        if task["project_name"] == project_name:
            print("This is a task")
            pprint.pprint(task)
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
                "project_code": get_project_short_name(task["project_name"])
            })


    return entity_names, task_details, entity_types
# FIXME: This should get the thumbnail from the task or asset and download it so it can be used in the GUI
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
