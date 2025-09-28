# THIS IS A WORK IN PROGRESS

# Kitsu Home Pipeline Tools

A homemade pipeline, basic tools you need to keep your digital assets in order and tracked. 
Using Kitsu as the main database and project tracking tool, this toolkit gives the user a friendly interface to view, launch and publish his/her tasks. 

## Installation

### Development Installation
```bash
git clone https://github.com/yourusername/KitsuHomeStudioTools.git
cd KitsuHomeStudioTools
pip install -e .
```

### Regular Installation
```bash
pip install git+https://github.com/yourusername/KitsuHomeStudioTools.git
```

## Usage

### Command Line
After installation, you can run the task manager using:
```bash
kitsu-task-manager
```

### Python Import
```python
from kitsu_home_pipeline.UI.task_manager.gui import run_gui

# Run the GUI
run_gui()
```

## Requirements
- Python 3.8 or higher
- PySide6
- requests
- python-dotenv

## License
MIT License 