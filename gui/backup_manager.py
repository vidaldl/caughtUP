import time
from tkinter import messagebox

class BackupManager:
    def __init__(self, main_interface, table):
        self.main_interface = main_interface
        self.table = table
        self.is_running = False
        self.interrupted_items = set()

    def start_backup(self):
        if self.is_running:
            return

        self.is_running = True
        self.main_interface.start_button.config(state="disabled")
        self.main_interface.retry_button.config(state="disabled")
        self.main_interface.stop_button.config(state="normal")

        total_items = len(self.table.get_children())
        completed_items = 0

        for item in self.table.get_children():
            if item in self.interrupted_items:
                self.table.item(item, values=(self.table.item(item)['values'][0], "Resuming", "0%"))
            else:
                self.table.item(item, values=(self.table.item(item)['values'][0], "Backing up", "0%"))
            self.main_interface.root.update()

            try:
                # Simulate backup process
                for progress in range(1, 101, 10):
                    if not self.is_running:
                        self.interrupted_items.add(item)
                        raise Exception("Backup interrupted")

                    time.sleep(0.1)  # Simulate work
                    self.table.item(item, values=(
                        self.table.item(item)['values'][0],
                        "Backing up",
                        f"{progress}%"
                    ))
                    self.main_interface.overall_progress['value'] = (
                        (completed_items / total_items * 100) + (progress / total_items)
                    )
                    self.main_interface.root.update()

                # Mark as completed
                self.table.item(item, values=(
                    self.table.item(item)['values'][0],
                    "Completed",
                    "100%"
                ))
                if item in self.interrupted_items:
                    self.interrupted_items.remove(item)

            except Exception as e:
                self.table.item(item, values=(
                    self.table.item(item)['values'][0],
                    "Failed",
                    "Error"
                ))
                messagebox.showerror("Backup Error", f"An error occurred while backing up {self.table.item(item)['values'][0]}: {e}")
            finally:
                completed_items += 1

        self.is_running = False
        self.main_interface.start_button.config(state="normal")
        self.main_interface.retry_button.config(state="normal")
        self.main_interface.stop_button.config(state="disabled")

    def retry_failed(self):
        for item in self.table.get_children():
            if self.table.item(item)['values'][1] == "Failed":
                self.table.item(item, values=(self.table.item(item)['values'][0], "Pending", "0%"))
        self.start_backup()

    def stop_backup(self):
        if self.is_running:
            messagebox.showinfo("Stop Backup", "Backup process stopped by user.")
        self.is_running = False
        self.main_interface.start_button.config(state="normal")
        self.main_interface.retry_button.config(state="normal")
        self.main_interface.stop_button.config(state="disabled")
