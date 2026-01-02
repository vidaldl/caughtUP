import csv
import logging
import re
from urllib.parse import urlparse
from typing import Tuple, List, Dict

class CSVValidator:
    def __init__(self, filepath: str, expected_domain: str = None):
        self.filepath = filepath
        self.expected_domain = expected_domain
        self.seen_course_ids = set()
        self.invalid_chars = re.compile(r'[<>:"/\\|?*]')  # Forbidden in filenames

    def validate_and_sanitize(self) -> Tuple[bool, str, List[Dict], List[Tuple[int, str, str]]]:
        """Validate a CSV file and produce sanitised course information.

        Returns:
            Tuple containing:
                - ``is_valid`` (bool): Whether validation succeeded.
                - ``message`` (str): Description of the validation outcome.
                - ``sanitized_rows`` (List[Dict]): Validated course rows with
                  sanitized names.
                - ``duplicate_courses`` (List[Tuple[int, str, str]]): Details of
                  any duplicate courses encountered as ``(row_num, name,
                  course_id)``.
        """
        try:
            with open(self.filepath, "r", encoding="utf-8-sig") as csvfile:
                reader = csv.DictReader(csvfile)
                sanitized_rows: List[Dict] = []
                duplicate_courses: List[Tuple[int, str, str]] = []

                # Validate header
                if not reader.fieldnames or [col.strip() for col in reader.fieldnames[:2]] != ["Course Name", "Course URL"]:
                    return False, "First two columns must be 'Course Name' and 'Course URL'", [], []

                # Process rows
                for row_num, row in enumerate(reader, start=2):
                    if len(row) < 2:
                        print(f"⚠ Warning: Skipping malformed row {row_num}: {row}")  # Debugging output
                        continue  # Skip bad rows instead of stopping execution

                    course_name = row.get("Course Name", "").strip()
                    course_url = row.get("Course URL", "").strip()
                    course_id = self._extract_course_id(course_url) if course_url else None
                    
                    if not course_id:
                        print(f"⚠ Warning: Skipping row {row_num} due to invalid Canvas course URL")
                        continue

                    # Check domain match
                    if self.expected_domain:
                        parsed = urlparse(course_url)
                        if parsed.netloc != self.expected_domain:
                            print(f"⚠ Warning: Row {row_num}: URL domain must be {self.expected_domain}")
                            continue

                    # Remove duplicates
                    if course_id in self.seen_course_ids:
                        duplicate_courses.append([row_num, course_name, course_id])
                        logging.warning(f"Duplicate course ID [{course_name}, {course_id}] skipped")
                        continue
                    self.seen_course_ids.add(course_id)

                    # Sanitize course name
                    sanitized_name = self._sanitize_folder_name(course_name)
                    if not sanitized_name:
                        sanitized_name = f"Course_{course_id}"  # Fallback

                    sanitized_rows.append({
                        "original_name": course_name,
                        "sanitized_name": sanitized_name,
                        "course_id": course_id
                    })

                if not sanitized_rows:
                    return False, "CSV contains no valid rows after sanitization", [], duplicate_courses

                return True, "CSV validated and sanitized", sanitized_rows, duplicate_courses

        except FileNotFoundError:
            return False, f"File not found: {self.filepath}", [], []
        except Exception as e:
            return False, f"Validation error: {str(e)}", [], []

    def _extract_course_id(self, url: str) -> str:
        """Extracts numeric course ID from URL"""
        match = re.search(r'/courses/(\d+)', url)
        return match.group(1) if match else None

    def _sanitize_folder_name(self, name: str) -> str:
        """Makes course name filesystem-safe"""
        # Remove invalid characters
        sanitized = self.invalid_chars.sub('_', name)
        # Trim whitespace and dots
        sanitized = sanitized.strip().strip('.')
        # Collapse multiple underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        return sanitized