# File: gui/csv_handler.py

import csv
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
                    required_headers = ["course name", "course link"]

                    if not all(header in headers for header in required_headers):
                        raise ValueError("The selected file does not have the required columns: 'Course Name' and 'Course Link'. Please check the file and try again.")

                    # Clear and populate the table
                    self.main_interface.table.delete(*self.main_interface.table.get_children())
                    for row in reader:
                        self.main_interface.table.insert("", "end", values=(row["Course Name"], "Pending", "0%"))

                    self.main_interface.csv_label.config(text=file_path)
                    self.main_interface.start_button.config(state="normal")
            except ValueError as ve:
                messagebox.showerror("CSV Error", str(ve))
            except Exception as e:
                messagebox.showerror("CSV Error", f"An unexpected error occurred: {e}")
        else:
            messagebox.showerror("File Selection Error", "No file was selected. Please choose a valid CSV file.")
