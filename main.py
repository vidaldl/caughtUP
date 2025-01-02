import logging
from logging.handlers import RotatingFileHandler
from gui.gui_main import start_gui

# Setup logging
def setup_logging():
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler = RotatingFileHandler("logs/app.log", maxBytes=5 * 1024 * 1024, backupCount=10)
    handler.setFormatter(log_formatter)
    handler.setLevel(logging.INFO)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    logging.info("Logging initialized.")

# Entry point for the application
if __name__ == "__main__":
    setup_logging()
    logging.info("Starting Course Backup Manager...")
    start_gui()
