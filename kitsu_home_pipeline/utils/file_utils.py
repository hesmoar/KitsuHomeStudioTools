   # In file_utils.py
import os
import tempfile
from pathlib import Path

def get_temp_dir(subfolder: str = None) -> Path:
       temp_base = Path(tempfile.gettempdir())
       if subfolder:
           temp_path = temp_base / subfolder
           temp_path.mkdir(parents=True, exist_ok=True)
           return temp_path
       return temp_base