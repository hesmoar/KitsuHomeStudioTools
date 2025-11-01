import os
import sys
import shutil
import platform
from pathlib import Path
import logging
import subprocess
import tempfile
import winreg

logger = logging.getLogger(__name__)

class ResolveSetup:
    def __init__(self):
        self.system = platform.system()
        self.resolve_paths = self._get_resolve_paths()
        self.scripts_path = self._get_scripts_path()
        self.env_vars = self._get_env_vars()
        logger.info(f"Initialized ResolveSetup with system: {self.system}")
        logger.info(f"Environment variables to set: {self.env_vars}")

    def _get_env_vars(self):
        """Get the required environment variables for Resolve scripting."""
        if self.system == "Windows":
            return {
                "RESOLVE_SCRIPT_API": os.path.join(os.environ.get("APPDATA", "C:\\APPDATA"),
                                                 "Blackmagic Design",
                                                 "DaVinci Resolve",
                                                 "Support",
                                                 "Developer",
                                                 "Scripting"),
                "RESOLVE_SCRIPT_LIB": os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"),
                                                 "Blackmagic Design",
                                                 "DaVinci Resolve",
                                                 "fusionscript.dll"),
                "PYTHONPATH": os.path.join(os.environ.get("APPDATA", "C:\\ProgramData"),
                                         "Blackmagic Design",
                                         "DaVinci Resolve",
                                         "Support",
                                         "Developer",
                                         "Scripting",
                                         "Modules")
            }
        elif self.system == "Darwin":  # macOS
            return {
                "RESOLVE_SCRIPT_API": "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting",
                "RESOLVE_SCRIPT_LIB": "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so",
                "PYTHONPATH": "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
            }
        elif self.system == "Linux":
            return {
                "RESOLVE_SCRIPT_API": "/opt/resolve/Developer/Scripting",
                "RESOLVE_SCRIPT_LIB": "/opt/resolve/libs/Fusion/fusionscript.so",
                "PYTHONPATH": "/opt/resolve/Developer/Scripting/Modules"
            }
        return {}

    def _get_resolve_paths(self):
        """Get Resolve installation paths based on operating system."""
        paths = []
        
        if self.system == "Windows":
            # Common Resolve installation paths on Windows
            program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
            program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
            
            paths.extend([
                os.path.join(program_files, "Blackmagic Design", "DaVinci Resolve"),
                os.path.join(program_files_x86, "Blackmagic Design", "DaVinci Resolve")
            ])
            
        elif self.system == "Darwin":  # macOS
            paths.extend([
                "/Library/Application Support/Blackmagic Design/DaVinci Resolve",
                os.path.expanduser("~/Library/Application Support/Blackmagic Design/DaVinci Resolve")
            ])
            
        elif self.system == "Linux":
            paths.extend([
                "/opt/resolve",
                os.path.expanduser("~/.local/share/DaVinciResolve")
            ])
            
        return paths

    def _get_scripts_path(self):
        """Get the Resolve scripts path based on operating system."""
        if self.system == "Windows":
            return os.path.join(os.environ.get("APPDATA", ""), 
                              "Blackmagic Design", 
                              "DaVinci Resolve", 
                              "Support", 
                              "Fusion", 
                              "Scripts",
                              "Utility")
        elif self.system == "Darwin":  # macOS
            return os.path.expanduser("~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts")
        elif self.system == "Linux":
            return os.path.expanduser("~/.local/share/DaVinciResolve/Fusion/Scripts")
        return None

    #def _set_windows_env_var(self, name, value, user=True):
    #    """Set a Windows environment variable using the registry."""
    #    try:
    #        if user:
    #            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS)
    #        else:
    #            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'System\\CurrentControlSet\\Control\\Session Manager\\Environment', 0, winreg.KEY_ALL_ACCESS)
    #        
    #        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
    #        winreg.CloseKey(key)
    #        
    #        # Notify Windows about the change
    #        import ctypes
    #        HWND_BROADCAST = 0xFFFF
    #        WM_SETTINGCHANGE = 0x1A
    #        SMTO_ABORTIFHUNG = 0x0002
    #        result = ctypes.windll.user32.SendMessageTimeoutW(
    #            HWND_BROADCAST, WM_SETTINGCHANGE, 0, 'Environment',
    #            SMTO_ABORTIFHUNG, 5000, None
    #        )
    #        return True
    #    except Exception as e:
    #        logger.error(f"Error setting Windows environment variable {name}: {e}")
    #        return False

    #def setup_environment_variables(self):
    #    """Set up environment variables for Resolve integration."""
    #    try:
    #        logger.info("Starting environment variable setup")
    #        
    #        # Get environment variables
    #        env_vars = self._get_env_vars()
    #        logger.info(f"Environment variables to set: {env_vars}")
    #        
    #        # Set each environment variable
    #        for var_name, var_path in env_vars.items():
    #            logger.info(f"Setting {var_name} to {var_path}")
    #            
    #            if var_name == "PYTHONPATH":
    #                # For PYTHONPATH, we need to handle it differently
    #                current_path = os.environ.get(var_name, "")
    #                if current_path:
    #                    # Split existing paths and add new path if not present
    #                    paths = current_path.split(os.pathsep)
    #                    if var_path not in paths:
    #                        paths.append(var_path)
    #                    new_path = os.pathsep.join(paths)
    #                else:
    #                    new_path = var_path
    #                
    #                # Set the environment variable
    #                os.environ[var_name] = new_path
    #                
    #                # Set in Windows registry
    #                self._set_windows_env_var(var_name, new_path)
    #            else:
    #                # For other variables, set directly
    #                os.environ[var_name] = var_path
    #                
    #                # Set in Windows registry
    #                self._set_windows_env_var(var_name, var_path)
    #        
    #        logger.info("Successfully set environment variables")
    #        return True
    #        
    #    except Exception as e:
    #        logger.error(f"Error setting environment variables: {str(e)}")
    #        return False

    #def _create_user_setup_file(self):
    #    """Create a file with instructions for manual environment variable setup."""
    #    if self.system == "Windows":
    #        instructions = """
