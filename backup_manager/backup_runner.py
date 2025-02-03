import asyncio
import os
import logging
import time
from datetime import datetime
import aiohttp
import aiofiles
from backup_manager.api_handler import CanvasAPIHandler
from backup_manager.system_compat import configure_platform_settings

class BackupRunner:
    def __init__(self, api_handler: CanvasAPIHandler, output_dir: str, stop_event: asyncio.Event, concurrency_limit: int = 5):
        self.api_handler = api_handler
        self.output_dir = output_dir
        self.stop_event = stop_event  # Add stop event
        self.concurrency_limit = concurrency_limit
        self.semaphore = asyncio.Semaphore(concurrency_limit)

        # Configure platform-specific settings on initialization
        configure_platform_settings()

    async def run_backup(self, course_name: str, course_id: str, status_callback=None):
        try:
            if status_callback:
                if asyncio.iscoroutinefunction(status_callback):
                    await status_callback(course_name, course_id, "Backing up", 0)
                else:
                    status_callback(course_name, course_id, "Backing up", 0)

            logging.info(f"Starting export for course: {course_name} (ID: {course_id})")
            export_id = await self.trigger_course_export(course_id)

            export_url = await self.poll_export_status(course_id, export_id, status_callback, course_name)
            if not export_url:
                logging.error(f"Export failed for course: {course_name} (ID: {course_id})")
                if status_callback:
                    if asyncio.iscoroutinefunction(status_callback):
                        await status_callback(course_name, course_id, "Failed", 0)
                    else:
                        status_callback(course_name, course_id, "Failed", 0)
                return False

            if status_callback:
                if asyncio.iscoroutinefunction(status_callback):
                    await status_callback(course_name, course_id, "Downloading", 0)
                else:
                    status_callback(course_name, course_id, "Downloading", 0)

            await self.download_backup(course_name, export_url, status_callback, course_id)
            await self.manage_backups(course_name)

            logging.info(f"Backup completed for course: {course_name} (ID: {course_id})")
            if status_callback:
                if self.stop_event.is_set():  # Check stop event
                    logging.info(f"Backup Stopped by User")
                    if asyncio.iscoroutinefunction(status_callback):
                        await status_callback(course_name, course_id, "Stopped", 0)
                    else:
                        status_callback(course_name, course_id, "Stopped", 0)
                else:
                    if asyncio.iscoroutinefunction(status_callback):
                        await status_callback(course_name, course_id, "Completed", 100)
                    else:
                        status_callback(course_name, course_id, "Completed", 100)
            return True

        except Exception as e:
            logging.error(f"Backup failed for course: {course_name} (ID: {course_id}): {e}")
            if status_callback:
                if asyncio.iscoroutinefunction(status_callback):
                    await status_callback(course_name, course_id, "Failed", 0)
                else:
                    status_callback(course_name, course_id, "Failed", 0)
            return False

    async def trigger_course_export(self, course_id: str):
        endpoint = f"/api/v1/courses/{course_id}/content_exports"

        # Make a GET request to check for existing content exports
        response = await self.api_handler.make_request(endpoint, method="GET")
        exports = response if isinstance(response, list) else response.get("content_exports", [])

        # Check if there is an export created today
        current_date = datetime.now().strftime("%Y-%m-%d")
        for export in exports:
            created_at = export.get("created_at", "")
            if created_at.startswith(current_date):
                logging.info(f"Found existing export for course ID: {course_id} created on {current_date}")
                return export.get("id")

        # If no export found for today, create a new one
        data = {"export_type": "common_cartridge"}
        response = await self.api_handler.make_request(endpoint, method="POST", data=data)
        return response.get("id")

    async def poll_export_status(self, course_id: str, export_id: str, status_callback, course_name):
        endpoint = f"/api/v1/courses/{course_id}/content_exports/{export_id}"
        response = await self.api_handler.make_request(endpoint)
        progress_url = response.get("progress_url")

        if not progress_url:
            logging.error(f"No progress URL found for course ID: {course_id}")
            return None

        for _ in range(600):  # Polling for up to 300 seconds (5 minutes)
            if self.stop_event.is_set():  # Check stop event
                logging.info(f"Backup stopped for course: {course_name} (ID: {course_id})")
                return None

            stripped_progress_url = progress_url.replace("https://byui.instructure.com", "")
            progress_response = await self.api_handler.make_request(stripped_progress_url)
            progress = progress_response.get("completion", 0)
            workflow_state = progress_response.get("workflow_state")

            if status_callback:
                if asyncio.iscoroutinefunction(status_callback):
                    await status_callback(course_name, course_id, "Backing up", progress)
                else:
                    status_callback(course_name, course_id, "Backing up", progress)

            logging.info(f"Polling progress status: {progress}% completed...")

            if workflow_state == "completed":
                final_response = await self.api_handler.make_request(endpoint)
                attachment = final_response.get("attachment")
                if attachment and "url" in attachment:
                    return attachment["url"]

            await asyncio.sleep(1)

        logging.error(f"Export timed out for course ID: {course_id}")
        return None

    async def download_backup(self, course_name: str, file_url: str, status_callback, course_id):
        timeout = aiohttp.ClientTimeout(total=3600)  # Set a timeout of 1 hour
        connector = aiohttp.TCPConnector(ssl=False)  # Disable SSL verification
        chunk_size = 1024 * 1024 # 1 MB chunk size
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(file_url) as response:
                response.raise_for_status()

                content_length = response.headers.get("Content-Length")
                total_size = int(content_length) if content_length and content_length.isdigit() else 0
                downloaded_size = 0

                course_dir = os.path.join(self.output_dir, course_name)
                os.makedirs(course_dir, exist_ok=True)

                timestamp = datetime.now().strftime("%Y-%m-%d")
                file_name = f"{course_name}_{timestamp}.zip"
                file_path = os.path.join(course_dir, file_name)

                async with aiofiles.open(file_path, "wb") as f:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        if chunk:
                            await f.write(chunk)
                            downloaded_size += len(chunk)
                            if status_callback and total_size > 0:
                                progress = int((downloaded_size / total_size) * 100)
                                if asyncio.iscoroutinefunction(status_callback):
                                    await status_callback(course_name, course_id, "Downloading", progress)
                                else:
                                    status_callback(course_name, course_id, "Downloading", progress)

                            if self.stop_event.is_set():  # Check stop event
                                logging.info(f"Download stopped for course: {course_name} (ID: {course_id})")
                                return

                logging.info(f"Downloaded backup: {file_path}")

    async def manage_backups(self, course_name: str):
        course_dir = os.path.join(self.output_dir, course_name)
        backups = sorted(
            [os.path.join(course_dir, f) for f in os.listdir(course_dir) if f.endswith(".zip")],
            key=os.path.getctime,
        )

        while len(backups) > 10:  # Retain only the 10 most recent backups
            oldest_backup = backups.pop(0)
            os.remove(oldest_backup)
            logging.info(f"Deleted old backup: {oldest_backup}")

    async def process_queue(self, queue: asyncio.Queue):
        """Process tasks from the queue concurrently with a concurrency limit."""
        async def worker():
            while not queue.empty():
                if self.stop_event.is_set():  # Check stop event
                    logging.info("Backup process stopped by user.")
                    break

                course_name, course_id, status_callback = await queue.get()
                async with self.semaphore:
                    await self.run_backup(course_name, course_id, status_callback)
                queue.task_done()

        # Create a list of worker tasks
        workers = [asyncio.create_task(worker()) for _ in range(self.concurrency_limit)]

        # Wait for all worker tasks to complete
        await asyncio.gather(*workers)