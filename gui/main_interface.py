# File: gui/main_interface.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from gui.csv_handler import CSVHandler
from gui.backup_manager import BackupManager
from gui.ui_components import create_table, create_progress_bar
from gui.menu_bar import MenuBar

class MainInterface:
    def __init__(self, root, token_manager):
        self.root = root
        self.token_manager = token_manager

        # Set the window title and dynamic size
        self.root.title("Course Backup Manager")

        # Load preferred size or use default dynamic size
        preferred_width = 800  # Example: default width
        preferred_height = 600  # Example: default height
        self.root.geometry(f"{preferred_width}x{preferred_height}")

        # Initialize and attach the menu bar
        self.menu_bar = MenuBar(root, self.token_manager)
        print("MenuBar initialized")  # Debugging statement

        # Create the main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # CSV upload section
        self.csv_handler = CSVHandler(self)
        self.csv_frame = ttk.Frame(self.main_frame)
        self.csv_frame.pack(fill=tk.X, pady=10)

        self.browse_button = ttk.Button(
            self.csv_frame, text="Browse CSV", command=self.csv_handler.browse_csv
        )
        self.browse_button.pack(side=tk.LEFT, padx=5)

        self.csv_label = ttk.Label(
            self.csv_frame, text="No file selected", anchor="w"
        )
        self.csv_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Course table section
        self.table_frame = ttk.Frame(self.main_frame)
        self.table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.table = create_table(self.table_frame)

        # Control panel section
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=10)

        self.backup_manager = BackupManager(self, self.table)
        self.start_button = ttk.Button(
            self.control_frame, text="Start Backup", command=self.backup_manager.start_backup
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.start_button.config(state=tk.DISABLED)  # Disable initially

        self.retry_button = ttk.Button(
            self.control_frame, text="Retry Failed", command=self.backup_manager.retry_failed
        )
        self.retry_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(
            self.control_frame, text="Stop", command=self.backup_manager.stop_backup
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Overall progress bar
        self.progress_frame = ttk.Frame(self.main_frame)
        self.progress_frame.pack(fill=tk.X, pady=10)
        self.progress_label, self.overall_progress = create_progress_bar(self.progress_frame)

        # State variables
        self.is_running = False
