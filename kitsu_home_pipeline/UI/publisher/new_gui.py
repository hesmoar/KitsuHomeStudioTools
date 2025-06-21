import os
import sys
import json
import logging
import pprint
import tkinter as tk
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QCheckBox, QRadioButton, QButtonGroup, QFileDialog, QHBoxLayout, QGroupBox, QFrame, QSpacerItem, QSizePolicy, QComboBox, QTextEdit, QToolButton, QMenu, QLineEdit, QMessageBox
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QCheckBox, QRadioButton, QButtonGroup, QFileDialog, QHBoxLayout, QGroupBox, 
    QFrame, QSpacerItem, QSizePolicy, QComboBox, QTextEdit, QInputDialog, QLineEdit, 
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout, QGridLayout, 
    QMessageBox, QListWidget, QListWidgetItem, QMenu, QToolButton, QScrollArea
)
 
from PySide6.QtGui import QIcon, QPixmap, QFont, QColor, QPalette, QDragEnterEvent, QDropEvent
from PySide6.QtCore import Qt, QThread, Signal, QSize, QMimeData
from kitsu_project_context import project_context, task_context, get_project
from kitsu_home_pipeline.utils.context_from_json import get_context_from_json, context_file_path
from kitsu_home_pipeline.utils import (
    get_user_projects,
    get_user_tasks_for_project,
    get_preview_thumbnail,
    clean_up_thumbnails,
    get_user_avatar,
    get_project_short_name,
    get_task_short_name
)
import keyring

current_dir = os.path.dirname(os.path.abspath(__file__))


