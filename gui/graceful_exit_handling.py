import tkinter as tk
from tkinter import messagebox
import asyncio
import logging

class GracefulExitApp:
    def __init__(self, root, runner):
        self.root = root
        self.runner = runner  # Reference to the BackupRunner instance
        self.tasks_running = False

        # Override the close protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_task(self):
        """Start a simulated long-running task."""
        self.tasks_running = True
        logging.info("Starting a task.")
        asyncio.create_task(self.simulated_task())

    async def simulated_task(self):
        """Simulated long-running task."""
        try:
            for i in range(10):
                if self.runner.stop_event.is_set():
                    logging.info("Task stopped early.")
                    return
                logging.info(f"Task progress: {i + 1}/10")
                await asyncio.sleep(1)  # Simulate work
        finally:
            logging.info("Task completed.")
            self.tasks_running = False

    def on_close(self):
        """Handle application close event."""
        if self.tasks_running:
            if not messagebox.askyesno("Exit", "Tasks are running. Are you sure you want to exit?"):
                return

        # Stop all tasks gracefully
        logging.info("Stopping tasks and exiting.")
        self.runner.stop_event.set()
        self.root.destroy()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    root = tk.Tk()
    root.title("Graceful Exit App")

    # Simulated BackupRunner with a stop event
    class MockRunner:
        def __init__(self):
            self.stop_event = asyncio.Event()

    runner = MockRunner()
    app = GracefulExitApp(root, runner)

    # Create a start button for testing
    start_button = tk.Button(root, text="Start Task", command=app.start_task)
    start_button.pack(pady=20)

    root.mainloop()
