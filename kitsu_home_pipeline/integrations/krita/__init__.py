import os
import subprocess
import tempfile
import json
import shutil
from pathlib import Path

class KritaIntegration:
    def __init__(self):
        self.plugin_folder = os.path.join(os.path.dirname(__file__), "kitsu_create_doc")
    
    def launch(self, software_path, task_context):
        """Copy plugin to Krita's plugin directory and launch Krita"""
        try:
            # Copy the plugin folder to Krita's plugin directory
            plugin_dir = os.path.join(os.environ['APPDATA'], 'krita', 'pykrita', 'kitsu_create_doc')
            if os.path.exists(plugin_dir):
                shutil.rmtree(plugin_dir)
            shutil.copytree(self.plugin_folder, plugin_dir)

            # Save task context (optional, for future use)
            self._save_task_context(task_context)

            # Launch Krita
            subprocess.Popen([
                software_path,
                "--nosplash"
            ])
            return True
        except Exception as e:
            print(f"Error launching Krita: {str(e)}")
            return False
#TODO: Context should be saved in the same file when launching the software, currently we are creating 2 different files.
    def _save_task_context(self, task_context):
        """Save task context to a temporary file"""
        try:
            temp_dir = os.path.join(tempfile.gettempdir(), "KitsuTaskManager", "Context")
            os.makedirs(temp_dir, exist_ok=True)
            context_file = os.path.join(temp_dir, "krita_task_context.json")
            with open(context_file, 'w') as f:
                json.dump(task_context, f, indent=4)
        except Exception as e:
            print(f"Error saving task context: {str(e)}")
    
    def get_version(self):
        """Get Krita version"""
        try:
            result = subprocess.run([software_path, '--version'], 
                                 capture_output=True, 
                                 text=True)
            return result.stdout.strip()
        except:
            return "Unknown"
    
    def is_installed(self):
        """Check if Krita is installed"""
        try:
            subprocess.run([software_path, '--version'], 
                         capture_output=True, 
                         check=True)
            return True
        except:
            return False 