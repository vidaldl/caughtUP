import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
from backup_manager.token_manager import TokenManager
from platform_utils import get_app_data_dir

class MenuBar:
    def __init__(self, root, token_manager: TokenManager):
        self.root = root
        self.token_manager = token_manager
        self.app_data_dir = get_app_data_dir()

        # Create the menu bar
        self.menu_bar = tk.Menu(root)

        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Change Default Backup Folder", command=self.change_backup_folder)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # Token management menu
        self.token_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.token_menu.add_command(label="Update Token", command=self.update_token)
        self.token_menu.add_command(label="Reset Token", command=self.reset_token)
        self.menu_bar.add_cascade(label="Token Management", menu=self.token_menu)

        # Attach the menu bar to the root window
        root.config(menu=self.menu_bar)

    def change_backup_folder(self):
        folder = filedialog.askdirectory(title="Select Backup Folder")
        if folder:
            if os.access(folder, os.W_OK):
                # Get the config file path from the app data directory
                resources_dir = os.path.join(self.app_data_dir, "resources")
                os.makedirs(resources_dir, exist_ok=True)
                config_path = os.path.join(resources_dir, "config.txt")
                
                # Read existing lines from the config file
                lines = []
                if os.path.exists(config_path):
                    with open(config_path, "r") as f:
                        lines = f.readlines()
                
                # Update or add the backup_folder line
                with open(config_path, "w") as f:
                    backup_folder_written = False
                    for line in lines:
                        if line.startswith("backup_folder="):
                            f.write(f"backup_folder={folder}\n")
                            backup_folder_written = True
                        else:
                            f.write(line)
                    if not backup_folder_written:
                        f.write(f"backup_folder={folder}\n")
                
                messagebox.showinfo("Backup Folder Changed", f"Default backup folder set to: {folder}")
            else:
                messagebox.showerror("Permission Denied", "The selected folder is not writable. Please choose a different folder.")

    def update_token(self):
        token = simpledialog.askstring("Update Token", "Enter new API token:")
        if token and token.strip():
            # The validate_token method needs to be implemented or replaced with direct token validation
            try:
                # Call the token_manager's method to encrypt and save the token
                self.token_manager.encrypt_token(token)
                messagebox.showinfo("Token Updated", "API token has been updated successfully.")
            except Exception as e:
                messagebox.showerror("Token Error", f"Failed to update token: {e}")
        else:
            messagebox.showerror("Empty Token", "No token was provided. Please try again.")

    def reset_token(self):
        if messagebox.askyesno("Reset Token", "Are you sure you want to reset the token?"):
            self.token_manager.reset_token()
            messagebox.showinfo("Token Reset", "API token has been reset. You will need to provide a new token on the next run.")