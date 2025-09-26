import os
import sys
import webbrowser
import subprocess
import json
import logging
import pprint
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QCheckBox, QRadioButton, QButtonGroup, QFileDialog, QHBoxLayout, QGroupBox, 
    QFrame, QSpacerItem, QSizePolicy, QComboBox, QTextEdit, QInputDialog, QLineEdit, 
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout, QGridLayout, 
    QMessageBox, QListWidget, QListWidgetItem, QMenu, QToolButton, QSizeGrip
)
from PySide6.QtGui import QIcon, QPixmap, QFont, QColor, QPalette
from PySide6.QtCore import Qt, QSize, QThread, Signal
from kitsu_home_pipeline.utils import (
    get_user_projects,
    get_user_tasks_for_project,
    get_preview_thumbnail,
    clean_up_thumbnails,
    get_user_avatar,
    get_project_short_name,
    get_task_short_name
)
from kitsu_home_pipeline.utils.auth import connect_to_kitsu, kitsu_auto_login, load_credentials, clear_credentials
from kitsu_home_pipeline.utils.file_utils import clean_up_temp_files, create_main_directory, collect_published_files
from kitsu_home_pipeline.UI.publisher.new_gui import run_publisher_gui
from kitsu_home_pipeline.utils.kitsu_utils import get_project_code, get_user_info
from kitsu_home_pipeline.UI.task_manager.log_console import LogConsole

current_dir = os.path.dirname(os.path.abspath(__file__))

# Configure logging
def setup_logging():
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.expanduser("~"), ".kitsu", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(logs_dir, f"task_manager_{timestamp}.log")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # This will also show logs in console
        ]
    )
    
    return logging.getLogger(__name__)

# Initialize logger
logger = setup_logging()

