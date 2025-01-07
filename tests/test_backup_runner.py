from backup_manager.api_handler import CanvasAPIHandler
from backup_manager.backup_runner import BackupRunner
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Replace with your Canvas LMS base URL, API token, and course details
BASE_URL = "https://<INSTANCE>.instructure.com:443"
API_TOKEN = "<API Token>"
OUTPUT_DIR = "C:...Directory here"
COURSE_NAME = "Course Name"
COURSE_ID = "Course ID"

if __name__ == "__main__":
    api_handler = CanvasAPIHandler(BASE_URL, API_TOKEN)
    backup_runner = BackupRunner(api_handler, OUTPUT_DIR)
    
    success = backup_runner.run_backup(COURSE_NAME, COURSE_ID)
    if success:
        print(f"Backup completed for {COURSE_NAME}")
    else:
        print(f"Backup failed for {COURSE_NAME}")
