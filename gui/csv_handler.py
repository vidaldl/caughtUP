import csv
import re
import logging
from tkinter import filedialog, messagebox, ttk, END, Text, Toplevel
from backup_manager.csv_validator import CSVValidator
from urllib.parse import urlparse

class CSVHandler:
    def __init__(self, main_interface):
        self.main_interface = main_interface
        self.canvas_domain = self._get_canvas_domain()

    def _get_canvas_domain(self):
        """Extracts domain from configured base URL"""
        if hasattr(self.main_interface, 'token_manager'):
            url = urlparse(self.main_interface.token_manager.base_url).netloc
            return url.replace(":443", "") if url else None
        return None

    def browse_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
        )
        if not file_path:
            return

        try:
            # Validate and sanitize CSV
            validator = CSVValidator(file_path, self.canvas_domain)
            is_valid, error_msg, sanitized_rows, duplicate_courses = validator.validate_and_sanitize()
            
            if not is_valid:
                raise ValueError(error_msg)

            # Clear existing table
            self.main_interface.table.delete(*self.main_interface.table.get_children())

            # Populate table with sanitized data
            duplicates_removed = len(duplicate_courses)
            for row in sanitized_rows:
                self.main_interface.table.insert("", "end", values=(
                    row["sanitized_name"],
                    row["course_id"],
                    "Pending",
                    "0%"
                ))

            # Show summary
            self._show_import_summary(len(sanitized_rows), duplicate_courses)
            self.main_interface.csv_label.config(text=file_path)
            self.main_interface.start_button.config(state="normal")

        except ValueError as ve:
            messagebox.showerror("CSV Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")

    def _show_import_summary(self, imported_count: int, duplicate_courses: list):
        """Displays post-import statistics with duplicate details in scrollable box"""
        # Create custom dialog window
        summary_window = Toplevel(self.main_interface.root)
        summary_window.title("Import Summary")
        summary_window.geometry("500x400")
        
        # Main container frame
        container = ttk.Frame(summary_window)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Summary text
        summary_text = f"Successfully imported {imported_count} courses\n" \
                      f"Removed {len(duplicate_courses)} duplicates"
                      
        ttk.Label(container, text=summary_text).pack(pady=(0, 10))

        # Create scrollable text box for duplicates
        duplicates_frame = ttk.Frame(container)
        duplicates_frame.pack(fill="both", expand=True)

        # Text widget with scrollbar
        text_box = Text(duplicates_frame, wrap="none", state="disabled")
        scrollbar = ttk.Scrollbar(duplicates_frame, orient="vertical", command=text_box.yview)
        text_box.configure(yscrollcommand=scrollbar.set)

        # Grid layout for proper scrollbar placement
        text_box.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        duplicates_frame.grid_rowconfigure(0, weight=1)
        duplicates_frame.grid_columnconfigure(0, weight=1)

        # Populate duplicates
        text_box.config(state="normal")
        if duplicate_courses:
            text_box.insert(END, "Duplicate courses:\n")
            for course in duplicate_courses:
                text_box.insert(END, f"Row {course[0]} - {course[1]} (ID: {course[2]})\n")
        else:
            text_box.insert(END, "No duplicate courses found")
        text_box.config(state="disabled")

        # OK button
        ttk.Button(container, text="OK", command=summary_window.destroy).pack(pady=(10, 0))

        # Make window resizable
        summary_window.minsize(400, 300)
        container.pack_propagate(0)