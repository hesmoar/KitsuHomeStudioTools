import os
import sys
import webbrowser
import subprocess
import json
import logging
import pprint
from datetime import datetime

from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QCheckBox, QRadioButton, QButtonGroup, QFileDialog, QHBoxLayout, QGroupBox, 
    QFrame, QSpacerItem, QSizePolicy, QComboBox, QTextEdit, QInputDialog, QLineEdit, 
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout, QGridLayout, 
    QMessageBox, QListWidget, QListWidgetItem, QMenu, QToolButton, QSizeGrip
)
from PySide6.QtGui import QIcon, QPixmap, QFont, QColor, QPalette
from PySide6.QtCore import Qt, QSize, QThread, Signal

# --- INTERNAL IMPORTS ---
from kitsu_home_pipeline.utils.helpers import resource_path
from kitsu_home_pipeline.utils import (
    get_user_projects,
    get_user_tasks_for_project,
    get_preview_thumbnail,
    clean_up_thumbnails,
    get_user_avatar,
    get_project_short_name,
    get_task_short_name
)
# UPDATED AUTH IMPORTS
from kitsu_home_pipeline.utils.auth import (
    connect_to_kitsu, 
    kitsu_auto_login, 
    load_credentials, 
    clear_credentials, 
    login_ui_logic  # Make sure this is exported in auth.py
)
from kitsu_home_pipeline.utils.file_utils import clean_up_temp_files, create_main_directory, collect_published_files
# from kitsu_home_pipeline.UI.publisher.new_gui import run_publisher_gui # Not currently used?
from kitsu_home_pipeline.utils.kitsu_utils import get_project_code, get_user_info
from kitsu_home_pipeline.UI.task_manager.log_console import LogConsole

current_dir = os.path.dirname(os.path.abspath(__file__))