#To set up DaVinci Resolve environment variables:
#
#1. Press Windows + R
#2. Type 'sysdm.cpl' and press Enter
#3. Go to the 'Advanced' tab
#4. Click 'Environment Variables'
#5. Under 'User variables', click 'New'
#6. Add the following variables:
#
#"""
#            for var_name, var_path in self.env_vars.items():
#                instructions += f"{var_name}: {var_path}\n"
#            
#            instructions += "\nNote: For PYTHONPATH, append the path to your existing PYTHONPATH if it exists."
#        else:
#            instructions = """
#To set up DaVinci Resolve environment variables:
#
#1. Open Terminal
#2. Edit your shell profile:
#   - For bash: nano ~/.bash_profile
#   - For zsh: nano ~/.zshrc
#3. Add these lines:
#
#"""
#            for var_name, var_path in self.env_vars.items():
#                if var_name == "PYTHONPATH":
#                    instructions += f'export {var_name}="$PYTHONPATH:{var_path}"\n'
#                else:
#                    instructions += f'export {var_name}="{var_path}"\n'
#            
#            instructions += "\n4. Save the file and restart your terminal"
#
#        # Save instructions to a file
#        setup_file = os.path.join(os.path.expanduser("~"), "resolve_setup_instructions.txt")
#        with open(setup_file, "w") as f:
#            f.write(instructions)
#        
#        return setup_file
#
#    def find_resolve_installation(self):
#        """Find Resolve installation directory."""
#        for path in self.resolve_paths:
#            if os.path.exists(path):
#                return path
#        return None

    def setup_integration(self, source_scripts_dir):
        """
        Set up the integration by creating symlinks or copying files to Resolve's scripts directory.
        
        Args:
            source_scripts_dir (str): Path to the directory containing the scripts to be installed
        """
        if not self.scripts_path:
            logger.error("Could not determine Resolve scripts path")
            return False

        # First, set up environment variables
        if not self.setup_environment_variables():
            logger.error("Failed to set up environment variables")
            return False

        try:
            logger.info(f"Setting up integration with source directory: {source_scripts_dir}")
            logger.info(f"Target scripts path: {self.scripts_path}")

            # Create scripts directory if it doesn't exist
            os.makedirs(self.scripts_path, exist_ok=True)
            logger.info(f"Created/verified scripts directory: {self.scripts_path}")
            
            # Create KitsuTools directory if it doesn't exist
            kitsuTools_path = os.path.join(self.scripts_path, "KitsuTools")
            os.makedirs(kitsuTools_path, exist_ok=True)
            logger.info(f"Created/verified KitsuTools directory: {kitsuTools_path}")

            # Create symlink for the publisher script
            publisher_source = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                                          "UI", "publisher", "main.py")
            publisher_target = os.path.join(kitsuTools_path, "kitsu_publisher.py")
            
            logger.info(f"Publisher source path: {publisher_source}")
            logger.info(f"Publisher target path: {publisher_target}")

            # Verify source file exists
            if not os.path.exists(publisher_source):
                logger.error(f"Publisher source file does not exist: {publisher_source}")
                return False

            # Remove existing file/link if it exists
            if os.path.exists(publisher_target):
                logger.info(f"Removing existing file/link at: {publisher_target}")
                if os.path.islink(publisher_target):
                    os.unlink(publisher_target)
                else:
                    os.remove(publisher_target)

            # Create symlink
            try:
                if self.system == "Windows":
                    # On Windows, we need to use absolute paths for symlinks
                    abs_source = os.path.abspath(publisher_source)
                    logger.info(f"Creating Windows symlink from {abs_source} to {publisher_target}")
                    os.symlink(abs_source, publisher_target)
                else:
                    logger.info(f"Creating symlink from {publisher_source} to {publisher_target}")
                    os.symlink(publisher_source, publisher_target)
                logger.info(f"Successfully created symlink for publisher script at: {publisher_target}")
            except OSError as e:
                logger.error(f"Failed to create symlink for publisher script: {e}")
                # Fall back to copying if symlink fails
                logger.info(f"Attempting to copy file instead of symlink")
                try:
                    shutil.copy2(publisher_source, publisher_target)
                    logger.info(f"Successfully copied publisher script to: {publisher_target}")
                except Exception as copy_error:
                    logger.error(f"Failed to copy publisher script: {copy_error}")
                    return False

            # Get all Python files from source directory
            source_files = [f for f in os.listdir(source_scripts_dir) 
                          if f.endswith('.py')]
            logger.info(f"Found {len(source_files)} Python files in source directory")

            for file in source_files:
                source_path = os.path.join(source_scripts_dir, file)
                target_path = os.path.join(self.scripts_path, file)
                logger.info(f"Processing file: {file}")

                # Remove existing file/link if it exists
                if os.path.exists(target_path):
                    logger.info(f"Removing existing file/link at: {target_path}")
                    if os.path.islink(target_path):
                        os.unlink(target_path)
                    else:
                        os.remove(target_path)

                # Create symlink (or copy if symlink fails)
                try:
                    if self.system == "Windows":
                        # On Windows, we need to use absolute paths for symlinks
                        abs_source = os.path.abspath(source_path)
                        logger.info(f"Creating Windows symlink from {abs_source} to {target_path}")
                        os.symlink(abs_source, target_path)
                    else:
                        logger.info(f"Creating symlink from {source_path} to {target_path}")
                        os.symlink(source_path, target_path)
                except OSError as e:
                    logger.error(f"Failed to create symlink for {file}: {e}")
                    # If symlink fails, fall back to copying
                    try:
                        shutil.copy2(source_path, target_path)
                        logger.info(f"Copied {file} to Resolve scripts directory")
                    except Exception as copy_error:
                        logger.error(f"Failed to copy {file}: {copy_error}")
                        return False

            logger.info("Successfully set up Resolve integration")
            return True

        except Exception as e:
            logger.error(f"Error setting up Resolve integration: {str(e)}")
            return False

    def verify_setup(self):
        """Verify that the integration is properly set up."""
        if not self.scripts_path or not os.path.exists(self.scripts_path):
            return False

        # Check if our scripts are present
        required_files = ["kitsu_resolve_integration.py"]  # Add your required files here
        for file in required_files:
            if not os.path.exists(os.path.join(self.scripts_path, file)):
                return False

        # Check if environment variables are set
        for var_name, var_path in self.env_vars.items():
            if not os.environ.get(var_name) or not os.path.exists(os.environ.get(var_name)):
                return False

        return True

