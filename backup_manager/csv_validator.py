import csv
import logging
from urllib.parse import urlparse

class CSVValidator:
    def __init__(self, filepath: str, expected_domain: str = None):
        self.filepath = filepath
        self.expected_domain = expected_domain  # e.g., "canvas.instructure.com"

    def validate(self) -> tuple[bool, str]:
        """Returns (is_valid, error_message)"""
        try:
            with open(self.filepath, "r", encoding="utf-8-sig") as csvfile:
                reader = csv.reader(csvfile)
                
                # Validate header
                header = next(reader, None)
                if not header or [col.strip() for col in header[:2]] != ["Course Name", "Course URL"]:
                    return False, "Invalid CSV structure. First two columns must be 'Course Name' and 'Course Link'"

                # Validate rows
                for row_num, row in enumerate(reader, start=2):
                    if len(row) < 2:
                        return False, f"Row {row_num}: Missing columns"
                        
                    course_name, course_url = row[0].strip(), row[1].strip()
                    
                    # Validate URL format
                    if not course_url.startswith(("http://", "https://")):
                        return False, f"Row {row_num}: Invalid URL format"
                        
                    # Optional: Validate domain match
                    if self.expected_domain:
                        parsed = urlparse(course_url)
                        if parsed.netloc != self.expected_domain:
                            return False, f"Row {row_num}: URL domain must be {self.expected_domain}"

                return True, "CSV validation successful"

        except FileNotFoundError:
            return False, f"File not found: {self.filepath}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"