class FileGalleryWidget(QWidget):
    """Custom widget for displaying files in a gallery view"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.files = []
        self.setup_ui()
        self.setAcceptDrops(True)
    
    def setup_ui(self):
        """Setup the gallery UI"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(7, 7, 7, 7)
        
        # Scroll area for the gallery
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container widget for the grid
        self.container_widget = QWidget()
        self.grid_layout = QGridLayout(self.container_widget)
        self.grid_layout.setSpacing(15)
        
        # Drop zone label
        self.drop_label = QLabel("Drag and drop files here")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 14px;
                padding: 20px;
                border: 2px dashed #555;
                border-radius: 10px;
                background-color: #2a2a2a;
            }
        """)
        self.grid_layout.addWidget(self.drop_label, 0, 0)
        
        self.scroll_area.setWidget(self.container_widget)
        self.layout.addWidget(self.scroll_area)
        
        # Set minimum size
        self.setMinimumHeight(200)
        
        # Apply styling
        self.setStyleSheet("""
            QWidget {
                background-color: #2a2a2a;
                border: 2px solid #555;
                border-radius: 8px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
    
    def add_file(self, file_path):
        """Add a file to the gallery"""
        if file_path not in self.files:
            self.files.append(file_path)
            self.update_gallery()
    
    def remove_file(self, file_path):
        """Remove a file from the gallery"""
        if file_path in self.files:
            self.files.remove(file_path)
            self.update_gallery()
    
    def clear_files(self):
        """Clear all files from the gallery"""
        self.files.clear()
        self.update_gallery()
    
    def get_files(self):
        """Get list of all files"""
        return self.files.copy()
    
    def update_gallery(self):
        """Update the gallery display"""
        # Clear existing widgets except the drop label
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget and widget != self.drop_label:
                widget.deleteLater()
        
        if not self.files:
            # Show drop zone when no files
            self.drop_label.setVisible(True)
            return
        
        # Hide drop zone when files are present
        self.drop_label.setVisible(False)
        
        # Add file thumbnails
        cols = 4  # Number of columns
        for i, file_path in enumerate(self.files):
            row = i // cols
            col = i % cols
            
            file_widget = self.create_file_widget(file_path)
            self.grid_layout.addWidget(file_widget, row, col)
    
    def create_file_widget(self, file_path):
        """Create a widget for displaying a single file"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # File icon/thumbnail
        icon_label = QLabel()
        icon_label.setFixedSize(80, 80)
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Get file extension
        _, ext = os.path.splitext(file_path.lower())
        
        # Create appropriate icon based on file type
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tga']:
            # Image file - try to load thumbnail
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(pixmap)
            else:
                icon_label.setText("IMG")
                icon_label.setStyleSheet("background-color: #4a4a4a; border-radius: 5px; color: white; font-weight: bold;")
        elif ext in ['.mp4', '.mov', '.avi', '.mkv', '.wmv']:
            icon_label.setText("VID")
            icon_label.setStyleSheet("background-color: #8B0000; border-radius: 5px; color: white; font-weight: bold;")
        elif ext in ['.wav', '.mp3', '.aac', '.flac']:
            icon_label.setText("AUD")
            icon_label.setStyleSheet("background-color: #006400; border-radius: 5px; color: white; font-weight: bold;")
        elif ext in ['.txt', '.doc', '.docx', '.pdf']:
            icon_label.setText("DOC")
            icon_label.setStyleSheet("background-color: #4169E1; border-radius: 5px; color: white; font-weight: bold;")
        else:
            icon_label.setText("FILE")
            icon_label.setStyleSheet("background-color: #666; border-radius: 5px; color: white; font-weight: bold;")
        
        # File name
        file_name = os.path.basename(file_path)
        name_label = QLabel(file_name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setStyleSheet("color: white; font-size: 10px; max-width: 80px;")
        name_label.setToolTip(file_path)  # Show full path on hover
        
        # Remove button
        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(20, 20)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_file(file_path))
        
        # Add widgets to layout
        layout.addWidget(icon_label, alignment=Qt.AlignCenter)
        layout.addWidget(name_label, alignment=Qt.AlignCenter)
        layout.addWidget(remove_btn, alignment=Qt.AlignRight)
        
        # Style the widget
        widget.setStyleSheet("""
            QWidget {
                background-color: #333;
                border: 1px solid #555;
                border-radius: 8px;
                padding: 5px;
            }
            QWidget:hover {
                border: 1px solid #777;
                background-color: #3a3a3a;
            }
        """)
        
        return widget
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                files.append(file_path)
        
        for file_path in files:
            self.add_file(file_path)


class UserHeaderWidget(QWidget):
    """Widget for displaying user header with avatar and menu"""
    
    # Signals
    logout_requested = Signal()
    settings_requested = Signal()
    profile_requested = Signal()
    
    def __init__(self, user_email=None, parent=None):
        super().__init__(parent)
        self.user_email = keyring.get_password("kitsu", "email")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the header UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Left side - Welcome message
        left_column = QVBoxLayout()
        left_column.setAlignment(Qt.AlignLeft)
        
        self.header_label = QLabel("Welcome")
        self.header_label.setAlignment(Qt.AlignLeft)
        self.header_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        left_column.addWidget(self.header_label)
        
        # Right side - User avatar and menu
        right_column = QVBoxLayout()
        right_column.setAlignment(Qt.AlignRight)
        
        # Avatar button
        self.username_button = QToolButton()
        self.setup_avatar()
        self.setup_menu()
        
        right_column.addWidget(self.username_button)
        
        # Add columns to main layout
        layout.addLayout(left_column)
        layout.addStretch()
        layout.addLayout(right_column)
    
    def setup_avatar(self):
        """Setup user avatar"""
        try:
            avatar_path = get_user_avatar(self.user_email)
            
            if avatar_path:
                pixmap = QPixmap(avatar_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.username_button.setIcon(QIcon(pixmap))
            else:
                self.username_button.setIcon(QIcon(os.path.join(current_dir, "icons", "photo.png")))
        except Exception as e:
            print(f"Error loading avatar: {e}")
            # Fallback to default icon
            self.username_button.setIcon(QIcon(os.path.join(current_dir, "icons", "photo.png")))
        
        self.username_button.setIconSize(QSize(50, 50))
    
    def setup_menu(self):
        """Setup user menu"""
        menu = QMenu(self)
        
        # Add menu items
        profile_action = menu.addAction(self.user_email, self.view_profile)
        settings_action = menu.addAction("Settings", self.view_settings)
        logout_action = menu.addAction("Logout", self.logout)
        
        # Note: QAction objects don't support setStyleSheet directly
        # Menu styling is handled by the QMenu stylesheet in StyleManager
        
        self.username_button.setMenu(menu)
        self.username_button.setPopupMode(QToolButton.InstantPopup)
    
    def view_profile(self):
        """View user profile"""
        print("Viewing user profile...")
        self.profile_requested.emit()
    
    def view_settings(self):
        """View settings"""
        print("Viewing settings...")
        self.settings_requested.emit()
    
    def logout(self):
        """Logout user"""
        print("Logging out...")
        self.logout_requested.emit()
    
    def set_welcome_message(self, message):
        """Set the welcome message"""
        self.header_label.setText(message)


class ProjectInfoWidget(QWidget):
    """Widget for displaying project and task information"""
    
    def __init__(self, context=None, parent=None):
        super().__init__(parent)
        self.context = context or {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the project info UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Project section
        info_group = QGroupBox("Kitsu Context")
        info_layout = QVBoxLayout(info_group)
        
        self.project_label = QLabel(f"Project: {self.context.get('project_name', 'Unknown Project')}")
        self.project_label.setStyleSheet("color: white; font-size: 14px;")
        self.task_label = QLabel(f"Task: {self.context.get('task_type_name', 'Unknown Task')}")
        self.task_label.setStyleSheet("color: white; font-size: 14px;")
        info_layout.addWidget(self.project_label)
        info_layout.addWidget(self.task_label)
        

        
        # Add groups to layout
        layout.addWidget(info_group)

    
    def update_context(self, context):
        """Update the context and refresh display"""
        self.context = context
        self.project_label.setText(f"Project: {self.context.get('project_name', 'Unknown Project')}")
        self.task_label.setText(f"Task: {self.context.get('task_type_name', 'Unknown Task')}")


class CommentWidget(QWidget):
    """Widget for handling comments and descriptions"""
    
    comment_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the comment UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Comment group
        comment_group = QGroupBox("Preview Comment")
        comment_layout = QVBoxLayout(comment_group)
        
        self.comment_label = QLabel("Add a description for the shot")
        self.comment_label.setStyleSheet("color: white; font-size: 14px;")
        
        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("Enter your comment here...")
        self.comment_edit.textChanged.connect(self.on_comment_changed)
        
        comment_layout.addWidget(self.comment_label)
        comment_layout.addWidget(self.comment_edit)
        
        layout.addWidget(comment_group)
    
    def on_comment_changed(self):
        """Handle comment text changes"""
        comment = self.comment_edit.toPlainText()
        self.comment_changed.emit(comment)
    
    def get_comment(self):
        """Get the current comment text"""
        return self.comment_edit.toPlainText()
    
    def set_comment(self, comment):
        """Set the comment text"""
        self.comment_edit.setPlainText(comment)
    
    def clear_comment(self):
        """Clear the comment"""
        self.comment_edit.clear()


class ActionButtonsWidget(QWidget):
    """Widget for action buttons (Start, Cancel)"""
    
    start_clicked = Signal()
    cancel_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the action buttons UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Start button
        self.start_button = QPushButton("Publish")
        self.start_button.clicked.connect(self.start_clicked.emit)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #28282e;
                color: white;
                font-size: 14px;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #737373;
            }
            QPushButton:disabled {
                background-color: #666;
                color: #aaa;
            }
        """)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_clicked.emit)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #28282e;
                color: white;
                font-size: 14px;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #737373;
            }
        """)
        
        # Add buttons to layout
        layout.addStretch()
        layout.addWidget(self.start_button)
        layout.addWidget(self.cancel_button)
        
    
    def set_start_enabled(self, enabled):
        """Enable or disable the start button"""
        self.start_button.setEnabled(enabled)
    
    def set_buttons_enabled(self, enabled):
        """Enable or disable all buttons"""
        self.start_button.setEnabled(enabled)
        self.cancel_button.setEnabled(enabled)


class StyleManager:
    """Manager for application styling"""
    
    @staticmethod
    def get_dark_theme():
        """Get the dark theme stylesheet"""
        return """
            QMainWindow {
                background-color: #1e1e22;
                color: #f0f0f0;
            }
            
            QLabel {
                font-size: 14px;
                color: white;
            }

            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #f0f0f0;
                border: 1px solid #555;
                border-radius: 8px;
                margin-top: 15px;
                padding: 15px;
            }

            QPushButton {
                background-color: #28282e;
                color: white;
                font-size: 14px;
                border-radius: 5px;
                padding: 8px 12px;
            }

            QPushButton:hover {
                background-color: #737373;
            }

            QRadioButton, QCheckBox {
                font-size: 14px;
                color: white;
            }

            QPushButton:disabled {
                background-color: #555;
                color: #aaa;
            }

            QLineEdit, QTextEdit {
                background-color: #333;
                color: white;
                border: 1px solid #555;
            }
            
            QMenu {
                background-color: #333;
                border: 1px solid #555;
                color: white;
            }
            
            QMenu::item {
                padding: 5px 10px;
            }
            
            QMenu::item:selected {
                background-color: #555;
            }
        """


class AgnosticPublisher(QMainWindow):
    """GUI for selecting export and render options"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kitsu Publisher")
        self.setGeometry(100, 100, 700, 500)
        
        # Initialize selections attribute
        self.selections = None
        
        # Get context from JSON with error handling
        try:
            self.context = get_context_from_json(context_file_path)
            self.project_name = self.context.get("project_name", "Unknown Project")
            self.task_name = self.context.get("task_type_name", "Unknown Task")
            print(f"Project name that comes from the context json: {self.project_name}")
        except Exception as e:
            print(f"Error loading context: {e}")
            # Fallback to default values
            self.context = {}
            self.project_name = "Unknown Project"
            self.task_name = "Unknown Task"
        
        # Setup UI
        self.setup_ui()
        
        # Connect signals
        self.connect_signals()
        
        # Apply styling
        self.apply_stylesheet()

    def setup_ui(self):
        """Setup the main UI using modular widgets"""
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Create modular widgets
        self.header_widget = UserHeaderWidget()
        self.project_info_widget = ProjectInfoWidget(self.context)
        self.file_gallery = FileGalleryWidget()
        self.comment_widget = CommentWidget()
        self.action_buttons = ActionButtonsWidget()
        
        # Add widgets to main layout
        main_layout.addWidget(self.header_widget)
        main_layout.addWidget(self.project_info_widget)
        main_layout.addWidget(self.create_file_section())
        main_layout.addWidget(self.comment_widget)
        main_layout.addWidget(self.action_buttons)
    
    def create_file_section(self):
        """Create the file selection section with gallery and buttons"""
        file_group = QGroupBox("Files to Publish")
        file_layout = QVBoxLayout(file_group)
        
        # Add file gallery
        file_layout.addWidget(self.file_gallery)
        
        # Add browse and clear buttons
        file_buttons_layout = QHBoxLayout()
        
        browse_button = QPushButton("Browse Files")
        browse_button.clicked.connect(self.browse_files)
        
        clear_button = QPushButton("Clear All")
        clear_button.clicked.connect(self.clear_files)
        
        file_buttons_layout.addWidget(browse_button)
        file_buttons_layout.addWidget(clear_button)
        file_buttons_layout.addStretch()
        
        file_layout.addLayout(file_buttons_layout)
        return file_group
    
    def connect_signals(self):
        """Connect all widget signals"""
        # Action button signals
        self.action_buttons.start_clicked.connect(self.start_process)
        self.action_buttons.cancel_clicked.connect(self.cancel_and_exit)
        
        # Header widget signals
        self.header_widget.logout_requested.connect(self.handle_logout)
        self.header_widget.settings_requested.connect(self.handle_settings)
        self.header_widget.profile_requested.connect(self.handle_profile)
        
        # Comment widget signals
        self.comment_widget.comment_changed.connect(self.on_comment_changed)
    
    def apply_stylesheet(self):
        """Apply the dark theme stylesheet"""
        self.setStyleSheet(StyleManager.get_dark_theme())
    
    def start_process(self):
        """Start process and set selections"""
        # Get selected files
        selected_files = self.file_gallery.get_files()
        
        # Set selections based on current state
        self.selections = {
            "project_name": self.project_name,
            "task_name": self.task_name,
            "comment": self.comment_widget.get_comment(),
            "files": selected_files,
            "action": "publish"
        }
        
        print(f"Starting process with {len(selected_files)} files...")
        self.close()
    
    def cancel_and_exit(self):
        """Cancel and exit the application"""
        # Clean up any running threads
        for thread in self.findChildren(QThread):
            if thread.isRunning():
                thread.quit()
                thread.wait()
        
        # Close the application properly
        QApplication.quit()
    
    def browse_files(self):
        """Browse and select files to publish"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Publish",
            "",
            "All Files (*.*)"
        )
        
        if files:
            for file_path in files:
                self.file_gallery.add_file(file_path)
    
    def clear_files(self):
        """Clear all files from the gallery"""
        self.file_gallery.clear_files()
    
    def on_comment_changed(self, comment):
        """Handle comment changes"""
        # You can add validation or other logic here
        pass
    
    def handle_logout(self):
        """Handle logout request"""
        print("Handling logout...")
        # Add logout logic here
    
    def handle_settings(self):
        """Handle settings request"""
        print("Opening settings...")
        # Add settings logic here
    
    def handle_profile(self):
        """Handle profile request"""
        print("Opening profile...")
        # Add profile logic here


def run_gui():
    """Function to run the GUI and return the user selections."""
    app = QApplication(sys.argv)
    window = AgnosticPublisher()
    window.show()
    app.exec()
    
    # Return selections if they exist, otherwise return None
    if hasattr(window, 'selections'):
        return window.selections
    else:
        return None


if __name__ == "__main__":
    selections = run_gui()
    print("\nUser Selections:")
    for key, value in selections.items():
        print(f"{key}: {value}")
