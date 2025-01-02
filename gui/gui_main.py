# File: gui_main.py

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QProgressBar, QTableWidget, QTableWidgetItem, QFileDialog, QWidget

class BackupManagerGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Course Backup Manager")
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()

    def init_ui(self):
        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()

        # Labels
        self.label_csv = QLabel("Select CSV File:")
        self.layout.addWidget(self.label_csv)

        # Buttons
        self.btn_select_csv = QPushButton("Browse CSV")
        self.btn_select_csv.clicked.connect(self.select_csv_file)
        self.layout.addWidget(self.btn_select_csv)

        self.btn_start_backup = QPushButton("Start Backup")
        self.layout.addWidget(self.btn_start_backup)

        # Table for displaying courses
        self.course_table = QTableWidget()
        self.course_table.setColumnCount(3)
        self.course_table.setHorizontalHeaderLabels(["Course Name", "Status", "Retry"])
        self.layout.addWidget(self.course_table)

        # Progress Bars
        self.overall_progress = QProgressBar()
        self.overall_progress.setValue(0)
        self.layout.addWidget(self.overall_progress)

        # Set layout
        self.central_widget.setLayout(self.layout)

    def select_csv_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_name:
            self.label_csv.setText(f"Selected File: {file_name}")

# Start GUI
def start_gui():
    app = QApplication(sys.argv)
    main_window = BackupManagerGUI()
    main_window.show()
    sys.exit(app.exec_())
