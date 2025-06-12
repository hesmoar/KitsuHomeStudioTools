#!/usr/bin/env python
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import the run_gui function from the correct module
from kitsu_home_pipeline.task_manager.gui import run_gui

if __name__ == "__main__":
    run_gui() 