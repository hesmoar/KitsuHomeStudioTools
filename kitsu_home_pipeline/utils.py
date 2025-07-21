import os
import json
import logging

logger = logging.getLogger(__name__)

def get_user_projects(username):
    """Get user's active projects from Kitsu."""
    try:
        # Create context directory if it doesn't exist
        context_dir = os.path.join(os.environ.get('TEMP', os.path.expanduser('~')), 'KitsuTaskManager', 'Context')
        os.makedirs(context_dir, exist_ok=True)
        
        context_file = os.path.join(context_dir, 'Kitsu_task_context.json')
        
        # Initialize empty context if file doesn't exist
        if not os.path.exists(context_file):
            context = {
                'projects': [],
                'last_update': None
            }
            with open(context_file, 'w') as f:
                json.dump(context, f)
            return []
            
        # Read existing context
        with open(context_file, 'r') as f:
            context = json.load(f)
            
        return context.get('projects', [])
        
    except Exception as e:
        logger.error(f"Error reading JSON file: {str(e)}")
        return [] 