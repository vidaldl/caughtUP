import os
import sys
import platform
import logging

def get_platform():
    """Returns the current platform: 'windows', 'macos', or 'other'"""
    system = platform.system().lower()
    if system == 'darwin':
        return 'macos'
    elif system == 'windows':
        return 'windows'
    else:
        return 'other'

def get_app_data_dir(app_name='CaughtUP'):
    """
    Returns the appropriate directory for storing application data
    based on the current platform.
    
    Windows: %APPDATA%/CaughtUP (e.g., C:/Users/username/AppData/Roaming/CaughtUP)
    macOS: ~/Library/Application Support/CaughtUP
    Other: ~/.caughtup
    """
    platform_name = get_platform()
    
    if platform_name == 'windows':
        # Use %APPDATA% on Windows (AppData/Roaming)
        base_dir = os.environ.get('APPDATA')
        if not base_dir:
            # Fallback if APPDATA is not available
            base_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming')
    
    elif platform_name == 'macos':
        # Use ~/Library/Application Support on macOS
        base_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support')
    
    else:
        # Use ~/.appname for other platforms
        base_dir = os.path.expanduser('~')
        app_name = f".{app_name.lower()}"
    
    # Combine base directory with app name
    app_data_dir = os.path.join(base_dir, app_name)
    
    # Ensure directory exists
    os.makedirs(app_data_dir, exist_ok=True)
    
    logging.info(f"Application data directory: {app_data_dir}")
    return app_data_dir

def get_resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller bundle.
    
    Args:
        relative_path: Path relative to the application root
        
    Returns:
        Absolute path to the resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        logging.info(f"Using PyInstaller _MEIPASS path: {base_path}")
    except Exception:
        # We're not running from a bundle
        base_path = os.path.abspath(".")
        logging.info(f"Using development path: {base_path}")
    
    return os.path.join(base_path, relative_path)

def get_logs_dir():
    """
    Returns the appropriate directory for storing log files.
    Creates the directory if it doesn't exist.
    """
    app_data_dir = get_app_data_dir()
    logs_dir = os.path.join(app_data_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir

def setup_user_directories():
    """
    Creates all necessary user directories for the application.
    Should be called early in application startup.
    """
    app_data_dir = get_app_data_dir()
    
    # Create resources directory
    resources_dir = os.path.join(app_data_dir, 'resources')
    os.makedirs(resources_dir, exist_ok=True)
    
    # Create logs directory
    logs_dir = os.path.join(app_data_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create backups directory if it doesn't exist already
    backups_dir = os.path.join(app_data_dir, 'backups')
    os.makedirs(backups_dir, exist_ok=True)
    
    return {
        'app_data_dir': app_data_dir,
        'resources_dir': resources_dir,
        'logs_dir': logs_dir,
        'backups_dir': backups_dir
    }

def ensure_backup_folder_configured():
    """
    Checks if a backup folder is configured, and prompts the user to select
    one if it isn't. Returns the backup folder path.
    """
    from tkinter import filedialog, messagebox
    
    app_data_dir = get_app_data_dir()
    config_file = os.path.join(app_data_dir, "resources", "config.txt")
    
    # Check if config file exists and has backup_folder
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                for line in f:
                    if line.startswith("backup_folder="):
                        folder_path = line.strip().split("=", 1)[1]
                        if os.path.exists(folder_path) and os.access(folder_path, os.W_OK):
                            return folder_path
        except Exception as e:
            logging.warning(f"Failed to read backup_folder from config: {e}")
    
    # No valid backup folder found, prompt user
    messagebox.showinfo(
        "Backup Folder Required", 
        "Please select a folder where course backups will be saved.\n"
        "You can change this later in File > Change Default Backup Folder."
    )
    
    while True:
        folder = filedialog.askdirectory(title="Select Backup Folder")
        
        if not folder:  # User cancelled
            # Use default in app data directory instead of forcing user selection
            default_dir = os.path.join(app_data_dir, "backups")
            os.makedirs(default_dir, exist_ok=True)
            folder = default_dir
            break
            
        if not os.access(folder, os.W_OK):
            messagebox.showerror(
                "Permission Denied", 
                "The selected folder is not writable. Please choose a different folder."
            )
            continue
            
        # Valid folder selected
        break
        
    # Save to config
    resources_dir = os.path.join(app_data_dir, "resources")
    os.makedirs(resources_dir, exist_ok=True)
    
    # Read existing config
    lines = []
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            lines = f.readlines()
    
    # Update or add backup_folder
    backup_folder_written = False
    with open(config_file, "w") as f:
        for line in lines:
            if line.startswith("backup_folder="):
                f.write(f"backup_folder={folder}\n")
                backup_folder_written = True
            else:
                f.write(line)
        if not backup_folder_written:
            f.write(f"backup_folder={folder}\n")
    
    return folder