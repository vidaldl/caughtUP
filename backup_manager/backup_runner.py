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

    def run_backup(self, course_name: str, course_id: str):
        try:
            logging.info(f"Starting export for course: {course_name} (ID: {course_id})")
            export_id = self.trigger_course_export(course_id)

            export_url = self.poll_export_status(course_id, export_id)
            if not export_url:
                logging.error(f"Export failed for course: {course_name} (ID: {course_id})")
                return False

            self.download_backup(course_name, export_url)
            self.manage_backups(course_name)

            logging.info(f"Backup completed for course: {course_name} (ID: {course_id})")
            return True

        except Exception as e:
            logging.error(f"Backup failed for course: {course_name} (ID: {course_id}): {e}")
            return False

    def trigger_course_export(self, course_id: str):
        endpoint = f"/api/v1/courses/{course_id}/content_exports"
        data = {"export_type": "common_cartridge"}
        response = self.api_handler.make_request(endpoint, method="POST", data=data)
        return response.get("id")

    def poll_export_status(self, course_id: str, export_id: str):
        endpoint = f"/api/v1/courses/{course_id}/content_exports/{export_id}"
        for _ in range(30):
            response = self.api_handler.make_request(endpoint)
            file_url = response.get("attachment", {}).get("url")

            if file_url:
                return file_url

            logging.info("Polling export status...")
            time.sleep(5)

        logging.error(f"Export timed out for course ID: {course_id}")
        return None

    def download_backup(self, course_name: str, file_url: str):
        response = requests.get(file_url, stream=True)
        response.raise_for_status()

        course_dir = os.path.join(self.output_dir, course_name)
        os.makedirs(course_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d")
        file_name = f"{course_name}_{timestamp}.zip"
        file_path = os.path.join(course_dir, file_name)

        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

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
