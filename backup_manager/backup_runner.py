import os
import logging
import time
from datetime import datetime
from backup_manager.api_handler import CanvasAPIHandler
import requests

class BackupRunner:
    def __init__(self, api_handler: CanvasAPIHandler, output_dir: str):
        self.api_handler = api_handler
        self.output_dir = output_dir

    def run_backup(self, course_name: str, course_id: str, status_callback=None):
        try:
            if status_callback:
                status_callback(course_name, "Backing up", 0)

            logging.info(f"Starting export for course: {course_name} (ID: {course_id})")
            export_id = self.trigger_course_export(course_id)

            export_url = self.poll_export_status(course_id, export_id, status_callback, course_name)
            if not export_url:
                logging.error(f"Export failed for course: {course_name} (ID: {course_id})")
                if status_callback:
                    status_callback(course_name, "Failed", 0)
                return False

            if status_callback:
                status_callback(course_name, "Downloading", 0)

            self.download_backup(course_name, export_url, status_callback)
            self.manage_backups(course_name)

            logging.info(f"Backup completed for course: {course_name} (ID: {course_id})")
            if status_callback:
                status_callback(course_name, "Completed", 100)
            return True

        except Exception as e:
            logging.error(f"Backup failed for course: {course_name} (ID: {course_id}): {e}")
            if status_callback:
                status_callback(course_name, "Failed", 0)
            return False

    def trigger_course_export(self, course_id: str):
        endpoint = f"/api/v1/courses/{course_id}/content_exports"
        
        # Get the current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Make a GET request to check for existing content exports
        response = self.api_handler.make_request(endpoint, method="GET")
        exports = response if isinstance(response, list) else response.get("content_exports", [])
        
        # Check if there is an export created today
        for export in exports:
            created_at = export.get("created_at", "")
            if created_at.startswith(current_date):
                logging.info(f"Found existing export for course ID: {course_id} created on {current_date}")
                return export.get("id")
        
        # If no export found for today, create a new one
        data = {"export_type": "common_cartridge"}
        response = self.api_handler.make_request(endpoint, method="POST", data=data)
        return response.get("id")

    def poll_export_status(self, course_id: str, export_id: str, status_callback, course_name):
        endpoint = f"/api/v1/courses/{course_id}/content_exports/{export_id}"
        response = self.api_handler.make_request(endpoint)
        progress_url = response.get("progress_url")

        if not progress_url:
            logging.error(f"No progress URL found for course ID: {course_id}")
            return None

        for _ in range(300):  # Polling for up to 300 seconds (5 minutes)
            stripped_progress_url = progress_url.replace("https://byui.instructure.com", "")
            progress_response = self.api_handler.make_request(stripped_progress_url)
            progress = progress_response.get("completion", 0)
            workflow_state = progress_response.get("workflow_state")

            if status_callback:
                status_callback(course_name, "Backing up", progress)

            logging.info(f"Polling progress status: {progress}% completed...")

            if workflow_state == "completed":
                final_response = self.api_handler.make_request(endpoint)
                attachment = final_response.get("attachment")
                if attachment and "url" in attachment:
                    file_url = attachment["url"]
                    return file_url

            time.sleep(1)

        logging.error(f"Export timed out for course ID: {course_id}")
        return None

    def download_backup(self, course_name: str, file_url: str, status_callback):
        response = requests.get(file_url, stream=True)
        response.raise_for_status()

        content_length = response.headers.get("Content-Length")
        total_size = int(content_length) if content_length and content_length.isdigit() else 0
        downloaded_size = 0

        course_dir = os.path.join(self.output_dir, course_name)
        os.makedirs(course_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d")
        file_name = f"{course_name}_{timestamp}.zip"
        file_path = os.path.join(course_dir, file_name)

        try:
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if status_callback and total_size > 0:
                            progress = int((downloaded_size / total_size) * 100)
                            status_callback(course_name, "Downloading", progress)
        except Exception as e:
            logging.error(f"Download interrupted for course: {course_name}. Error: {e}")
            if os.path.exists(file_path):
                os.remove(file_path)
            raise

        logging.info(f"Downloaded backup: {file_path}")

    def manage_backups(self, course_name: str):
        course_dir = os.path.join(self.output_dir, course_name)
        backups = sorted(
            [os.path.join(course_dir, f) for f in os.listdir(course_dir) if f.endswith(".zip")],
            key=os.path.getctime,
        )

        while len(backups) > 10:
            oldest_backup = backups.pop(0)
            os.remove(oldest_backup)
            logging.info(f"Deleted old backup: {oldest_backup}")
