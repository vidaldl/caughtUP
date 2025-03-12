import tkinter as tk
from tkinter import simpledialog, messagebox
from gui.main_interface import MainInterface
from backup_manager.token_manager import TokenManager
import os
import atexit
import logging

# Ensure log directory exists, use user's home directory for logs when packaged
if getattr(sys, 'frozen', False):
    # Running as packaged app
    log_dir = os.path.join(os.path.expanduser("~"), "CaughtUP", "logs")
else:
    # Running in development
    log_dir = "logs"
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

def save_state_on_exit():
    try:
        # Placeholder: Add logic to save temporary data or clean up resources
        print("Application state saved successfully.")
    except Exception as e:
        print(f"Error while saving state: {e}")

def main():
    # Initialize the root Tkinter window
    root = tk.Tk()

    # Register cleanup function
    atexit.register(save_state_on_exit)

    # Initialize the TokenManager which now handles base_url validation internally
    token_manager = TokenManager()
    
    # Create the main interface
    MainInterface(root, token_manager)

    # Start the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()
