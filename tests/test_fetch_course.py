from backup_manager.api_handler import CanvasAPIHandler

# Replace with your Canvas LMS base URL and API token
BASE_URL = "https://byui.instructure.com:443/"
API_TOKEN = "####"
COURSE_URL = "https://byui.instructure.com/courses/328154"

if __name__ == "__main__":
    handler = CanvasAPIHandler(BASE_URL, API_TOKEN)
    course_details = handler.fetch_course_details(COURSE_URL)

    if course_details:
        print(f"Course Name: {course_details['course_name']}")
        print(f"Course ID: {course_details['course_id']}")
    else:
        print("Failed to fetch course details.")
