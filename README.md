# Kitsu Home Pipeline Tools

Kitsu Home Pipeline Tools is a small, home-grown pipeline toolkit that integrates with Kitsu for project tracking
and provides a GUI (Task Manager + Publisher) to browse tasks, create project folders and publish files.

This README gives a practical overview of how the project is structured and how to run the tools locally.

## Main Features
- Task Manager UI to view user assignments based on database (currently Kitsu)
- Publisher to upload previews into kitsu and working files into a desired location
- File management that takes care of structure and naming convention based on database info

## Quick start (development)

1. Create a virtual environment and activate it (Windows example):

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt   # or install packages below
```

2. Install the package in editable/development mode:

```powershell
pip install -e .
```

3. Run the Task Manager GUI directly from source:

```powershell
python run_task_manager.py
```

Or import and call the entry point in Python:

```python
from kitsu_home_pipeline.UI.task_manager.gui import run_gui
run_gui()
```

## Requirements
- Python 3.10+ (3.12 tested in the dev environment)
- PySide6 (Qt bindings used for the GUI)
- gazu (Kitsu API client)
- fileseq (optional, for image sequence detection)
- ffmpeg (optional, for sequence->video conversion) and the project's `ffmpeg_utils` wrapper

If you rely on image-sequence handling or ffmpeg conversion, install `fileseq` and ensure ffmpeg is available in PATH.

## Project layout (high level)

Key folders and modules inside `kitsu_home_pipeline/`:

- `UI/task_manager/` — main Task Manager GUI code (`gui.py`), a small `log_console.py` and icons.
- `UI/publisher/` — Publisher GUI (`new_gui.py`), a gallery widget and publisher helpers.
- `utils/` — pipeline utilities: `file_utils.py` (path creation, file moves), `kitsu_utils.py` (gazu wrappers and project/task helpers), `ffmpeg_utils.py`, `helpers.py`.
- `integrations/resolve/` — Resolve-specific code (integration setup, timeline/render helpers).

Use these modules to trace behavior: `create_entity_directory` in `utils/file_utils.py` builds Publish/Working paths,
and `start_process` in the publisher calls the file move / publish pipeline.

## How the tool works (user flow)

1. Launch the Task Manager and log into your Kitsu instance (the app uses gazu). Login must succeed before Kitsu-based calls are made.
2. Select a project / entity / task from the lists. The GUI maps the selection into a small `context` JSON used by the Publisher.
3. Right‑click a task and choose Publish to open the Publisher GUI. The Publisher collects working/output files (single files and image sequences).
4. When you hit Publish, the Publisher:
	- Calls `create_entity_directory` (or similar) to ensure the Publish and Working directories exist for the selected project/entity/task.
	- If an image sequence is provided, it can be detected (via `fileseq`) and optionally converted to a preview video using ffmpeg (`utils/ffmpeg_utils.py`).
	- Uses `get_unique_filename` to produce a versioned filename (checks local disk and optionally Kitsu records).
	- Moves or copies files into the Publish path and (optionally) registers the result with Kitsu.

## File tree / mount point configuration

Paths are built from a `file_tree.json` template under `UI/publisher/`. The template contains a `mountpoint` that by default points to a network path used in the studio.

Recommended approach for local/dev use:

- Set an environment variable `KITSU_PROJECTS_ROOT` (or edit your local config) to the root path you want the pipeline to use (for example `W:\KitsuProjects` or `D:\KitsuProjects`).
- The path generation code replaces a placeholder in the JSON templates with that value, making the pipeline portable across machines.

## Image sequences

The Publisher supports image sequences via the `fileseq` library. When users add files, the Publisher will group sequence frames into a single `FileSequence` item and handle it as one logical asset. If you need a quick preview video from a sequence, the project includes `utils/ffmpeg_utils.py` where you can call your ffmpeg wrapper to produce an mp4.

Suggested integration point:
- Call the conversion function from `AgnosticPublisher.start_process` when a sequence is detected (after adding files but before publishing).

## Logging and debugging

- The Task Manager provides an integrated log console (`UI/task_manager/log_console.py`) which can capture `stdout`/`stderr` redirected after the console is instantiated. If you want to capture all logs in the GUI, open the console early in the application lifecycle.
- For file-system operations the utilities use `pathlib.Path.mkdir(parents=True, exist_ok=True)` and wrap operations in `try`/`except` to handle errors gracefully.

## Where to add code

- Put Resolve-specific scripts and helpers under `integrations/resolve/` (e.g. `timeline_utils.py`, `render_utils.py`).
- Put generic utilities under `utils/` (file helpers, ffmpeg wrappers, context mapping, Kitsu helpers).

## Tests

There is a `tests/` directory with some small unit tests and integration helpers (gazu configuration fixer etc.). Run them with your preferred test runner.

## Notes

- The GUI expects the Kitsu server URL and credentials to be configured/login performed before calling API-dependent functions (some earlier code tried to call Kitsu while not logged in and will fail to resolve a default placeholder host).
- Use project codes (short names) for folder creation; the `get_project_code` helper returns a mapping used by the directory creation tooling.

---

If you'd like, I can make this README even more specific (example screenshots, command examples for sequence conversion, or an explicit configuration sample). If you want that, tell me which sections to expand.

License: MIT
