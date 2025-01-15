# File: gui/csv_handler.py

import csv
import re
from tkinter import filedialog, messagebox

class CSVHandler:
    def __init__(self, main_interface):
        self.main_interface = main_interface

    def browse_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=(
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            )
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8-sig") as csv_file:
                    reader = csv.DictReader(csv_file)
                    headers = [header.strip().lower() for header in reader.fieldnames]
                    required_headers = ["course name", "course url"]

                    if not all(header in headers for header in required_headers):
                        raise ValueError("The selected file does not have the required columns: 'Course Name' and 'Course URL'. Please check the file and try again.")

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
        else:
            messagebox.showerror("File Selection Error", "No file was selected. Please choose a valid CSV file.")

    def extract_course_id(self, course_url):
        match = re.search(r'/courses/(\d+)', course_url)
        if match:
            return match.group(1)
        return None
