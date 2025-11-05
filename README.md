# WORK IN PROGRESS
# Home Pipeline Tools

Home Pipeline Tools is a small, home-grown pipeline toolkit that integrates with Kitsu for project tracking and provides a GUI (Task Manager + Publisher) to browse tasks, create project folders and publish files. Helping you keep everything in order and your database updated and your project going. 

This README gives a practical overview of how the project is structured and how to run the tools locally.

## Main Features
- **Task Manager**: A user interface to view, filter and manage kitsu tasks
- **Publisher**: A user interface to publish working and preview files into Kitsu and your designated storage

## Pre-requisites
- This application assumes you already have a running Kitsu server either self-hosted or hosted by Kitsu.
- This application assumes you already have a File-tree setup on your project in kitsu and relies on it to work properly


## Installation (Recommended Method)

This is the easiest way to get started. You will download a self-contained application that runs without installing or any other dependencies.

1.  Go to the [**Releases Page**](https://github.com/hesmoar/KitsuHomeStudioTools/releases) on this repository.
2.  Download the latest `.zip` file (e.g., `KitsuHomeStudioTools-v1.0.0-windows.zip`).
3.  Unzip the entire folder to a location on your computer.
4.  Follow the **Configuration** steps below.
5.  Run the application by double-clicking the `.exe` file (e.g., `run_task_manager.exe`).

## Usage
- Simply run the main executable (e.g. run_task_manager.exe)
- In the gui insert the url for your Kitsu server
- Using your pre-set user and password hit login

## Development (Running from source)

If you want to run or contribute to the development, you can run the tool from the source code.
### 1. Clone the repository 
```
git clone [https://github.com/hesmoar/KitsuHomeStudioTools.git](https://github.com/hesmoar/KitsuHomeStudioTools.git)
cd KitsuHomeStudioTools
```
### 2. Create Virtual environment
### 3. Activate the virtual environment
### 4. Install dependencies
### 5. Run the application 



## Notes

- The GUI expects the Kitsu server URL and credentials to be configured/login performed before calling API-dependent functions (some earlier code tried to call Kitsu while not logged in and will fail to resolve a default placeholder host).
- Use project codes (short names) for folder creation; the `get_project_code` helper returns a mapping used by the directory creation tooling.

---

## Roadmap
1. [ ] Software integration
	- DaVinci Resolve
	- Blender
2. [ ] Multiple database support
	- Flow (Shotgrid, Shotgun forever!)
	- Ftrack



## License
This project is licensed under the MIT License. See the LICENSE file for details.
