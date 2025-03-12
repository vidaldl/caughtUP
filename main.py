import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import time
import atexit
import logging
import threading
from gui.main_interface import MainInterface
from backup_manager.token_manager import TokenManager

# Fix working directory when running as app bundle
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running as bundled app
    bundle_dir = os.path.dirname(sys.executable)
    if '.app/Contents/MacOS' in bundle_dir:
        # Running from .app bundle on macOS
        os.chdir(os.path.abspath(os.path.dirname(bundle_dir.split('.app/Contents/MacOS')[0])))
        print(f"Changed working directory to: {os.getcwd()}")

# Ensure log directory exists with absolute path
if getattr(sys, 'frozen', False):
    # Running as bundled app
    log_dir = os.path.join(os.path.expanduser("~"), "CaughtUP", "logs")
else:
    # Running in development
    log_dir = os.path.abspath("logs")

os.makedirs(log_dir, exist_ok=True)

# Configure logging
log_file = os.path.join(log_dir, "app.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Log system information
logging.info(f"Starting application")
logging.info(f"Python version: {sys.version}")
logging.info(f"Executable: {sys.executable}")
logging.info(f"Working directory: {os.getcwd()}")
logging.info(f"Frozen: {getattr(sys, 'frozen', False)}")
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    logging.info(f"MEIPASS: {sys._MEIPASS}")
logging.info(f"Log directory: {log_dir}")

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    result = os.path.join(base_path, relative_path)
    logging.info(f"Resource path for {relative_path}: {result}")
    return result

def save_state_on_exit():
    try:
        # Placeholder: Add logic to save temporary data or clean up resources
        logging.info("Application state saved successfully.")
    except Exception as e:
        logging.error(f"Error while saving state: {e}")

class SplashScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        
        # Get screen dimensions
        width, height = 500, 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Main frame
        frame = tk.Frame(self.root, bg="#f0f0f0", highlightbackground="#cccccc",
                         highlightthickness=1)
        frame.pack(fill="both", expand=True)
        
        # App title
        title = tk.Label(frame, text="Course Backup Manager", font=("Helvetica", 24, "bold"),
                        bg="#f0f0f0", fg="#305F87")
        title.pack(pady=(50, 10))
        
        # Version
        version = tk.Label(frame, text="v0.1", font=("Helvetica", 12),
                          bg="#f0f0f0", fg="#666666")
        version.pack(pady=(0, 20))
        
        # Progress bar
        self.progress_frame = tk.Frame(frame, bg="#f0f0f0")
        self.progress_frame.pack(pady=10, padx=50, fill="x")
        
        self.progress = ttk.Progressbar(self.progress_frame, mode="indeterminate", length=400)
        self.progress.pack(fill="x")
        self.progress.start(15)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Initializing...")
        status = tk.Label(frame, textvariable=self.status_var, bg="#f0f0f0", fg="#666666")
        status.pack(pady=10)
        
        # Copyright
        year = time.strftime("%Y")
        copyright = tk.Label(frame, text=f"© {year} David Leo Vidal", 
                            font=("Helvetica", 9), bg="#f0f0f0", fg="#999999")
        copyright.pack(side="bottom", pady=10)
        
        self.root.update()
    
    def update_status(self, text):
        logging.info(f"Splash status: {text}")
        self.status_var.set(text)
        self.root.update()
    
    def close(self):
        self.root.destroy()

def load_main_app():
    try:
        logging.info("Starting main application")
        root = tk.Tk()
        root.withdraw()  # Hide initially until fully loaded
        
        # Register cleanup function
        atexit.register(save_state_on_exit)
        
        # Create and initialize TokenManager with resource paths
        token_manager = TokenManager()
        
        # Create the main interface
        app = MainInterface(root, token_manager)
        
        # Show the window
        root.deiconify()
        
        # Start the Tkinter event loop
        root.mainloop()
    
    except Exception as e:
        logging.error(f"Error in main application: {e}", exc_info=True)
        try:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        except:
            print(f"Error: {str(e)}")
        sys.exit(1)

def main():
    try:
        # Show splash screen
        splash = SplashScreen()
        
        # Update status with short delays to ensure UI updates
        splash.update_status("Loading components...")
        time.sleep(0.3)
        
        splash.update_status("Initializing API connections...")
        time.sleep(0.3)
        
        splash.update_status("Preparing user interface...")
        time.sleep(0.3)
        
        # Schedule the splash screen to close and main app to launch
        splash.update_status("Starting application...")
        splash.root.after(1000, lambda: (splash.close(), load_main_app()))
        
        # Run the splash screen
        splash.root.mainloop()
    
    except Exception as e:
        logging.error(f"Error during startup: {e}", exc_info=True)
        
        try:
            # Try to show error dialog
            import tkinter.messagebox as msgbox
            msgbox.showerror("Startup Error", f"Error during startup: {str(e)}")
        except:
            print(f"Error: {str(e)}")
        
        # Try to start the main app directly if splash fails
        load_main_app()

if __name__ == "__main__":
    main()