"""
Kitsu utilities module for handling Kitsu API interactions and data processing.
"""

from .auth import connect_to_kitsu, load_credentials, clear_credentials
from .kitsu_utils import get_user_projects, get_project_short_name
from .kitsu_utils import get_user_tasks_for_project, get_task_short_name
from .kitsu_utils import get_preview_thumbnail, clean_up_thumbnails
from .kitsu_utils import get_user_avatar
from .context_from_json import get_context_from_json

__all__ = [
    'connect_to_kitsu',
    'load_credentials',
    'clear_credentials',
    'get_user_projects',
    'get_project_short_name',
    'get_user_tasks_for_project',
    'get_task_short_name',
    'get_preview_thumbnail',
    'clean_up_thumbnails',
    'get_user_avatar',	
    'get_context_from_json'
] 