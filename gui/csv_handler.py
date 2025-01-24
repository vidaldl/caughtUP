# File: gui/csv_handler.py

import csv
import re
from tkinter import filedialog, messagebox
from backup_manager.csv_validator import CSVValidator
from urllib.parse import urlparse

class CSVHandler:
    def __init__(self, main_interface):
        self.main_interface = main_interface
        self.canvas_domain = urlparse(self.main_interface.token_manager.base_url).netloc  # Get domain from config
        self.canvas_domain = self.canvas_domain.replace(":443", "")  # Normalize domain


    def browse_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=(
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            )
        )
        if not file_path:
            return
        try:
            # Validate CSV first
            validator = CSVValidator(file_path, self.canvas_domain)
            is_valid, error_msg = validator.validate()
            
            if not is_valid:
                raise ValueError(error_msg)  # Will be caught below
            
            # Process valid CSV
            with open(file_path, "r", encoding="utf-8-sig") as csv_file:
                reader = csv.DictReader(csv_file)
                # Clear and populate the table
                self.main_interface.table.delete(*self.main_interface.table.get_children())
                for row in reader:
                    course_name = row["Course Name"]
                    course_url = row["Course URL"]
                    course_id = self.extract_course_id(course_url)
                    if course_id:
                        self.main_interface.table.insert("", "end", values=(course_name, course_id, "Pending", "0%"))
                    else:
                        raise ValueError(f"Invalid course URL: {course_url}")

                self.main_interface.csv_label.config(text=file_path)
                self.main_interface.start_button.config(state="normal")
        except ValueError as ve:
            messagebox.showerror("CSV Error", str(ve))
        except Exception as e:
            messagebox.showerror("CSV Error", f"An unexpected error occurred: {e}")

    def extract_course_id(self, course_url):
        match = re.search(r'/courses/(\d+)', course_url)
        if match:
            return match.group(1)
        return None
