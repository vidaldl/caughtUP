# File: gui_main.py

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QProgressBar, QTableWidget, QTableWidgetItem, QFileDialog, QWidget
import csv
from backup_manager.api_handler import CanvasAPIHandler
from backup_manager.backup_runner import BackupRunner

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
        self.btn_start_backup.clicked.connect(self.start_backup)
        self.layout.addWidget(self.btn_start_backup)

        # Table for displaying courses
        self.course_table = QTableWidget()
        self.course_table.setColumnCount(3)
        self.course_table.setHorizontalHeaderLabels(["Course Name", "Course ID", "Status"])
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
            self.load_courses(file_name)

    def load_courses(self, file_name):
        with open(file_name, "r", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)
            self.course_table.setRowCount(0)
            for row in reader:
                row_position = self.course_table.rowCount()
                self.course_table.insertRow(row_position)
                self.course_table.setItem(row_position, 0, QTableWidgetItem(row["Course Name"]))
                self.course_table.setItem(row_position, 1, QTableWidgetItem(row["Course ID"]))
                self.course_table.setItem(row_position, 2, QTableWidgetItem("Pending"))

    def start_backup(self):
        base_url = "https://<institution>.instructure.com:443"
        api_token = "<your_api_token>"
        output_dir = "backups"

        api_handler = CanvasAPIHandler(base_url, api_token)
        backup_runner = BackupRunner(api_handler, output_dir)

        for row in range(self.course_table.rowCount()):
            course_name = self.course_table.item(row, 0).text()
            course_id = self.course_table.item(row, 1).text()
            success = backup_runner.run_backup(course_name, course_id, self.status_callback)
            if success:
                self.course_table.setItem(row, 2, QTableWidgetItem("Completed"))
            else:
                self.course_table.setItem(row, 2, QTableWidgetItem("Failed"))

    def status_callback(self, course_name, status, progress):
        for row in range(self.course_table.rowCount()):
            if self.course_table.item(row, 0).text() == course_name:
                self.course_table.setItem(row, 2, QTableWidgetItem(f"{status} ({progress}%)"))

# Start GUI
def start_gui():
    app = QApplication(sys.argv)
    main_window = BackupManagerGUI()
    main_window.show()
    sys.exit(app.exec_())
