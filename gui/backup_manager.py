import time
from tkinter import messagebox
from backup_manager.api_handler import CanvasAPIHandler
from backup_manager.backup_runner import BackupRunner

class BackupManager:
    def __init__(self, main_interface, table):
        self.main_interface = main_interface
        self.table = table
        self.is_running = False
        self.interrupted_items = set()
        self.api_handler = None
        self.backup_runner = None

    def start_backup(self):
        if self.is_running:
            return

        self.is_running = True
        self.main_interface.start_button.config(state="disabled")
        self.main_interface.retry_button.config(state="disabled")
        self.main_interface.stop_button.config(state="normal")

        base_url = self.main_interface.token_manager.base_url
        api_token = self.main_interface.token_manager.get_token()
        output_dir = "backups"

        self.api_handler = CanvasAPIHandler(base_url, api_token)
        self.backup_runner = BackupRunner(self.api_handler, output_dir)

        total_items = len(self.table.get_children())
        completed_items = 0

        for item in self.table.get_children():
            course_name = self.table.item(item)['values'][0]
            course_id = self.table.item(item)['values'][1]

            if item in self.interrupted_items:
                self.table.item(item, values=(course_name, course_id, "Resuming", "0%"))
            else:
                self.table.item(item, values=(course_name, course_id, "Backing up", "0%"))
            self.main_interface.root.update()

            try:
                success = self.backup_runner.run_backup(course_name, course_id, self.status_callback)
                if success:
                    self.table.item(item, values=(course_name, course_id, "Completed", "100%"))
                else:
                    self.table.item(item, values=(course_name, course_id, "Failed", "Error"))

                if item in self.interrupted_items:
                    self.interrupted_items.remove(item)

            except Exception as e:
                self.table.item(item, values=(course_name, course_id, "Failed", "Error"))
                messagebox.showerror("Backup Error", f"An error occurred while backing up {course_name}: {e}")
            finally:
                completed_items += 1

        self.is_running = False
        self.main_interface.start_button.config(state="normal")
        self.main_interface.retry_button.config(state="normal")
        self.main_interface.stop_button.config(state="disabled")

    def status_callback(self, course_name, status, progress):
        for item in self.table.get_children():
            if self.table.item(item)['values'][0] == course_name:
                self.table.item(item, values=(course_name, status, f"{progress}%"))
                self.main_interface.root.update()

    def retry_failed(self):
        for item in self.table.get_children():
            if self.table.item(item)['values'][2] == "Failed":
                self.table.item(item, values=(self.table.item(item)['values'][0], self.table.item(item)['values'][1], "Pending", "0%"))
        self.start_backup()

    def stop_backup(self):
        if self.is_running:
            messagebox.showinfo("Stop Backup", "Backup process stopped by user.")
        self.is_running = False
        self.main_interface.start_button.config(state="normal")
        self.main_interface.retry_button.config(state="normal")
        self.main_interface.stop_button.config(state="disabled")
