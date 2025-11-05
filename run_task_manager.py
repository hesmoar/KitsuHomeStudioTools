#!/usr/bin/env python
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import the run_gui function from the correct module
from kitsu_home_pipeline.utils import config
from kitsu_home_pipeline.UI.task_manager.gui import run_gui
from kitsu_home_pipeline.UI.setup.gui import run_gui_configuration_setup
import run_setup

def main():
    app_config = config.load_config()

    setup_complete = False

    if not app_config.get("StudioFolder"):
        print("Configuration missing. Starting setup...")
        #setup_complete = run_setup.run_configuration_setup()
        setup_complete = run_gui_configuration_setup()
    
    else: 
        print("Configuration found.")
        setup_complete = True

    if setup_complete: 
        print("Starting task manager...")
        run_gui()

    else: 
        print("Setup was not completed. Exiting application.")
        sys.exit(1)


if __name__ == "__main__":
    main() 