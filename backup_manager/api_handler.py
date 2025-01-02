
import logging
import time
import requests

class CanvasAPIHandler:
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}"
        }

    def make_request(self, endpoint: str, method: str = "GET", params: dict = None, data: dict = None):
        """Reusable function for making API calls."""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            else:
                raise ValueError("Unsupported HTTP method")

            if response.status_code == 429:  # Rate limiting
                logging.warning("Rate limit reached, retrying after a delay...")
                time.sleep(1)  # Wait before retrying
                return self.make_request(endpoint, method, params, data)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logging.error(f"API Request failed: {e}")
            raise

    def validate_token(self):
        """Validates the provided API token by calling a test endpoint."""
        try:
            user_info = self.make_request("/api/v1/users/self")
            logging.info(f"Token validated. Logged in as: {user_info.get('name')} ({user_info.get('email')})")
            return True
        except Exception as e:
            logging.error(f"Token validation failed: {e}")
            return False


    def fetch_course_details(self, course_url: str):
        """Fetches the course name and ID from a given Canvas course URL."""
        try:
            # Extract course ID from the URL
            course_id = course_url.split("/courses/")[-1]
            endpoint = f"/api/v1/courses/{course_id}"
            course_data = self.make_request(endpoint)

            course_name = course_data.get("name", "Unknown Course")
            logging.info(f"Fetched course details: {course_name} (ID: {course_id})")
            return {"course_name": course_name, "course_id": course_id}

        except Exception as e:
            logging.error(f"Failed to fetch course details for URL {course_url}: {e}")
            return None