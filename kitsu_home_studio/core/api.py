"""
Core API module for Kitsu integration
"""

import os
import requests
import tempfile
from pathlib import Path
from .auth import load_credentials

def get_kitsu_session():
    """Get an authenticated Kitsu session."""
    credentials = load_credentials()
    if not credentials:
        raise Exception("No credentials found. Please log in first.")
    
    session = requests.Session()
    session.post(
        f"{credentials['kitsu_url']}/api/auth/login",
        json={"email": credentials["username"], "password": credentials["password"]}
    )
    return session, credentials["kitsu_url"]

def get_user_projects():
    """Get list of projects for the current user."""
    session, kitsu_url = get_kitsu_session()
    
    # Get user info
    user_response = session.get(f"{kitsu_url}/api/auth/me")
    user_data = user_response.json()
    user_id = user_data["id"]
    
    # Get user's projects
    projects_response = session.get(
        f"{kitsu_url}/api/data/persons/{user_id}/projects"
    )
    projects_data = projects_response.json()
    
    # Extract project names
    project_names = [project["name"] for project in projects_data]
    project_dict = {project["name"]: project for project in projects_data}
    
    return project_names, project_dict

def get_user_tasks_for_project(username, project_name):
    """Get tasks for a specific project and user."""
    session, kitsu_url = get_kitsu_session()
    
    # Get user info
    user_response = session.get(f"{kitsu_url}/api/auth/me")
    user_data = user_response.json()
    user_id = user_data["id"]
    
    # Get project info
    projects_response = session.get(
        f"{kitsu_url}/api/data/persons/{user_id}/projects"
    )
    projects_data = projects_response.json()
    project = next((p for p in projects_data if p["name"] == project_name), None)
    
    if not project:
        raise Exception(f"Project {project_name} not found")
    
    # Get tasks for the project
    tasks_response = session.get(
        f"{kitsu_url}/api/data/projects/{project['id']}/tasks",
        params={"assignee_id": user_id}
    )
    tasks_data = tasks_response.json()
    
    # Extract task details
    entities = []
    task_details = []
    entities_type = []
    
    for task in tasks_data:
        entity = task.get("entity", {})
        entities.append(entity.get("name", "Unknown"))
        entities_type.append(entity.get("type", "Unknown"))
        
        task_details.append({
            "task_id": task["id"],
            "task_type_name": task["task_type_name"],
            "due_date": task.get("due_date", "No due date"),
            "status": task.get("task_status_name", "Unknown"),
            "entity_name": entity.get("name", "Unknown"),
            "project_code": project.get("code", ""),
            "task_code": task.get("code", ""),
            "entity_type_name": entity.get("type", "Unknown")
        })
    
    return entities, task_details, entities_type

def get_preview_thumbnail(task_id):
    """Get preview thumbnail for a task."""
    session, kitsu_url = get_kitsu_session()
    
    # Get preview file
    preview_response = session.get(
        f"{kitsu_url}/api/data/tasks/{task_id}/preview-file"
    )
    preview_data = preview_response.json()
    
    if not preview_data:
        return None
    
    # Download thumbnail
    thumbnail_url = preview_data.get("thumbnail_url")
    if not thumbnail_url:
        return None
    
    # Create temp directory for thumbnails
    temp_dir = os.path.join(tempfile.gettempdir(), "KitsuTaskManager", "thumbnails")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Download and save thumbnail
    thumbnail_path = os.path.join(temp_dir, f"preview_{task_id}.png")
    if not os.path.exists(thumbnail_path):
        thumbnail_response = session.get(thumbnail_url)
        with open(thumbnail_path, "wb") as f:
            f.write(thumbnail_response.content)
    
    return thumbnail_path

def get_user_avatar(username):
    """Get user avatar."""
    session, kitsu_url = get_kitsu_session()
    
    # Get user info
    user_response = session.get(f"{kitsu_url}/api/data/persons", params={"name": username})
    user_data = user_response.json()
    
    if not user_data:
        return None
    
    user = user_data[0]
    avatar_url = user.get("avatar_url")
    
    if not avatar_url:
        return None
    
    # Create temp directory for avatars
    temp_dir = os.path.join(tempfile.gettempdir(), "KitsuTaskManager", "avatars")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Download and save avatar
    avatar_path = os.path.join(temp_dir, f"avatar_{username}.png")
    if not os.path.exists(avatar_path):
        avatar_response = session.get(avatar_url)
        with open(avatar_path, "wb") as f:
            f.write(avatar_response.content)
    
    return avatar_path

def get_project_short_name(project_name):
    """Get short name for a project."""
    _, project_dict = get_user_projects()
    project = project_dict.get(project_name, {})
    return project.get("code", "")

def get_task_short_name(task_id):
    """Get short name for a task."""
    session, kitsu_url = get_kitsu_session()
    task_response = session.get(f"{kitsu_url}/api/data/tasks/{task_id}")
    task_data = task_response.json()
    return task_data.get("code", "") 