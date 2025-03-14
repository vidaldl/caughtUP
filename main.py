import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import time
import threading
import atexit
import logging

# Import platform utility functions
from platform_utils import get_app_data_dir, get_logs_dir, setup_user_directories

# Set up necessary directories for the application
app_dirs = setup_user_directories()
log_dir = app_dirs['logs_dir']

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

logging.info(f"Application starting. Platform: {sys.platform}")
logging.info(f"Application directories: {app_dirs}")

def save_state_on_exit():
    try:
        logging.info("Application state saved successfully.")
    except Exception as e:
        logging.error(f"Error while saving state: {e}")

class LoadingWindow:
    def __init__(self, master):
        self.master = master
        self.window = tk.Toplevel(master)
        self.window.withdraw()  # Hide initially 
        
        # Configure window
        self.window.title("Loading")
        self.window.attributes('-topmost', True)
        
        # No window decorations or titlebar if supported on this platform
        try:
            self.window.overrideredirect(True)
        except:
            pass
        
        # Size and position
        width, height = 300, 80
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Frame for content
        frame = tk.Frame(self.window, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Progress bar
        self.progress = ttk.Progressbar(frame, mode="indeterminate", length=280)
        self.progress.pack(pady=(5, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Loading...")
        status_label = tk.Label(frame, textvariable=self.status_var)
        status_label.pack()
        
    def show(self, status_text=None):
        if status_text:
            self.status_var.set(status_text)
        self.window.deiconify()
        self.window.attributes('-topmost', True)  # Ensure it's on top
        self.progress.start(10)
        self.window.update()
        
    def update_status(self, text):
        self.status_var.set(text)
        self.window.update()
    
    def prepare_for_dialog(self):
        """Lower the window priority before showing dialogs"""
        self.window.attributes('-topmost', False)
        self.window.lower()  # Push the window below other windows
        self.window.update()
        
    def hide(self):
        self.progress.stop()
        self.window.withdraw()

def main():
    # Create the minimal root window without showing it
    root = tk.Tk()
    root.withdraw()
    
    # Register cleanup function
    atexit.register(save_state_on_exit)
    
    # Create a loading window 
    loading = LoadingWindow(root)
    
    # This function loads and initializes components after the UI appears
    def delayed_initialization():
        try:
            # Now we import the heavy modules AFTER the UI is shown
            loading.show("Loading token manager...")
            
            # IMPORTANT: Lower the loading window priority before token dialogs may appear
            loading.prepare_for_dialog()
            
            # Import and initialize token manager which may show dialogs
            from backup_manager.token_manager import TokenManager
            token_manager = TokenManager()
            
            # Show loading window again after token dialog
            loading.show("Initializing interface...")
            
            # Initialize main interface
            from gui.main_interface import MainInterface
            app = MainInterface(root, token_manager)
            
            # Hide loading and show main window
            loading.hide()
            root.deiconify()
            
        except Exception as e:
            logging.error(f"Error during initialization: {e}", exc_info=True)
            loading.hide()
            messagebox.showerror("Error", f"Failed to initialize: {str(e)}")
            root.destroy()
    
    # Schedule the initialization to happen after a short delay
    # This ensures the loading window appears immediately
    root.after(100, lambda: loading.show("Starting..."))
    root.after(200, delayed_initialization)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()