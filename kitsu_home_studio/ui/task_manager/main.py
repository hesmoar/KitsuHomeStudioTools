"""
Main task manager UI module
"""

import sys
import os
import webbrowser
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QCheckBox, QRadioButton, QButtonGroup, QFileDialog, QHBoxLayout, QGroupBox, 
    QFrame, QSpacerItem, QSizePolicy, QComboBox, QTextEdit, QInputDialog, QLineEdit, 
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout, QGridLayout, 
    QMessageBox, QListWidget, QListWidgetItem, QMenu, QToolButton, QSizeGrip
)
from PySide6.QtGui import QIcon, QPixmap, QFont, QColor, QPalette
from PySide6.QtCore import Qt, QSize

from ...core.auth import connect_to_kitsu, load_credentials, clear_credentials
from ...core.api import (
    get_user_projects, get_user_tasks_for_project, get_preview_thumbnail,
    get_user_avatar, get_project_short_name, get_task_short_name
)
from ...utils.file_utils import clean_up_temp_files, create_context_file
from ...integrations.resolve import ResolveIntegration
from ...integrations.krita import KritaIntegration

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

class TaskManager(QMainWindow):
    """Main task manager window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kitsu Task Manager")

        icon_path = os.path.join(current_dir, "icons", "KitsuTaskManagerIcon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setGeometry(50, 50, 400, 300)

        stored_credentials = load_credentials()
        if stored_credentials:
            self.selections = stored_credentials
            if self.auto_login():
                return
            
        self.show_login_screen()

    def apply_stylesheet(self):
        """Apply the application stylesheet."""
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

        main_layout = QVBoxLayout(central_widget)
        central_widget.setLayout(main_layout)

        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(10)

        # Title label
        self.title_label = QLabel("Task Manager", self)
        self.title_label.setAlignment(Qt.AlignCenter)
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
        """Attempt to log in with stored credentials."""
        try:
            connect_to_kitsu(
                self.selections["kitsu_url"],
                self.selections["username"],
                self.selections["password"]
            )
            self.update_ui_with_kitsu()
            return True
        except Exception as e:
            QMessageBox.warning(self, "Auto-Login Failed", f"Auto-login failed: {str(e)}")
            return False

    def get_selections(self):
        """Get user input selections."""
        self.selections = {
            "kitsu_url": self.url_name_input.text(),
            "username": self.user_name_input.text(),
            "password": self.password_input.text(),
        }
        return self.selections
    
    def start_process(self):
        """Start the login process."""
        self.get_selections()
        print("Starting process with selections:")

        try:
            connect_to_kitsu(
                self.selections["kitsu_url"],
                self.selections["username"],
                self.selections["password"]
            )

            self.update_ui_with_kitsu()
        except Exception as e:
            QMessageBox.warning(self, "Login Failed", f"Login failed: {str(e)}")

    def detect_installed_software(self):
        """Detect installed software and create integration instances."""
        self.software_integrations = {
            "Resolve": ResolveIntegration(self.get_software_path("Resolve.exe")),
            "Krita": KritaIntegration(self.get_software_path("krita.exe")),
            "Nuke": None  # TODO: Implement Nuke integration
        }

    def get_software_path(self, executable_name):
        """Get the path to a software executable."""
        from ...utils.file_utils import get_software_path
        return get_software_path(executable_name)

    def logout(self):
        """Log out the current user."""
        clear_credentials()
        self.selections = {}
        clean_up_temp_files()
        QMessageBox.information(self, "Logout", "You have been logged out.")
        
        self.setGeometry(50, 50, 400, 300)
        self.show_login_screen()

    def update_ui_with_kitsu(self):
        """Update the UI with Kitsu data."""
        # Main Window
        self.setGeometry(100, 100, 800, 700)

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

        self.header_label = QLabel(f"Welcome", self)
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
            self.username_button.setIcon(QIcon(os.path.join(current_dir, "icons", "photo.png")))
        
        self.username_button.setIconSize(QSize(50, 50))

        menu = QMenu(self)
        menu.addAction(self.selections["username"], self.view_profile)
        menu.addAction("Settings", self.view_settings)
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
        project_names, _ = get_user_projects()
        self.projects_list.addItems(project_names)
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

        first_level.addLayout(left_column)
        first_level.addLayout(right_column)

        # Second level
        second_level = QHBoxLayout()

        # Left Column (Second level)
        second_right_column = QVBoxLayout()

        tasks_group = QGroupBox("Tasks")
        tasks_layout = QVBoxLayout(tasks_group)

        self.tasks_label = QLabel("Tasks")
        self.tasks_label.setAlignment(Qt.AlignCenter)
        tasks_layout.addWidget(self.tasks_label)

        self.tasks_list = QListWidget(self)
        self.tasks_list.addItems(["Your tasks"])
        tasks_layout.addWidget(self.tasks_list)

        second_right_column.addWidget(tasks_group)

        second_level.addLayout(second_right_column)

        main_layout.addLayout(header_level)
        main_layout.addLayout(first_level)
        main_layout.addLayout(second_level)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        self.apply_stylesheet()
        self.detect_installed_software()

    def view_profile(self):
        """Open user profile in web browser."""
        try:
            kitsu_url = self.selections.get("kitsu_url", "").rstrip("/api")
            my_tasks_url = f"{kitsu_url}/my-tasks"
            webbrowser.open(my_tasks_url)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open profile: {str(e)}")

    def view_settings(self):
        """Open settings in web browser."""
        QMessageBox.information(self, "Settings", "Opening settings...")
        webbrowser.open("https://google.com")

    def add_task_to_list(self, task_type_name, due_date, status, entity_name, id, project_code, task_code, entity_type_name):
        """Add a task to the task list."""
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
            task_preview_icon_button.setIcon(QIcon(os.path.join(current_dir, "icons", "photo.png")))
        
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
            "project_code": project_code,
            "task_code": task_code,
            "entity_type_name": entity_type_name
        })

    def on_project_selected(self, item):
        """Handle project selection."""
        selected_project = item.text()
        entities, self.task_details, entities_type = get_user_tasks_for_project(
            self.selections["username"], selected_project
        )
        entity_type_and_name = [
            f"{entities[i]} ({entities_type[i]})" for i in range(len(entities))
        ]
        self.entity_list.clear()
        self.tasks_list.clear()
        self.entity_list.addItems(entity_type_and_name)

    def on_entity_selected(self, item):
        """Handle entity selection."""
        selected_entity = item.text().split(" (")[0]
        selected_entity_type = item.text().split("(")[1].rstrip(")")
        
        filtered_tasks = [
            task for task in self.task_details if task["entity_name"] == selected_entity
        ]

        self.tasks_list.clear()

        for task in filtered_tasks:
            self.add_task_to_list(
                task["task_type_name"],
                task["due_date"],
                task["status"],
                selected_entity,
                task["task_id"],
                task["project_code"],
                task["task_code"],
                task["entity_type_name"]
            )

    def get_selected_task(self):
        """Get the currently selected task."""
        selected_item = self.tasks_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "No Task Selected", "Please select a task to view details.")
            return None
        
        task_data = selected_item.data(Qt.UserRole)
        if task_data:
            return task_data
        
        QMessageBox.warning(self, "Task Not Found", "The selected task could not be found.")
        return None

    def save_task_context(self, task):
        """Save task context to file."""
        context = {
            "project_name": self.projects_list.currentItem().text(),
            "task_id": task["task_id"],
            "task_name": task["task_type_name"],
            "due_date": task["due_date"],
            "status": task["status"],
            "entity_name": task["entity_name"],
            "project_code": task["project_code"],
            "task_code": task["task_code"],
            "entity_type": task["entity_type_name"]
        }
        return context

    def contextMenuEvent(self, event):
        """Handle context menu events."""
        if self.tasks_list.underMouse():
            menu = QMenu(self)

            action_view_details = menu.addAction("View Details")

            action_launch_software = menu.addMenu("Launch Software")
            action_launch_software.setIcon(QIcon(os.path.join(current_dir, "icons", "PhotoIcon.ico")))
            
            action_launch_resolve = None
            if self.software_integrations.get("Resolve"):
                action_launch_resolve = action_launch_software.addAction("Launch Resolve")
                action_launch_resolve.setIcon(QIcon(os.path.join(current_dir, "icons", "DaVinci_Resolve_Icon.ico")))
            
            if self.software_integrations.get("Krita"):
                action_launch_krita = action_launch_software.addAction("Launch Krita")
                action_launch_krita.setIcon(QIcon(os.path.join(current_dir, "icons", "kritaicon.ico")))
            
            if self.software_integrations.get("Nuke"):
                action_launch_nuke = action_launch_software.addAction("Launch Nuke")
                action_launch_nuke.setIcon(QIcon(os.path.join(current_dir, "icons", "NukeIcon.ico")))
                action_launch_nuke.setEnabled(True)

            action_launch_software.addSeparator()

            action = menu.exec(self.mapToGlobal(event.pos()))

            if action is None:
                return

            if action == action_view_details:
                self.view_task_details()
            elif action == action_launch_resolve:
                selected_task = self.get_selected_task()
                if selected_task:
                    context = self.save_task_context(selected_task)
                    self.software_integrations["Resolve"].launch(context)
            elif action == action_launch_krita:
                selected_task = self.get_selected_task()
                if selected_task:
                    context = self.save_task_context(selected_task)
                    self.software_integrations["Krita"].launch(context)
            elif action == action_launch_nuke:
                selected_task = self.get_selected_task()
                if selected_task:
                    context = self.save_task_context(selected_task)
                    # TODO: Implement Nuke integration
                    pass

    def view_task_details(self):
        """View task details."""
        selected_items = self.tasks_list.currentItem()
        if selected_items:
            selected_task = selected_items.data(Qt.UserRole)
            QMessageBox.information(
                self,
                "Task Details",
                f"Details for task: {selected_task['task_type_name']}\n"
                f"Entity: {selected_task['entity_name']}\n"
                f"Status: {selected_task['status']}\n"
                f"Due Date: {selected_task['due_date']}"
            )

def run_gui():
    """Run the task manager GUI."""
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(current_dir, "icons", "KitsuIcon.ico")))
    app.setFont(QFont("Segoe UI", 10))
    window = TaskManager()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_gui() 