class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kitsu Task Manager")

        icon_path = os.path.join(current_dir, "icons", "KitsuTaskManagerIcon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setGeometry(50, 50, 400, 300)

        # Initialize software detection
        self.software_availability = {}
        #self.detect_installed_software()
        
        # Set the initial directory

#TODO: Fix this, as its not working correctly

        stored_credentials = load_credentials()
        if stored_credentials:
            self.selections = stored_credentials
            if self.auto_login():
                return
            
        self.show_login_screen()

    def apply_stylesheet(self):
         self.setStyleSheet("""             
            QMainWindow {
            background-color: #1f1f1f;
        }

        QLabel {
            color: #f0f0f0;
            font-size: 14px;
        }

        QGroupBox {
            color: #f0f0f0;
            font-size: 16px;
            font-weight: bold;
            border: 1px solid #444;
            border-radius: 8px;
            margin-top: 10px;
        }

        QGroupBox:title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }

        QLineEdit, QTextEdit {
            background-color: #2c2c2c;
            color: #fff;
            border: 1px solid #555;
            padding: 6px;
            border-radius: 4px;
        }

        QPushButton {
            background-color: #007acc;
            color: #ffffff;
            font-weight: bold;
            border-radius: 5px;
            padding: 8px 12px;
        }

        QPushButton:hover {
            background-color: #005fa3;
        }

        QListWidget {
            background-color: #2a2a2a;
            color: white;
            border: 1px solid #444;
        }

        QListWidget::item:selected {
            background-color: #007acc;
            color: white;
        }
        
        QToolButton {
            background-color: #2c2c2c;
            color: #f0f0f0;
            border: 1px solid #444;
            padding: 6px;
            border-radius: 4px;
        }
        QToolButton:hover {
            background-color: #007acc;
        }

        QMenu {
            background-color: #2c2c2c;
            color: #f0f0f0;
            border: 1px solid #444;
            padding: 6px;
            border-radius: 4px;
        }
        QMenu::item:selected {
            background-color: #007acc;
            color: white;
        }
    """)
         
    def show_login_screen(self):
        """Display the login screen."""
        central_widget = QWidget(self)
        self.setGeometry(50, 50, 400, 300)
        self.setCentralWidget(central_widget)

        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        central_widget.setLayout(main_layout)

        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(10)

        # Title label
        self.title_label = QLabel("Task Manager", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        #self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(self.title_label)

        # Log in 
        self.title_label = QLabel("Log in to Kitsu", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)

        self.url_name_label = QLabel("Kitsu URL:", self)
        self.url_name_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.url_name_label)

        self.url_name_input = QLineEdit(self)
        self.url_name_input.setPlaceholderText("Enter your Kitsu URL")
        main_layout.addWidget(self.url_name_input)

        self.user_name_label = QLabel("Username:", self)
        self.user_name_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.user_name_label)

        self.user_name_input = QLineEdit(self)
        self.user_name_input.setPlaceholderText("Enter your username")
        main_layout.addWidget(self.user_name_input)

        self.password_label = QLabel("Password:", self)
        self.password_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.password_label)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        main_layout.addWidget(self.password_input)

        self.input_button = QPushButton("Log in", self)
        self.input_button.clicked.connect(self.start_process)
        main_layout.addWidget(self.input_button)

        self.apply_stylesheet()

    def auto_login(self):
        try:
            #connect_to_kitsu(
            #    self.selections["kitsu_url"],
            #    self.selections["username"],
            #    self.selections["password"]
            #)
            kitsu_auto_login()
            
            self.update_ui_with_kitsu()
            # Set up DCC integrations after successful login
            #self.setup_dcc_integrations()
            return True
        except Exception as e:
            QMessageBox.warning(self, "Auto-Login Failed", f"Auto-login failed: {str(e)}")
            return False

    def get_selections(self):
        self.selections = {
            "kitsu_url": self.url_name_input.text(),
            "username": self.user_name_input.text(),
            "password": self.password_input.text(),
        }
        return self.selections
    
    def start_process(self):
        self.get_selections()

        try:
            connect_to_kitsu(
                self.selections["kitsu_url"],
                self.selections["username"],
                self.selections["password"]
            )
            self.update_ui_with_kitsu()
            # Set up DCC integrations after successful login
            #self.setup_dcc_integrations()
        except Exception as e:
            QMessageBox.warning(self, "Login Failed", f"Login failed: {str(e)}")

    def detect_installed_software(self):
        """Detect installed DCC software."""
        try:
            # Only detect if not already done
            if not self.software_availability:
                self.software_availability = {
                    "Resolve": self.is_software_installed("Resolve.exe"),
                    "Krita": self.is_software_installed("krita.exe"),
                    "Nuke": self.is_software_installed("Nuke.exe"),
                    "Storyboarder": self.is_software_installed("Storyboarder.exe"),
                    "Blender": self.is_software_installed("blender.exe"),
                }
                logger.info(f"Detected software: {self.software_availability}")
            
            return self.software_availability
            
        except Exception as e:
            logger.error(f"Error detecting software: {str(e)}")
            return {}

    def is_software_installed(self, executable_name):
        for path in os.environ["PATH"].split(os.pathsep):
            executable_path = os.path.join(path, executable_name)
            if os.path.exists(os.path.join(path, executable_name)):
                return executable_path
        print(f"{executable_name} not found in PATH. Searching common paths...")

        common_paths = [
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            r"C:\Users\%USERNAME%\AppData\Local\Programs",
        ]
        for base_path in common_paths:
            for root, dirs, files in os.walk(base_path):
                if executable_name in files:
                    executable_path = os.path.join(root, executable_name)
                    print(f"Found {executable_name} in {root}")
                    return executable_path
                if root.count(os.sep) - base_path.count(os.sep) >= 2:
                    del dirs[:]

        print(f"{executable_name} not found in common paths. Skipping...")
        return False

    def logout(self):
        clear_credentials()
        self.selections = {}
        clean_up_temp_files()
        #clean_up_thumbnails()
        QMessageBox.information(self, "Logout", "You have been logged out.")
        
        self.setGeometry(50, 50, 400, 300)
        self.show_login_screen()
    
    def unpack_projects(self):
        project_names, project_dict = get_user_projects()

    def update_ui_with_kitsu(self):

        self.initial_directory_setup(drive_letter='w', root_folder='KitsuProjects')

        # Main Window
        self.setGeometry(100, 100, 1200, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        central_widget.setLayout(main_layout)



        for i in reversed(range(main_layout.count())):
            widget = main_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Header level
        header_level = QHBoxLayout()

        # Left Column (Header level)
        header_left_column = QVBoxLayout()
        header_left_column.setAlignment(Qt.AlignLeft)

        user_info = get_user_info(self.selections["username"])
        user_name = user_info.get("first_name", "") + " " + user_info.get("last_name", "")

        self.header_label = QLabel(f"Welcome: {user_name}", self)
        self.header_label.setAlignment(Qt.AlignLeft)
        self.header_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_left_column.addWidget(self.header_label)

        header_right_column = QVBoxLayout()
        header_right_column.setAlignment(Qt.AlignRight)

        avatar_path = get_user_avatar(self.selections["username"])
        self.username_button = QToolButton(self)

        if avatar_path:
            pixmap = QPixmap(avatar_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.username_button.setIcon(QIcon(pixmap))

        else:
            self.username_button.setIcon(QIcon(r"D:\HecberryStuff\Dev\photo.png"))
        self.username_button.setIconSize(QSize(50, 50))
        #self.username_button.setFixedSize(150, 150)


        menu = QMenu(self)
        menu.addAction(self.selections["username"], self.view_profile)
        #menu.addAction("Settings", self.view_settings)
        menu.addAction("Console logs", self.view_console)
        menu.addAction("Logout", self.logout)

        self.username_button.setMenu(menu)
        self.username_button.setPopupMode(QToolButton.InstantPopup)
        header_right_column.addWidget(self.username_button)

        header_level.addLayout(header_left_column)
        header_level.addStretch()
        #header_level.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Expanding))
        header_level.addLayout(header_right_column)
        #header_level.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Expanding))

        # First level 
        first_level = QHBoxLayout()
        
        # Left Column (First level)
        left_column = QVBoxLayout()

        project_group = QGroupBox("Project")
        project_layout = QVBoxLayout(project_group)


        self.projects_label = QLabel("Kitsu Projects")
        self.projects_label.setAlignment(Qt.AlignCenter)
        project_layout.addWidget(self.projects_label)

        self.projects_list = QListWidget(self)
        self.projects_list.addItems(get_user_projects())
        self.projects_list.itemClicked.connect(self.on_project_selected)
        project_layout.addWidget(self.projects_list)

        left_column.addWidget(project_group)

        # Right Column (First level)
        right_column = QVBoxLayout()

        entity_group = QGroupBox("Entity")
        entity_layout = QVBoxLayout(entity_group)

        self.entity_label = QLabel("Entity")
        self.entity_label.setAlignment(Qt.AlignCenter)
        entity_layout.addWidget(self.entity_label)

        self.entity_list = QListWidget(self)
        self.entity_list.addItems(["Entities"])
        self.entity_list.itemClicked.connect(self.on_entity_selected)
        entity_layout.addWidget(self.entity_list)

        right_column.addWidget(entity_group)





        # Third Column

        third_column = QVBoxLayout()

        tasks_group = QGroupBox("Tasks")
        tasks_layout = QVBoxLayout(tasks_group)

        self.tasks_label = QLabel("Tasks")
        self.tasks_label.setAlignment(Qt.AlignCenter)
        tasks_layout.addWidget(self.tasks_label)

        self.tasks_list = QListWidget(self)
        self.tasks_list.addItems(["Your tasks"])
        self.tasks_list.itemClicked.connect(self.on_task_selected)
        tasks_layout.addWidget(self.tasks_list)

        third_column.addWidget(tasks_group)

        first_level.addLayout(left_column)
        first_level.addLayout(right_column)
        first_level.addLayout(third_column)

        first_level.setStretch(0, 1)
        first_level.setStretch(1, 1)
        first_level.setStretch(2, 3)


        # Second level
        second_level = QHBoxLayout()

        # Left Column (Second level)
        second_right_column = QVBoxLayout()

        versions_group = QGroupBox("Versions")
        versions_layout = QVBoxLayout(versions_group)

        self.versions_label = QLabel("Versions")
        self.versions_label.setAlignment(Qt.AlignCenter)
        versions_layout.addWidget(self.versions_label)

        self.versions_list = QListWidget(self)
        self.versions_list.addItems(["Versions"])
        self.versions_list.itemClicked.connect(self.on_version_selected)
        versions_layout.addWidget(self.versions_list)

        second_right_column.addWidget(versions_group)

        second_level.addLayout(second_right_column)



        main_layout.addLayout(header_level)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_layout.addLayout(first_level)
        main_layout.addLayout(second_level)
        
        self.apply_stylesheet()
        #self.detect_installed_software()

    def view_profile(self):
        try:
            kitsu_url = self.selections.get("kitsu_url", "").rstrip("/api")
            my_tasks_url = f"{kitsu_url}/my-tasks"

            #print(my_tasks_url)
            webbrowser.open(my_tasks_url)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open profile: {str(e)}")
            return

    def view_settings(self):
        QMessageBox.information(self, "Settings", "Opening settings...")
    
    def view_console(self):
        if not hasattr(self, "log_console") or self.log_console is None:
            self.log_console = LogConsole()
            self.log_console.show()
            self.log_console.raise_()
            self.log_console.activateWindow()

    def add_task_to_list(self, task_type_name, due_date, status, entity_name, id, project_code, task_code, entity_type_name, project_id, task_type_for_entity, sequence):
        # Create a custom widget for the task
        task_widget = QWidget()
        task_layout = QHBoxLayout(task_widget)


        # Add task details (name and date)
        text_layout_right = QVBoxLayout()
        text_layout_left = QVBoxLayout()

        thumbnail_path = get_preview_thumbnail(id)
        task_preview_icon_button = QToolButton(self)
        if thumbnail_path:
            pixmap = QPixmap(thumbnail_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            task_preview_icon_button.setIcon(QIcon(pixmap))
        else:
            task_preview_icon_button.setIcon(QIcon(r"D:\HecberryStuff\Dev\photo.png"))
        
        task_preview_icon_button.setIconSize(QSize(100, 100))
        task_preview_icon_button.setFixedSize(100, 100)

        task_entity_name_label = QLabel(entity_name)
        task_entity_name_label.setStyleSheet("font-weight: bold;")
        task_name_label = QLabel(task_type_name)
        task_name_label.setStyleSheet("font-weight: bold;")
        task_date_label = QLabel(due_date)
        task_date_label.setStyleSheet("font-size: 12px;")
        task_status_title_label = QLabel("Status:")
        task_status_title_label.setStyleSheet("font-weight: bold;")
        task_status_label = QLabel(status)
        task_status_label.setStyleSheet("font-size: 12px;")
        text_layout_left.addWidget(task_preview_icon_button)
        text_layout_right.addWidget(task_entity_name_label)
        text_layout_right.addWidget(task_name_label)
        text_layout_right.addWidget(task_date_label)
        text_layout_right.addWidget(task_status_title_label)
        text_layout_right.addWidget(task_status_label)

        task_layout.addLayout(text_layout_left)
        task_layout.addLayout(text_layout_right)

        # Add the custom widget to the QListWidget
        task_item = QListWidgetItem(self.tasks_list)
        task_item.setSizeHint(task_widget.sizeHint())
        self.tasks_list.addItem(task_item)
        self.tasks_list.setItemWidget(task_item, task_widget)

        task_item.setData(Qt.UserRole, {
            "project_name": self.projects_list.currentItem().text(),
            "task_type_name": task_type_name,
            "due_date": due_date,
            "status": status,
            "entity_name": entity_name,
            "task_id": id,
            "project_code": get_project_short_name(self.projects_list.currentItem().text()),
            "task_code": get_task_short_name(id),
            "entity_type_name": entity_type_name,
            "project_id": project_id,
            "task_type_for_entity": task_type_for_entity,
            "sequence": sequence
        })

        
    


    def on_project_selected(self, item):
        selected_project = item.text()
        entities, self.task_details, entities_type = get_user_tasks_for_project(self.selections["username"], selected_project)
        entity_type_and_name = []
        for i in range(len(entities)):
            entity_type_and_name.append(f"{entities[i]} ({entities_type[i]})")
        self.entity_list.clear()
        self.tasks_list.clear()
        #print("This is the task_details: ")
        #pprint.pprint(self.task_details)

        
        self.entity_list.addItems(entity_type_and_name)



    def on_entity_selected(self, item):
        selected_entity = item.text().split(" (")[0]
        selected_entity_type = item.text().split("(")[1]
        #selected_entity = selected_entity.split(" (")[0]
        # Do something with the selected entity
        print(f"Selected entity: {selected_entity}")

        filtered_tasks = [
            task for task in self.task_details if task["entity_name"] == selected_entity

        ]

        self.tasks_list.clear()

        for task in filtered_tasks:
            task_name = task["task_type_name"]
            task_code = task["task_code"]
            project_code = task["project_code"]
            due_date = task["due_date"]
            status = task["status"]
            id = task["task_id"]
            entity_type_name = task["entity_type_name"]
            project_id = task["project_id"]
            task_type_for_entity = task["task_type_for_entity"]
            sequence = task["sequence"]
            self.add_task_to_list(task_name, due_date, status, selected_entity, id, project_code, task_code, entity_type_name, project_id, task_type_for_entity, sequence)
    
    def on_task_selected(self):
        selected_task = self.get_selected_task()
        if selected_task:
            context = self.save_task_context(selected_task)
            path = os.path.join(self.root_directory, context["project_code"], "Publish", context["task_type_for_entity"], context["entity_name"], context["task_code"])
            print("THIS IS THE PATH where we will look for published files")
            print(path)
            self.published_files = collect_published_files(path)
    
            self.versions_list.clear()
            self.published_files_dict = {}
            
            if self.published_files:

                for file in self.published_files:
                    self.versions_list.addItem(file)
                    #self.versions_list.addItem(os.path.basename(file))
            else:
                self.versions_list.addItem("No published files found.")


    def get_selected_task(self):
        selected_item = self.tasks_list.currentItem()
        print(f"Selected item: {selected_item.text()}")
        if not selected_item:
            QMessageBox.warning(self, "No Task Selected", "Please select a task to view details.")
            return None
        
        task_data = selected_item.data(Qt.UserRole)
        if task_data:
            print("Task data: ")
            pprint.pprint(task_data)
            return task_data
        
        QMessageBox.warning(self, " Task Not Found", "The selected task could not be found.")
        return None
        #if selected_item:
        #    print(f"Selected item text: {selected_item.text()}")

            #print(f"Selected task: {task_name}")
        #    for task in self.task_details:
        #        if task["task_type_name"] == task_name:
        #            return task
        #QMessageBox.warning(self, "No Task Selected", "Please select a task to view details.")
        #return None
    #TODO: An asset is type ASSET, entity type name is a different thing, need to adjust to take this into consideration
    def save_task_context(self, task):
        context = {
            "project_name": self.projects_list.currentItem().text(),
            "task_id": task["task_id"],
            "task_name": task["task_type_name"],
            "due_date": task["due_date"],
            "status": task["status"],
            "entity_name": task["entity_name"],
            "project_code": task["project_code"],
            "task_code": task["task_code"],
            "entity_type": task["entity_type_name"],
            "project_id": task["project_id"],
            "task_type_for_entity": task["task_type_for_entity"],
            "sequence": task["sequence"]
        }
        return context
    
    def contextMenuEvent(self, event):
        if self.tasks_list.underMouse():
            menu = QMenu(self)

            action_publish = menu.addAction("Publish")
            action_publish.setIcon(QIcon(os.path.join(current_dir, "icons", "KitsuPublisherIcon.ico")))

            action_view_details = menu.addAction("View Details")

            action_launch_software = menu.addMenu("Launch Software")
            action_launch_software.setIcon(QIcon(os.path.join(current_dir, "icons", "PhotoIcon.ico")))
            
            action_launch_resolve = None
            action_launch_krita = None
            action_launch_nuke = None
            action_launch_storyboarder = None
            action_launch_blender = None

            if self.software_availability.get("Storyboarder"):
                action_launch_storyboarder = action_launch_software.addAction("Launch Storyboarder")
                action_launch_storyboarder.setIcon(QIcon(os.path.join(current_dir, "icons", "StoryborderLogo.ico")))

            if self.software_availability.get("Krita"):
                action_launch_krita = action_launch_software.addAction("Launch Krita")
                action_launch_krita.setIcon(QIcon(os.path.join(current_dir, "icons", "kritaicon.ico")))

            if self.software_availability.get("Resolve"):
                action_launch_resolve = action_launch_software.addAction("Launch Resolve")
                action_launch_resolve.setIcon(QIcon(os.path.join(current_dir, "icons", "DaVinci_Resolve_Icon.ico")))
            
            if self.software_availability.get("Blender"):
                action_launch_blender = action_launch_software.addAction("Launch Blender")
                action_launch_blender.setIcon(QIcon(os.path.join(current_dir, "icons", "Blender_Logo.ico")))

            if self.software_availability.get("Nuke"):
                action_launch_nuke = action_launch_software.addAction("Launch Nuke")
                action_launch_nuke.setIcon(QIcon(os.path.join(current_dir, "icons", "NukeIcon.ico")))
                action_launch_nuke.setEnabled(True)
            action_launch_software.addSeparator()

            #action_launch_resolve.setEnabled(self.software_availability.get("Resolve") is not None)
            #action_launch_krita.setEnabled(self.software_availability.get("Krita") is not None)
            #action_launch_nuke.setEnabled(self.software_availability.get("Nuke") is not None)

            action = menu.exec(self.mapToGlobal(event.pos()))

            if action is None:
                return

            if action == action_view_details:
                self.view_task_details()

            elif action == action_publish:
                from kitsu_home_pipeline.UI.publisher.new_gui import AgnosticPublisher
                from kitsu_home_pipeline.utils.file_utils import create_context_file, create_entity_directory
                print("Creating context file for selected task")
                selected_task = self.get_selected_task()
                if selected_task:
                    context = self.save_task_context(selected_task)
                    create_context_file(context)
                    publish_path, working_path = create_entity_directory(self.root_directory, 
                                             context["project_code"], 
                                             context["task_type_for_entity"], 
                                             context["task_code"],
                                             context["entity_name"]
                                            )

                print("Launching Publisher")
                self.publisher_window = AgnosticPublisher()
                self.publisher_window.show()

            elif action == action_launch_resolve:
                from kitsu_home_pipeline.task_manager.software_utils import launch_resolve
                selected_task = self.get_selected_task()
                if selected_task:
                    self.save_task_context(selected_task)
                    launch_resolve(self.software_availability["Resolve"], selected_task)

            elif action == action_launch_krita:
                from kitsu_home_pipeline.integrations.krita import KritaIntegration
                krita_integration = KritaIntegration()
                selected_task = self.get_selected_task()
                if selected_task:
                    self.save_task_context(selected_task)
                    krita_integration.launch(self.software_availability["Krita"], selected_task)
            
            elif action == action_launch_storyboarder:
                from kitsu_home_pipeline.task_manager.software_utils import launch_storyboarder
                selected_task = self.get_selected_task()
                if selected_task:
                    self.save_task_context(selected_task)
                    launch_storyboarder(self.software_availability["Storyboarder"], selected_task)
                    
            elif action == action_launch_nuke:
                from kitsu_home_pipeline.task_manager.software_utils import launch_nuke
                selected_task = self.get_selected_task()
                if selected_task:
                    self.save_task_context(selected_task)
                    launch_nuke(self.software_availability["Nuke"], selected_task)
            elif action == action_launch_blender:
                from kitsu_home_pipeline.task_manager.software_utils import launch_blender
                selected_task = self.get_selected_task()
                if selected_task:
                    self.save_task_context(selected_task)
                    launch_blender(self.software_availability["Blender"], selected_task)

        elif self.versions_list.underMouse():
            menu = QMenu(self)
            action_open_directory = menu.addAction("File location")

            action = menu.exec(self.mapToGlobal(event.pos()))
            if action:
                print(self.versions_list.currentItem())
            

            if action == action_open_directory:
                from kitsu_home_pipeline.utils.file_utils import open_file_location
                print("Opening file location...")
                selected_version = self.versions_list.currentItem()
                file_path = self.published_files.get(selected_version.text())
                if file_path:
                    open_file_location(file_path)
    def on_version_selected(self, item):
        print(f"Selected version: {item.text()}")
        file_name = item.text()
        file_path = self.published_files.get(file_name)
        if file_path:
            print(f"Full file path: {file_path}")
        else:
            print("File not found in path")

        for file in self.published_files:
            if item.text() == file:
                print(f"Full file path: {file}")

    def view_task_details(self):
        selected_items = self.tasks_list.currentItem()
        if selected_items:
            selected_task = selected_items[0].text()
            QMessageBox.information(self, "Task Details", f"Details for task: {selected_task}")
    
    def closeEvent(self, event):
        if hasattr(self, "publisher_window") and self.publisher_window is not None:
            self.publisher_window.close()
        event.accept()

    
    #def setup_dcc_integrations(self):
    #    """Setup DCC software integrations."""
    #    try:
    #        # Use already detected software instead of detecting again
    #        logger.info(f"Using detected software: {self.software_availability}")
#
    #        # Setup Resolve integration if available
    #        if self.software_availability.get("Resolve"):
    #            logger.info("Setting up Resolve integration")
    #            from kitsu_home_pipeline.integrations.resolve.setup_utils import setup_resolve_integration, ResolveSetup
    #            
    #            # Get the source scripts directory
    #            source_scripts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "integrations", "resolve", "scripts")
    #            logger.info(f"Source scripts directory: {source_scripts_dir}")
    #            
    #            # Setup integration (this will also set up environment variables)
    #            setup = ResolveSetup()
    #            success = setup.setup_integration(source_scripts_dir)
    #            
    #            if success:
    #                # Verify the environment
    #                verification = setup.verify_environment()
    #                
    #                if verification["success"]:
    #                    logger.info("Resolve integration has been set up successfully!")
    #                    logger.info("Environment variables have been configured.")
    #                    QMessageBox.information(self, "Setup Complete", 
    #                        "Resolve integration has been set up successfully!\n"
    #                        "The Kitsu publisher script has been installed in the Resolve Fusion Scripts directory.")
    #                else:
    #                    # Create setup instructions
    #                    setup._create_setup_instructions()
    #                    
    #                    # Show verification results only if there are issues
    #                    missing_vars = "\n".join(f"- {var}" for var in verification["missing_vars"])
    #                    msg = QMessageBox()
    #                    msg.setIcon(QMessageBox.Warning)
    #                    msg.setWindowTitle("Setup Verification")
    #                    msg.setText("Some environment variables could not be set automatically.")
    #                    msg.setInformativeText(f"Missing or invalid variables:\n{missing_vars}\n\n"
    #                                         f"Please check the setup instructions at:\n{verification['instructions_file']}")
    #                    msg.setStandardButtons(QMessageBox.Ok)
    #                    msg.exec_()
    #            else:
    #                QMessageBox.critical(self, "Setup Error", 
    #                    "Failed to set up Resolve integration.\n"
    #                    "Please check the logs for more details.")
#
    #    except Exception as e:
    #        logger.error(f"Error setting up DCC integrations: {str(e)}")
    #        QMessageBox.critical(self, "Setup Error", 
    #            f"Error setting up DCC integrations: {str(e)}\n\n"
    #            "Please check the logs for more details.")
            
    #def network_drive_detected(self, drive_letter):
    #    drive_path = f"{drive_letter.upper()}:\\"
    #    print(f"Checking for drive: {drive_path}")
    #    if os.path.exists(drive_path):
    #        print(f"Network drive {drive_letter} detected")
    #        return drive_path
    #    else:
    #        print(f"Network drive {drive_letter} not detected.")
    #        return None

    def initial_directory_setup(self, drive_letter, root_folder):
        from kitsu_home_pipeline.utils.file_utils import network_drive_detected
        project_codes_dict = get_project_code()
        pprint.pprint(project_codes_dict)
        project_codes = list(project_codes_dict.values())
        network_drive = network_drive_detected(drive_letter)
        if network_drive and all(project_codes):
            create_main_directory(network_drive, root_folder, project_codes)
            self.root_directory = os.path.join(network_drive, root_folder)
        else:
            self.root_directory = None
            QMessageBox.warning(self, "Directory Setup Failed", "Network drive or project codes not found. Please check your configuration.")


#def setup_dcc_integration(software_name):
#    """
#    Set up integration for a specific DCC software.
#    
#    Args:
#        software_name (str): Name of the DCC software (e.g., 'resolve', 'krita')
#    """
#    try:
#        if software_name.lower() == 'resolve':
#            from kitsu_home_pipeline.integrations.resolve.setup_utils import setup_resolve_integration
#            source_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'integrations', 'resolve')
#            if setup_resolve_integration(source_dir):
#                logger.info("Successfully set up Resolve integration")
#            else:
#                logger.error("Failed to set up Resolve integration")
#        # Add other DCC software integrations here
#        # elif software_name.lower() == 'krita':
#        #     ...
#    except Exception as e:
#        logger.error(f"Error setting up {software_name} integration: {e}")

def on_login_success(self):
    """
    Handle post-login tasks, including DCC software integration setup.
    """
    print("Login succesful!")
    # Detect installed DCC software
    #installed_software = self.detect_installed_software()  # You'll need to implement this
    
    # Set up integration for each detected software
    #for software in installed_software:
    #    print(f"Setting up integration for {software}...")
    #    setup_dcc_integration(software)

def run_gui():
    print("Welcome to the most amazing task manager ever!")
    print("............")
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(current_dir, "icons", "KitsuIcon.ico")))
    app.setFont(QFont("Segoe UI", 10))
    window = TaskManager()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_gui()