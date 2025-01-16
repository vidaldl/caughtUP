import os
import time
from tkinter import messagebox
from backup_manager.api_handler import CanvasAPIHandler
from backup_manager.backup_runner import BackupRunner
import asyncio

class BackupManager:
    def __init__(self, main_interface, table):
        self.main_interface = main_interface
        self.table = table
        self.is_running = False
        self.interrupted_items = set()
        self.api_handler = None
        self.backup_runner = None
        self.stop_event = asyncio.Event()  # Add stop event

    def get_backup_directory(self):
        """Retrieve the user-selected backup directory from the config file."""
        config_file = "resources/config.txt"
        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    for line in f:
                        if line.startswith("backup_folder="):
                            return line.split("=", 1)[1].strip()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load backup directory: {e}")
        return "backups"  # Default to "backups" if not set

    def start_backup(self):
        if self.is_running:
            return

        self.is_running = True
        self.stop_event.clear()  # Clear stop event
        self.main_interface.start_button.config(state="disabled")
        self.main_interface.retry_button.config(state="disabled")
        self.main_interface.stop_button.config(state="normal")

        base_url = self.main_interface.token_manager.base_url
        api_token = self.main_interface.token_manager.get_token()
        output_dir = self.get_backup_directory()  # Get the dynamic backup directory

        async def async_start_backup():
            self.api_handler = CanvasAPIHandler(base_url, api_token)
            self.backup_runner = BackupRunner(self.api_handler, output_dir, self.stop_event)  # Pass stop event

            queue = asyncio.Queue()

            # Populate the queue with data from the table
            for item in self.table.get_children():
                course_name = self.table.item(item)['values'][0]
                course_id = self.table.item(item)['values'][1]
                status = self.table.item(item)['values'][2]
                if(status == "Pending" or status == "Failed" or status == "Stopped"):
                    queue.put_nowait((course_name, course_id, self.status_callback))
                    self.table.item(item, values=(course_name, course_id, "Queued", "0%"))

            try:
                # Process the queue
                await self.backup_runner.process_queue(queue)
            except Exception as e:
                messagebox.showerror("Backup Error", f"An unexpected error occurred: {e}")
            finally:
                self.is_running = False
                self.main_interface.start_button.config(state="normal")
                self.main_interface.retry_button.config(state="normal")
                self.main_interface.stop_button.config(state="disabled")
                await self.api_handler.close_session()

        asyncio.run(async_start_backup())

    def status_callback(self, course_name, course_id, status, progress):
        for item in self.table.get_children():
            if self.table.item(item)['values'][0] == course_name:
                self.table.item(item, values=(course_name, course_id, status, f"{progress}%"))
                self.main_interface.root.update()

    def retry_failed(self):
        for item in self.table.get_children():
            if self.table.item(item)['values'][2] == "Failed" or self.table.item(item)['values'][2] == "Stopped":
                self.table.item(item, values=(self.table.item(item)['values'][0], self.table.item(item)['values'][1], "Pending", "0%"))
        self.start_backup()

    def stop_backup(self):
        if self.is_running:
            self.stop_event.set()  # Set stop event
            messagebox.showinfo("Stop Backup", "Backup process stopped by user.")
        self.is_running = False
        self.main_interface.start_button.config(state="normal")
        self.main_interface.retry_button.config(state="normal")
        self.main_interface.stop_button.config(state="disabled")