#    def verify_environment(self):
#        """Verify that the environment variables are set correctly."""
#        logger.info("Verifying environment variables")
#        missing_vars = []
#        
#        for var_name, var_path in self.env_vars.items():
#            current_value = os.environ.get(var_name)
#            logger.info(f"Checking {var_name}: current value = {current_value}, expected path = {var_path}")
#            
#            if not current_value:
#                missing_vars.append(var_name)
#                logger.warning(f"Missing environment variable: {var_name}")
#            elif var_name == "PYTHONPATH":
#                # For PYTHONPATH, we only verify that the variable is set
#                # since it's a list of paths and we don't need to check if each path exists
#                logger.info(f"PYTHONPATH is set to: {current_value}")
#            elif not os.path.exists(current_value):
#                missing_vars.append(f"{var_name} (path does not exist: {current_value})")
#                logger.warning(f"Path does not exist for {var_name}: {current_value}")
#
#        instructions_file = os.path.join(os.path.expanduser("~"), "resolve_setup_instructions.txt")
#        return {
#            "success": len(missing_vars) == 0,
#            "missing_vars": missing_vars,
#            "instructions_file": instructions_file
#        }
#
#    def get_setup_instructions(self):
#        """Get the path to the setup instructions file."""
#        return os.path.join(os.path.expanduser("~"), "resolve_setup_instructions.txt")
#
#    def _create_setup_instructions(self):
#        """Create a file with setup instructions for manual configuration."""
#        instructions_file = os.path.join(os.path.expanduser("~"), "resolve_setup_instructions.txt")
#        
#        # Get environment variables
#        env_vars = self._get_env_vars()
#        
#        # Create instructions based on OS
#        if sys.platform == "win32":
#            instructions = """DaVinci Resolve Integration Setup Instructions (Windows)
#
#1. Open System Properties:
#   - Press Windows + R
#   - Type 'sysdm.cpl' and press Enter
#   - Click on 'Advanced' tab
#   - Click 'Environment Variables'
#
#2. Under 'User variables', add or modify these variables:
#"""
#            for var_name, var_path in env_vars.items():
#                instructions += f"\n{var_name} = {var_path}\n"
#                
#        elif sys.platform == "darwin":  # macOS
#            instructions = """DaVinci Resolve Integration Setup Instructions (macOS)
#
#1. Open Terminal
#2. Edit your shell profile (e.g., ~/.zshrc or ~/.bash_profile)
#3. Add these lines:
#"""
#            for var_name, var_path in env_vars.items():
#                instructions += f"\nexport {var_name}={var_path}\n"
#                
#        else:  # Linux
#            instructions = """DaVinci Resolve Integration Setup Instructions (Linux)
#
#1. Open Terminal
#2. Edit your shell profile (e.g., ~/.bashrc)
#3. Add these lines:
#"""
#            for var_name, var_path in env_vars.items():
#                instructions += f"\nexport {var_name}={var_path}\n"
#        
#        # Add general instructions
#        instructions += """
#4. Save the file and restart your terminal/computer
#5. Verify the setup by opening DaVinci Resolve
#6. The Kitsu integration should be available in the Workspace menu
#
#If you need help, please check the logs or contact support.
#"""
#        
#        # Write instructions to file
#        try:
#            with open(instructions_file, 'w') as f:
#                f.write(instructions)
#            logger.info(f"Created setup instructions at: {instructions_file}")
#            return instructions_file
#        except Exception as e:
#            logger.error(f"Failed to create setup instructions: {str(e)}")
#            return None

def setup_resolve_integration(source_scripts_dir):
    """
    Main function to set up Resolve integration.
    
    Args:
        source_scripts_dir (str): Path to the directory containing the scripts to be installed
    
    Returns:
        bool: True if setup was successful, False otherwise
    """
    setup = ResolveSetup()
    
    # Find Resolve installation
    resolve_path = setup.find_resolve_installation()
    if not resolve_path:
        logger.error("Could not find DaVinci Resolve installation")
        return False
    
    # Set up the integration
    return setup.setup_integration(source_scripts_dir) 