import tkinter as tk
from tkinter import ttk
from typing import Callable

def create_table(parent, filter_changed_callback: Callable = None) -> ttk.Treeview:
    """Create a table with sorting and filtering capabilities"""
    container = ttk.Frame(parent)
    container.pack(fill=tk.BOTH, expand=True)
    
    # Filter Entry
    filter_frame = ttk.Frame(container)
    filter_frame.pack(fill=tk.X, pady=(0, 5))
    
    ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT)
    filter_entry = ttk.Entry(filter_frame)
    filter_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    
    # Table with Scrollbars
    table_frame = ttk.Frame(container)
    table_frame.pack(fill=tk.BOTH, expand=True)
    
    columns = ("Course Name", "Course ID", "Status", "Progress")
    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        selectmode="extended"
    )
    
    # Configure columns
    col_config = {
        "Course Name": {"width": 300, "anchor": tk.W},
        "Course ID": {"width": 150, "anchor": tk.CENTER},
        "Status": {"width": 150, "anchor": tk.CENTER},
        "Progress": {"width": 150, "anchor": tk.CENTER}
    }
    
    for col, config in col_config.items():
        table.heading(col, text=col, 
                     command=lambda c=col: sort_column(table, c))
        table.column(col, **config)
    
    # Add scrollbars
    vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=table.yview)
    hsb = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=table.xview)
    table.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    # Grid layout
    table.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    
    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)
    
    # Bind filter entry
    if filter_changed_callback:
        filter_entry.bind("<KeyRelease>", 
                         lambda e: filter_changed_callback(filter_entry.get()))
    
    return table

def sort_column(table: ttk.Treeview, column: str):
    """Sort treeview by column, toggling between ascending/descending"""
    # Get current sort state
    current_sort = table.heading(column).get("direction", "")
    
    # Toggle direction
    new_sort = "desc" if current_sort == "asc" else "asc"
    
    # Update heading arrow
    table.heading(column, 
                 direction=new_sort,
                 image=get_sort_arrow(new_sort))
    
    # Sort the data
    data = [(table.set(child, column), child) 
           for child in table.get_children("")]
    
    # Numeric sorting for progress
    if column == "Progress":
        data.sort(key=lambda x: float(x[0].strip('%')), 
                 reverse=new_sort == "desc")
    else:
        data.sort(key=lambda x: x[0].lower(), 
                 reverse=new_sort == "desc")
    
    # Rearrange items
    for index, (_, child) in enumerate(data):
        table.move(child, "", index)

def get_sort_arrow(direction: str) -> tk.PhotoImage:
    """Generate sort direction arrows"""
    arrow = "↑" if direction == "asc" else "↓"
    photo = tk.PhotoImage(data=f"R0lGODlhCgAKAJEAAAAAAP///////yH5BAEAAAMALAAAAAAKAAoAAAIPnI8HygFiS4NlQABvFHwVADs=")
    return photo

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
