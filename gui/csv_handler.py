import csv
import re
import logging
from tkinter import filedialog, messagebox, ttk, Toplevel, Text, Frame, Scrollbar, END
from urllib.parse import urlparse
from backup_manager.csv_validator import CSVValidator

class CSVHandler:
    def __init__(self, main_interface):
        self.main_interface = main_interface
        self.canvas_domain = self._get_canvas_domain()

    def _get_canvas_domain(self):
        """Extracts domain from configured base URL"""
        if hasattr(self.main_interface, 'token_manager') and self.main_interface.token_manager.base_url:
            url = urlparse(self.main_interface.token_manager.base_url).netloc
            clearedURL = url.replace(":443", "")
            print(clearedURL)
            return  clearedURL # Remove port if present
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
            is_valid, error_msg, sanitized_rows, duplicateCourses = validator.validate_and_sanitize()
            
            if not is_valid:
                raise ValueError(error_msg)

            # Clear existing data and populate new
            self.main_interface.table.delete(*self.main_interface.table.get_children())
            self.main_interface.current_data = [
                {
                    "sanitized_name": row["sanitized_name"],
                    "course_id": row["course_id"],
                    "status": "Pending",
                    "progress": "0%"
                }
                for row in sanitized_rows
            ]

            # Show summary and update UI
            self._show_import_summary(len(sanitized_rows), duplicateCourses)
            self.main_interface.csv_label.config(text=file_path)
            self.main_interface.start_button.config(state="normal")
            self.main_interface._refresh_table()

        except ValueError as ve:
            messagebox.showerror("CSV Error", str(ve))
        except Exception as e:
            logging.error(f"CSV handling error: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Unexpected error: {e}")

    def _show_import_summary(self, imported_count: int, duplicate_courses: list):
        """Displays post-import statistics with duplicate details"""
        summary_window = Toplevel(self.main_interface.root)
        summary_window.title("Import Summary")
        summary_window.geometry("600x400")

        # Main container
        container = ttk.Frame(summary_window)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Summary text
        summary_text = f"• Successfully imported {imported_count} courses\n" \
                      f"• Removed {len(duplicate_courses)} duplicates"
        ttk.Label(container, text=summary_text).pack(anchor="w", pady=(0, 10))

        # Duplicates list
        duplicates_frame = ttk.Frame(container)
        duplicates_frame.pack(fill="both", expand=True)

        # Text widget with scrollbar
        text_box = Text(duplicates_frame, wrap="none", state="disabled", font=('TkDefaultFont', 10))
        scrollbar = ttk.Scrollbar(duplicates_frame, orient="vertical", command=text_box.yview)
        text_box.configure(yscrollcommand=scrollbar.set)

        # Layout
        text_box.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        duplicates_frame.grid_rowconfigure(0, weight=1)
        duplicates_frame.grid_columnconfigure(0, weight=1)

        # Populate duplicates
        text_box.config(state="normal")
        if duplicate_courses:
            text_box.insert(END, "Duplicate courses:\n\n")
            for course in duplicate_courses:
                text_box.insert(END, f"[Row {course[0]}] - {course[1]} - {course[2]}\n")
        else:
            text_box.insert(END, "No duplicate courses found")
        text_box.config(state="disabled")

        # OK button
        ttk.Button(container, text="OK", command=summary_window.destroy).pack(pady=(10, 0))

        # Window configuration
        summary_window.minsize(400, 300)
        container.pack_propagate(0)