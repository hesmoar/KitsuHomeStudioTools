import sys
import os
import pathlib
from PySide6 import QtWidgets, QtCore
from kitsu_home_pipeline.utils import config  # Import your config module

class SetupWindow(QtWidgets.QDialog):
    """
    A simple dialog window to ask the user for the Studio Folder path.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("KitsuHomeStudioTools - First-Time Setup")
        self.setMinimumWidth(500)
        
        # Store the selected path
        self.selected_path = ""

        # --- Widgets ---
        self.layout = QtWidgets.QVBoxLayout()
        
        self.label = QtWidgets.QLabel(
            "Welcome! Please select your main 'Studio' folder.\n"
            "This is the root directory where all your projects are stored."
        )
        self.label.setWordWrap(True)
        
        # Path selection (HBox)
        self.path_layout = QtWidgets.QHBoxLayout()
        self.path_edit = QtWidgets.QLineEdit()
        self.path_edit.setPlaceholderText("e.g., P:\\KitsuProjects")
        self.browse_button = QtWidgets.QPushButton("Browse...")
        
        self.path_layout.addWidget(self.path_edit)
        self.path_layout.addWidget(self.browse_button)
        
        # Save/Cancel buttons (HBox)
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel
        )
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.button_box)

        # --- Layout ---
        self.layout.addWidget(self.label)
        self.layout.addLayout(self.path_layout)
        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

        # --- Connections ---
        self.browse_button.clicked.connect(self.browse_for_folder)
        self.button_box.accepted.connect(self.on_save)
        self.button_box.rejected.connect(self.reject) # Closes the dialog

    def browse_for_folder(self):
        """
        Opens a QFileDialog to select a directory.
        """
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select Studio Folder",
            os.path.expanduser("~") # Start at home directory
        )
        if path:
            # os.path.normpath cleans up slashes for consistency
            self.path_edit.setText(os.path.normpath(path))

    def on_save(self):
        """
        Validates the path and accepts the dialog.
        """
        path_str = self.path_edit.text().strip()
        if not path_str:
            QtWidgets.QMessageBox.warning(self, "Error", "Path cannot be empty.")
            return

        studio_path = pathlib.Path(path_str)
        if not studio_path.exists():
            QtWidgets.QMessageBox.warning(
                self, 
                "Error", 
                f"Path not found:\n{studio_path}\nPlease check the path and try again."
            )
            return

        # Store the valid path and accept (close) the dialog
        self.selected_path = path_str
        self.accept()

    def get_selected_path(self):
        """Returns the path set by the user."""
        return self.selected_path

def run_gui_configuration_setup() -> bool:
    """
    This is the new "main" function for setup.
    It loads config, and if needed, shows the GUI setup window.
    
    Returns:
        bool: True if setup is complete, False if user cancelled.
    """
    
    # 1. Load the current config
    app_config = config.load_config()

    # 2. Check if the key setting is missing
    studio_folder = app_config.get("StudioFolder")
    
    if studio_folder:
        # Config is already good, return True!
        return True

    # 3. The setting is missing, so run the GUI prompt
    print("Configuration is missing. Starting GUI setup...")
    
    # We must have one (and only one) QApplication
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    
    setup_dialog = SetupWindow()
    
    # .exec() shows the dialog modally (blocks until closed)
    if setup_dialog.exec() == QtWidgets.QDialog.Accepted:
        new_path = setup_dialog.get_selected_path()
        if new_path:
            # 4. User provided a valid path. Update and save config.
            app_config["StudioFolder"] = new_path
            config.save_config(app_config)
            print(f"Configuration saved successfully! Path: {new_path}")
            return True

    # User cancelled the prompt
    print("Setup was not completed. The application may not work.")
    return False

if __name__ == "__main__":
    # You can run this file directly to test the setup GUI
    run_gui_configuration_setup()