import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import asyncio
from gui.csv_handler import CSVHandler
from gui.ui_components import create_table
from gui.menu_bar import MenuBar
from gui.backup_manager import BackupManager
from backup_manager.token_manager import TokenManager

class MainInterface:
    def __init__(self, root, token_manager):
        self.root = root
        self.token_manager = token_manager
        self.current_data = []

        # Initialize core UI components first
        self._create_basic_layout()
        
        # Initialize BackupManager AFTER UI components
        self.backup_manager = BackupManager(self, self.table)
        self.is_running = False

        # Complete window setup
        self._complete_initialization()

    def _create_basic_layout(self):
        """Create essential UI components needed by other components"""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # CSV section
        self.csv_frame = ttk.Frame(self.main_frame)
        self.csv_frame.pack(fill=tk.X, pady=10)
        self.csv_handler = CSVHandler(self)
        
        # Table section
        self.table_frame = ttk.Frame(self.main_frame)
        self.table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.table = create_table(self.table_frame, self._handle_filter_changed)

        # Progress bar
        self.progress_frame = ttk.Frame(self.main_frame)
        self.progress_frame.pack(fill=tk.X, pady=10)

    def _complete_initialization(self):
        """Finish setting up components that depend on core UI"""
        # CSV controls
        self.browse_button = ttk.Button(
            self.csv_frame, 
            text="Browse CSV", 
            command=self.csv_handler.browse_csv
        )
        self.browse_button.pack(side=tk.LEFT, padx=5)
        
        self.csv_label = ttk.Label(self.csv_frame, text="No file selected", anchor="w")
        self.csv_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Control buttons
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ttk.Button(
            self.control_frame, 
            text="Start Backup", 
            command=self.backup_manager.start_backup
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.start_button.config(state=tk.DISABLED)
        
        self.retry_button = ttk.Button(
            self.control_frame, 
            text="Retry Failed", 
            command=self.backup_manager.retry_failed
        )
        self.retry_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            self.control_frame, 
            text="Stop", 
            command=self.backup_manager.stop_backup
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.stop_button.config(state=tk.DISABLED)

        # Progress bar components
        self.progress_label = ttk.Label(self.progress_frame, text="Overall Progress", anchor="w")
        self.progress_label.pack(side=tk.LEFT, padx=5)
        
        self.overall_progress = ttk.Progressbar(self.progress_frame, mode="determinate")
        self.overall_progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Final window setup
        self.root.title("Course Backup Manager")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.menu_bar = MenuBar(self.root, self.token_manager)

    def _handle_filter_changed(self, filter_text):
        """Handle filter text changes"""
        filter_text = filter_text.lower()
        filtered_data = [
            item for item in self.current_data
            if any(filter_text in str(value).lower() 
                  for value in item.values())
        ]
        self._refresh_table(filtered_data)

    def _refresh_table(self, data=None):
        """Refresh table view with optional filtered data"""
        self.table.delete(*self.table.get_children())
        items = data if data is not None else self.current_data
        
        for item in items:
            self.table.insert("", tk.END, values=(
                item["sanitized_name"],
                item["course_id"],
                item["status"],
                item["progress"]
            ))

    def update_progress_bar(self, value):
        """Update the main progress bar"""
        self.overall_progress["value"] = value
        self.root.update_idletasks()

    def status_callback(self, course_name, course_id, status, progress):
        """Update status in current_data and refresh view"""
        for item in self.current_data:
            if item["course_id"] == course_id:
                item["status"] = status
                item["progress"] = f"{progress}%"
                break
                
        self._refresh_table()
        self._update_overall_progress()

    def _update_overall_progress(self):
        """Calculate and update the overall progress bar"""
        completed = sum(
            1 for item in self.current_data
            if item["status"] in ["Completed", "Failed", "Stopped"]
        )
        total = len(self.current_data)
        self.update_progress_bar((completed / total) * 100 if total > 0 else 0)

    def on_close(self):
        """Handle application close event"""
        if self.is_running:
            if not messagebox.askyesno("Exit", "Tasks are running. Are you sure you want to exit?"):
                return
        
        # Ensure sleep prevention is stopped when closing the app
        self.backup_manager.stop_backup()
        self.backup_manager._stop_sleep_prevention()  # Add this line
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    token_manager = TokenManager()
    app = MainInterface(root, token_manager)
    root.mainloop()