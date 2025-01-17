import asyncio
import logging
from aiohttp import ClientSession, ClientTimeout, TCPConnector

class CanvasAPIHandler:
    def __init__(self, base_url: str, api_token: str, concurrency_limit: int = 10):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}"
        }
        self.semaphore = asyncio.Semaphore(concurrency_limit)  # Concurrency control
        self.session = ClientSession(
            headers=self.headers, 
            timeout=ClientTimeout(total=30),
            connnector=TCPConnector(ssl=False)
            )

    async def make_request(self, endpoint: str, method: str = "GET", params: dict = None, data: dict = None):
        """Reusable function for making async API calls."""
        url = f"{self.base_url}{endpoint}"

        async with self.semaphore:  # Concurrency control
            await asyncio.sleep(0.09)  # Rate limiting (90ms delay)
            try:
                if method.upper() == "GET":
                    async with self.session.get(url, params=params) as response:
                        return await self._handle_response(response)
                elif method.upper() == "POST":
                    async with self.session.post(url, json=data) as response:
                        return await self._handle_response(response)
                else:
                    raise ValueError("Unsupported HTTP method")

            except Exception as e:
                logging.error(f"API Request failed: {e}")
                raise

    async def _handle_response(self, response):
        """Handle the API response, including retries for 429 errors."""
        if response.status == 429:  # Rate limiting
            retry_after = int(response.headers.get("Retry-After", 1))
            logging.warning(f"Rate limit reached. Retrying after {retry_after} seconds...")
            await asyncio.sleep(retry_after)
            return await self.make_request(response.url)

        response.raise_for_status()
        return await response.json()

    async def validate_token(self):
        """Validates the provided API token by calling a test endpoint."""
        try:
            user_info = await self.make_request("/api/v1/users/self")
            logging.info(f"Token validated. Logged in as: {user_info.get('name')} ({user_info.get('email')})")
            return True
        except Exception as e:
            logging.error(f"Token validation failed: {e}")
            return False

    async def fetch_course_details(self, course_url: str):
        """Fetches the course name and ID from a given Canvas course URL."""
        try:
            # Extract course ID from the URL
            course_id = course_url.split("/courses/")[-1]
            endpoint = f"/api/v1/courses/{course_id}"
            course_data = await self.make_request(endpoint)

            course_name = course_data.get("name", "Unknown Course")
            logging.info(f"Fetched course details: {course_name} (ID: {course_id})")
            return {"course_name": course_name, "course_id": course_id}

        except Exception as e:
            logging.error(f"Failed to fetch course details for URL {course_url}: {e}")
            return None

    async def close_session(self):
        """Closes the aiohttp session."""
        await self.session.close()
