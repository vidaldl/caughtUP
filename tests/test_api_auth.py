from backup_manager.api_handler import CanvasAPIHandler
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Replace with your Canvas LMS base URL and API token
BASE_URL = "https://byui.instructure.com:443"
API_TOKEN = "##########"

if __name__ == "__main__":
    handler = CanvasAPIHandler(BASE_URL, API_TOKEN)
    if handler.validate_token():
        print("Token is valid!")
    else:
        print("Invalid token or authentication failed.")
