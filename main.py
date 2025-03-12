import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import time
import threading
import atexit
import logging

# Fix working directory when running as app bundle
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running as bundled app
    bundle_dir = os.path.dirname(sys.executable)
    if '.app/Contents/MacOS' in bundle_dir:
        # Running from .app bundle on macOS
        os.chdir(os.path.abspath(os.path.dirname(bundle_dir.split('.app/Contents/MacOS')[0])))

# Configure logging
if getattr(sys, 'frozen', False):
    log_dir = os.path.join(os.path.expanduser("~"), "CaughtUP", "logs")
else:
    log_dir = os.path.abspath("logs")

os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "app.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

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
        self.progress.start(10)
        self.window.update()
        
    def update_status(self, text):
        self.status_var.set(text)
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
            from backup_manager.token_manager import TokenManager
            token_manager = TokenManager()
            
            loading.update_status("Initializing interface...")
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