import tkinter as tk
from tkinter import ttk

def create_table(parent):
    """Create and return a Treeview table with scrollbars."""
    table_frame = ttk.Frame(parent)
    table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    table = ttk.Treeview(
        table_frame, columns=("Course Name", "Status", "Progress"), show="headings"
    )
    table.heading("Course Name", text="Course Name")
    table.heading("Status", text="Status")
    table.heading("Progress", text="Progress")

    table.column("Course Name", anchor=tk.W, width=300, stretch=True)
    table.column("Status", anchor=tk.CENTER, width=150, stretch=True)
    table.column("Progress", anchor=tk.CENTER, width=150, stretch=True)

    # Add scrollbars for the table
    table_scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=table.yview)
    table_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    table_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=table.xview)
    table_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    table.configure(yscrollcommand=table_scroll_y.set, xscrollcommand=table_scroll_x.set)
    table.pack(fill=tk.BOTH, expand=True)

    return table

def create_progress_bar(parent):
    """Create and return a progress bar with its label."""
    progress_frame = ttk.Frame(parent)
    progress_frame.pack(fill=tk.X, pady=10)

    progress_label = ttk.Label(
        progress_frame, text="Overall Progress", anchor="w"
    )
    progress_label.pack(side=tk.LEFT, padx=5)

    overall_progress = ttk.Progressbar(
        progress_frame, mode="determinate"
    )
    overall_progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    return progress_label, overall_progress
