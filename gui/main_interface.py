import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
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

        # Add the menu bar
        self.menu_bar = MenuBar(root, token_manager)

        # Create the main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # CSV upload section
        self.csv_frame = ttk.Frame(self.main_frame)
        self.csv_frame.pack(fill=tk.X, pady=10)

        self.browse_button = ttk.Button(
            self.csv_frame, text="Browse CSV", command=self.browse_csv
        )
        self.browse_button.pack(side=tk.LEFT, padx=5)

        self.csv_label = ttk.Label(
            self.csv_frame, text="No file selected", anchor="w"
        )
        self.csv_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Course table section
        self.table_frame = ttk.Frame(self.main_frame)
        self.table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.table = ttk.Treeview(
            self.table_frame, columns=("Course Name", "Status", "Progress"), show="headings"
        )
        self.table.heading("Course Name", text="Course Name")
        self.table.heading("Status", text="Status")
        self.table.heading("Progress", text="Progress")

        self.table.column("Course Name", anchor=tk.W, width=300, stretch=True)
        self.table.column("Status", anchor=tk.CENTER, width=150, stretch=True)
        self.table.column("Progress", anchor=tk.CENTER, width=150, stretch=True)

        # Add scrollbars for the table
        self.table_scroll_y = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.table.yview)
        self.table_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.table_scroll_x = ttk.Scrollbar(self.table_frame, orient=tk.HORIZONTAL, command=self.table.xview)
        self.table_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.table.configure(yscrollcommand=self.table_scroll_y.set, xscrollcommand=self.table_scroll_x.set)
        self.table.pack(fill=tk.BOTH, expand=True)

        # Control panel section
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=10)

        self.start_button = ttk.Button(
            self.control_frame, text="Start Backup", command=self.start_backup
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.start_button.config(state=tk.DISABLED)  # Disable initially

        self.retry_button = ttk.Button(
            self.control_frame, text="Retry Failed", command=self.retry_failed
        )
        self.retry_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(
            self.control_frame, text="Stop", command=self.stop_backup
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Overall progress bar
        self.progress_frame = ttk.Frame(self.main_frame)
        self.progress_frame.pack(fill=tk.X, pady=10)

        self.progress_label = ttk.Label(
            self.progress_frame, text="Overall Progress", anchor="w"
        )
        self.progress_label.pack(side=tk.LEFT, padx=5)

        self.overall_progress = ttk.Progressbar(
            self.progress_frame, mode="determinate"
        )
        self.overall_progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

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
                with open(file_path, "r", encoding="utf-8") as csv_file:
                    reader = csv.DictReader(csv_file)
                    if "Course Name" not in reader.fieldnames or "Course Link" not in reader.fieldnames:
                        raise ValueError("The selected file does not have the required columns: 'Course Name' and 'Course Link'. Please check the file and try again.")

                    self.clear_table()
                    for row in reader:
                        self.table.insert("", tk.END, values=(row["Course Name"], "Pending", "0%"))

                    self.csv_label.config(text=file_path)
                    self.start_button.config(state=tk.NORMAL)  # Enable start button
            except FileNotFoundError:
                messagebox.showerror("CSV Error", "The selected file could not be found. Please try again.")
            except ValueError as ve:
                messagebox.showerror("CSV Error", str(ve))
            except Exception as e:
                messagebox.showerror("CSV Error", f"An unexpected error occurred: {e}")
        else:
            messagebox.showerror("File Selection Error", "No file was selected. Please choose a valid CSV file.")

    def clear_table(self):
        for item in self.table.get_children():
            self.table.delete(item)

    def start_backup(self):
        # Placeholder for backup functionality
        if self.csv_label.cget("text") == "No file selected":
            messagebox.showerror("Start Backup Error", "Please select a CSV file before starting the backup.")
        else:
            self.start_button.config(state=tk.DISABLED)  # Disable start button during backup
            messagebox.showinfo("Start Backup", "Backup process started.")

    def retry_failed(self):
        # Placeholder for retry functionality
        messagebox.showinfo("Retry Failed", "Retrying failed backups.")

    def stop_backup(self):
        # Placeholder for stop functionality
        messagebox.showinfo("Stop Backup", "Backup process stopped.")
        self.start_button.config(state=tk.NORMAL)  # Re-enable start button