# Configure logging
def setup_logging():
    logs_dir = os.path.join(os.path.expanduser("~"), ".kitsu", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(logs_dir, f"task_manager_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kitsu Task Manager")
        self.setGeometry(50, 50, 400, 450)

        # Fix 1: Corrected Try/Except block for Icon
        try:
            icon_path = resource_path("icons/KitsuTaskManagerIcon.ico")
            self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            logger.warning(f"Could not load app icon: {e}")

        # Initialize software detection (Commented out as per your code)
        # self.software_availability = {}
        # self.detect_installed_software()
        
        # --- LOGIN FLOW ---
        # 1. Load Creds
        stored_credentials = load_credentials()
        
        # 2. Try Auto Login
        # If credentials exist AND auto-login works, we enter the app.
        if stored_credentials and self.auto_login():
            return
            
        # 3. If failed, show login screen
        self.show_login_screen()

        # Optional: Pre-fill fields if we have partial creds
        if stored_credentials:
            if stored_credentials.get('kitsu_url'):
                self.url_name_input.setText(stored_credentials['kitsu_url'])
            if stored_credentials.get('username'):
                self.user_name_input.setText(stored_credentials['username'])


    def apply_stylesheet(self):
         self.setStyleSheet("""             
            QMainWindow { background-color: #1f1f1f; }
            QLabel { color: #f0f0f0; font-size: 14px; }
            QGroupBox {
                color: #f0f0f0; font-size: 16px; font-weight: bold;
                border: 1px solid #444; border-radius: 8px; margin-top: 10px;
            }
            QGroupBox:title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }
            QLineEdit, QTextEdit {
                background-color: #2c2c2c; color: #fff;
                border: 1px solid #555; padding: 6px; border-radius: 4px;
            }
            QPushButton {
                background-color: #007acc; color: #ffffff;
                font-weight: bold; border-radius: 5px; padding: 8px 12px;
            }
            QPushButton:hover { background-color: #005fa3; }
            QPushButton:disabled { background-color: #555; color: #aaa; }
            QListWidget {
                background-color: #2a2a2a; color: white; border: 1px solid #444;
            }
            QListWidget::item:selected { background-color: #007acc; color: white; }
            QToolButton {
                background-color: #2c2c2c; color: #f0f0f0;
                border: 1px solid #444; padding: 6px; border-radius: 4px;
            }
            QToolButton:hover { background-color: #007acc; }
            QMenu {
                background-color: #2c2c2c; color: #f0f0f0;
                border: 1px solid #444; padding: 6px; border-radius: 4px;
            }
            QMenu::item:selected { background-color: #007acc; color: white; }
    """)
          
    def show_login_screen(self):
        """Display the login screen."""
        # Create a clean central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.setGeometry(50, 50, 400, 450) # Ensure enough height

        main_layout = QVBoxLayout(central_widget)
        central_widget.setLayout(main_layout)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(10)

        # Title
        self.title_label = QLabel("Log in to Kitsu", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(self.title_label)

        # URL
        self.url_name_label = QLabel("Kitsu URL:", self)
        main_layout.addWidget(self.url_name_label)
        self.url_name_input = QLineEdit(self)
        self.url_name_input.setPlaceholderText("https://kitsu.betweenstudios.org")
        main_layout.addWidget(self.url_name_input)

        # User
        self.user_name_label = QLabel("Username (Email):", self)
        main_layout.addWidget(self.user_name_label)
        self.user_name_input = QLineEdit(self)
        self.user_name_input.setPlaceholderText("artist@betweenstudios.org")
        main_layout.addWidget(self.user_name_input)

        # Pass
        self.password_label = QLabel("Password:", self)
        main_layout.addWidget(self.password_label)
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.start_process) # Allow Enter key
        main_layout.addWidget(self.password_input)

        # Button
        self.input_button = QPushButton("Log in", self)
        self.input_button.setCursor(Qt.PointingHandCursor)
        self.input_button.clicked.connect(self.start_process)
        main_layout.addWidget(self.input_button)

        main_layout.addStretch()
        self.apply_stylesheet()

    def auto_login(self):
        try:
            # This calls the updated auth logic from utils
            kitsu_auto_login()
            
            # If successful, we need to populate selections for other parts of the app
            creds = load_credentials()
            self.selections = {
                "kitsu_url": creds.get("kitsu_url"),
                "username": creds.get("username"),
            }
            
            self.update_ui_with_kitsu()
            # self.setup_dcc_integrations() 
            return True
        except Exception as e:
            logger.warning(f"Auto-login failed: {str(e)}")
            # We do NOT show a popup here, we just silently fail to the login screen
            return False

    def start_process(self):
        """
        Triggered by the Login Button.
        Uses the new login_ui_logic to handle Cloudflare tokens.
        """
        url = self.url_name_input.text().strip()
        username = self.user_name_input.text().strip()
        password = self.password_input.text().strip()

        if not url or not username or not password:
             QMessageBox.warning(self, "Missing Info", "Please fill in all fields.")
             return

        # Disable button to prevent double-click crashes
        self.input_button.setEnabled(False)
        self.input_button.setText("Logging in...")
        QApplication.processEvents()

        try:
            # CALL THE NEW AUTH LOGIC
            success = login_ui_logic(url, username, password)
            
            if success:
                self.selections = {
                    "kitsu_url": url,
                    "username": username,
                    "password": password
                }
                self.update_ui_with_kitsu()
                # self.setup_dcc_integrations()
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid credentials or server error.")
                self.input_button.setEnabled(True)
                self.input_button.setText("Log in")
                
        except Exception as e:
            QMessageBox.warning(self, "Login Error", f"Error during login: {str(e)}")
            self.input_button.setEnabled(True)
            self.input_button.setText("Log in")

    # --- REMAINDER OF YOUR LOGIC (UNCHANGED MOSTLY) ---

    def detect_installed_software(self):
        """Detect installed DCC software."""
        try:
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
        # ... (rest of your search logic) ...
        return False

    def logout(self):
        clear_credentials()
        self.selections = {}
        clean_up_temp_files()
        QMessageBox.information(self, "Logout", "You have been logged out.")
        self.show_login_screen()

    def update_ui_with_kitsu(self):
        from kitsu_home_pipeline.utils.helpers import get_drive_root_paths

        drive_letter, root_folder = get_drive_root_paths()
        self.initial_directory_setup(drive_letter, root_folder)

        # Main Window
        self.setGeometry(100, 100, 1200, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        central_widget.setLayout(main_layout)

        # Header level
        header_level = QHBoxLayout()
        header_left_column = QVBoxLayout()
        header_left_column.setAlignment(Qt.AlignLeft)

        try:
            user_info = get_user_info(self.selections["username"])
            user_name = user_info.get("first_name", "") + " " + user_info.get("last_name", "")
        except:
            user_name = self.selections["username"]

        self.header_label = QLabel(f"Welcome: {user_name}", self)
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
            # Fallback icon
            self.username_button.setText("User") 

        self.username_button.setIconSize(QSize(50, 50))

        menu = QMenu(self)
        menu.addAction(self.selections["username"], self.view_profile)
        menu.addAction("Console logs", self.view_console)
        menu.addAction("Logout", self.logout)

        self.username_button.setMenu(menu)
        self.username_button.setPopupMode(QToolButton.InstantPopup)
        header_right_column.addWidget(self.username_button)

        header_level.addLayout(header_left_column)
        header_level.addStretch()
        header_level.addLayout(header_right_column)

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
        second_right_column = QVBoxLayout()
        versions_group = QGroupBox("Published Versions")
        versions_layout = QVBoxLayout(versions_group)

        self.versions_label = QLabel("Published Versions")
        self.versions_label.setAlignment(Qt.AlignCenter)
        versions_layout.addWidget(self.versions_label)

        self.versions_list = QListWidget(self)
        self.versions_list.addItems(["Published Versions"])
        self.versions_list.itemClicked.connect(self.on_version_selected)
        versions_layout.addWidget(self.versions_list)

        second_right_column.addWidget(versions_group)
        second_level.addLayout(second_right_column)

        main_layout.addLayout(header_level)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_layout.addLayout(first_level)
        main_layout.addLayout(second_level)
        
        self.apply_stylesheet()

    def view_profile(self):
        try:
            kitsu_url = self.selections.get("kitsu_url", "").rstrip("/api")
            my_tasks_url = f"{kitsu_url}/my-tasks"
            webbrowser.open(my_tasks_url)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open profile: {str(e)}")

    def view_console(self):
        if not hasattr(self, "log_console") or self.log_console is None:
            self.log_console = LogConsole()
            self.log_console.show()
            self.log_console.raise_()
            self.log_console.activateWindow()

    def add_task_to_list(self, task_type_name, due_date, status, entity_name, id, project_code, task_code, entity_type_name, project_id, task_type_for_entity, sequence):
        task_widget = QWidget()
        task_layout = QHBoxLayout(task_widget)

        text_layout_right = QVBoxLayout()
        text_layout_left = QVBoxLayout()

        thumbnail_path = get_preview_thumbnail(id)
        task_preview_icon_button = QToolButton(self)
        if thumbnail_path:
            pixmap = QPixmap(thumbnail_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            task_preview_icon_button.setIcon(QIcon(pixmap))
        else:
            task_preview_icon_button.setText("No Img")
        
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
        self.entity_list.addItems(entity_type_and_name)

    def on_entity_selected(self, item):
        selected_entity = item.text().split(" (")[0]
        # selected_entity_type = item.text().split("(")[1] 
        print(f"Selected entity: {selected_entity}")

        filtered_tasks = [
            task for task in self.task_details if task["entity_name"] == selected_entity
        ]

        self.tasks_list.clear()

        for task in filtered_tasks:
            # Unpacking task details
            self.add_task_to_list(
                task["task_type_name"], 
                task["due_date"], 
                task["status"], 
                selected_entity, 
                task["task_id"], 
                task["project_code"], 
                task["task_code"], 
                task["entity_type_name"], 
                task["project_id"], 
                task["task_type_for_entity"], 
                task["sequence"]
            )
    
    def on_task_selected(self):
        selected_task = self.get_selected_task()
        if selected_task:
            context = self.save_task_context(selected_task)
            # Ensure safe path joining
            if self.root_directory and context["project_code"]:
                path = os.path.join(self.root_directory, context["project_code"], "Publish", context["task_type_for_entity"], context["entity_name"], context["task_code"])
                print(f"Looking for published files in: {path}")
                self.published_files = collect_published_files(path)
            else:
                 self.published_files = []

            self.versions_list.clear()
            self.published_files_dict = {}
            
            if self.published_files:
                for file in self.published_files:
                    self.versions_list.addItem(file)
            else:
                self.versions_list.addItem("No published files found.")

    def get_selected_task(self):
        selected_item = self.tasks_list.currentItem()
        if not selected_item:
            # Don't show popup on single click, only if action requested on empty selection
            return None
        
        task_data = selected_item.data(Qt.UserRole)
        if task_data:
            return task_data
        return None

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
            try:
                pub_icon_path = resource_path("icons/KitsuPublisherIcon.ico")
                action_publish.setIcon(QIcon(pub_icon_path))
            except: pass

            action_view_details = menu.addAction("View Details")

            # Software Launching (Commented out per your request, but structure kept)
            # action_launch_software = menu.addMenu("Launch Software")
            
            action = menu.exec(self.mapToGlobal(event.pos()))

            if action is None:
                return

            if action == action_view_details:
                self.view_task_details()

            elif action == action_publish:
                from kitsu_home_pipeline.UI.publisher.new_gui import AgnosticPublisher
                from kitsu_home_pipeline.utils.file_utils import create_context_file, create_entity_directory
                
                selected_task = self.get_selected_task()
                if selected_task:
                    context = self.save_task_context(selected_task)
                    create_context_file(context)
                    # Create directory if it doesn't exist
                    create_entity_directory(self.root_directory, 
                                            context["project_code"], 
                                            context["task_type_for_entity"], 
                                            context["task_code"],
                                            context["entity_name"]
                                           )

                    print("Launching Publisher")
                    self.publisher_window = AgnosticPublisher()
                    self.publisher_window.show()

        elif self.versions_list.underMouse():
            menu = QMenu(self)
            action_open_directory = menu.addAction("File location")
            action_create_working = menu.addAction("Create working file from publish")

            action = menu.exec(self.mapToGlobal(event.pos()))
            
            if action:
                selected_version = self.versions_list.currentItem()
                # Ensure published_files is a dict or list to retrieve path
                # Since published_files seems to be a list of paths in collect_published_files:
                file_path = selected_version.text() 
                
                if action == action_open_directory:
                    from kitsu_home_pipeline.utils.file_utils import open_file_location
                    if file_path:
                        open_file_location(file_path)

                elif action == action_create_working:
                    from kitsu_home_pipeline.utils.file_utils import create_working_from_publish, open_file_location
                    
                    working_file_path = create_working_from_publish(file_path)
                    
                    wrkn_file_msg = QMessageBox()
                    wrkn_file_msg.setWindowTitle("Working file created")
                    wrkn_file_msg.setText(f"Working file created at:\n{working_file_path}")
                    wrkn_file_msg.setStandardButtons(QMessageBox.Ok)
                    wrkn_file_msg.exec()

                    open_file_location(working_file_path)

    def on_version_selected(self, item):
        print(f"Selected version: {item.text()}")

    def view_task_details(self):
        selected_task_data = self.get_selected_task()
        if selected_task_data:
             QMessageBox.information(self, "Task Details", f"Details for task: {selected_task_data['task_type_name']}")
    
    def initial_directory_setup(self, drive_letter, root_folder):
        from kitsu_home_pipeline.utils.file_utils import network_drive_detected
        project_codes_dict = get_project_code()
        
        project_codes = list(project_codes_dict.values())
        network_drive = network_drive_detected(drive_letter)
        
        if network_drive:
            create_main_directory(network_drive, root_folder, project_codes)
            self.root_directory = os.path.join(network_drive, root_folder)
        else:
            self.root_directory = None
            # Do NOT show a popup here during startup, just log it. 
            # Showing popups before the UI builds can freeze the app visually.
            logger.warning("Network drive not found. File operations will be disabled.")

    def closeEvent(self, event):
        if hasattr(self, "publisher_window") and self.publisher_window is not None:
            self.publisher_window.close()
        event.accept()

def run_gui():
    print("Welcome to the most amazing task manager ever!")
    print("............")
    
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    
    try:
        app_icon_path = resource_path("icons/KitsuIcon.ico")
        app.setWindowIcon(QIcon(app_icon_path))
    except: pass
    
    app.setFont(QFont("Segoe UI", 10))
    window = TaskManager()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_gui()