import asyncio
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
BASE_URL = "https://byui.instructure.com:443"
API_TOKEN = "10706~48ZV6PXZ6QBLum4yC9RF6Re8xnZJ43CCcffaE8GeQekDxcrrTczG7kJ4tn37fYGP"
OUTPUT_DIR = "backups"
COURSES = [
    {"name": "Course 1", "id": "160084"},
    {"name": "Course 2", "id": "276708"},
    {"name": "Course 3", "id": "320660"},
    {"name": "Course 4", "id": "332984"},
    {"name": "Course 5", "id": "275940"}
]

def status_callback(course_name, status, progress):
    """Simulates GUI updates for course backup status."""
    print(f"[{course_name}] Status: {status}, Progress: {progress}%")

async def main():
    api_handler = CanvasAPIHandler(BASE_URL, API_TOKEN)
    backup_runner = BackupRunner(api_handler, OUTPUT_DIR, concurrency_limit=5)

    queue = asyncio.Queue()

    # Populate the queue with courses
    for course in COURSES:
        queue.put_nowait((course["name"], course["id"], status_callback))

    # Process the queue
    await backup_runner.process_queue(queue)
    await api_handler.close_session()

if __name__ == "__main__":
    asyncio.run(main())