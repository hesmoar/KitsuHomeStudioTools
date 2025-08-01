import os
import shutil
import json
import pprint
from .file_utils import get_temp_dir, get_context_file_path

context_file_path = get_context_file_path()

def get_context_from_json(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            context_data = json.load(file)
            #pprint.pprint(context_data)
            return context_data
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None
    
task_context = get_context_from_json(context_file_path)