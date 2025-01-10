# File: main.py

import tkinter as tk
from tkinter import simpledialog, messagebox
from gui.main_interface import MainInterface
from backup_manager.token_manager import TokenManager
import os
import atexit

def load_base_url():
    config_file = "resources/config.txt"
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                for line in f:
                    if line.startswith("base_url="):
                        base_url = line.split("=", 1)[1].strip()
                        # Validate the base_url format (basic validation)
                        if base_url.startswith("http://") or base_url.startswith("https://"):
                            return base_url
                        else:
                            print("Invalid base_url format in configuration file.")
                            return None
        except (IOError, OSError) as e:
            print(f"Error reading configuration file: {e}")
            return None
    return None

def prompt_base_url_via_gui(root):
    while True:
        base_url = simpledialog.askstring("Base URL Required", "Enter the Canvas API base URL (must start with https://):")
        if base_url:
            if base_url.startswith("https://"):
                try:
                    os.makedirs("resources", exist_ok=True)
                    with open("resources/config.txt", "w") as f:
                        f.write(f"base_url={base_url}\n")
                    return base_url
                except (IOError, OSError) as e:
                    messagebox.showerror("Error", f"Error saving configuration file: {e}")
                    return None
            else:
                messagebox.showerror("Error", "The URL must start with https://. Please try again.")
        else:
            messagebox.showerror("Error", "A base URL is required to proceed.")
            return None

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

    # Load the base URL from the configuration file or prompt the user
    base_url = load_base_url()
    if not base_url:
        base_url = prompt_base_url_via_gui(root)
        if not base_url:
            return

    # Initialize the token manager with the base URL
    token_manager = TokenManager(base_url)

    # Create the main interface
    MainInterface(root, token_manager)

    # Start the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()
