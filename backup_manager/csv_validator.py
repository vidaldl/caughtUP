import csv
import logging

class CSVValidator:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def validate(self):
        """Validates the structure and content of the CSV file."""
        try:
            with open(self.filepath, "r", encoding="utf-8-sig") as csvfile:
                reader = csv.reader(csvfile)

                # Check header
                header = next(reader, None)
                if not header or len(header) < 2 or header[:2] != ["Course Name", "Course Link"]:
                    logging.error("CSV validation failed: Incorrect header structure.")
                    return False, "Invalid CSV structure. Expected 'Course Name' and 'Course Link' columns."

                # Validate rows
                for row_num, row in enumerate(reader, start=2):
                    if len(row) < 2 or not row[1].startswith("http"):
                        logging.error(f"CSV validation failed: Invalid row {row_num}: {row}")
                        return False, f"Invalid row at line {row_num}: {row}. Ensure all rows have a valid course link."

            logging.info("CSV validation passed.")
            return True, "CSV validation successful."

        except FileNotFoundError:
            logging.error(f"CSV file not found: {self.filepath}")
            return False, f"File not found: {self.filepath}."
        except Exception as e:
            logging.error(f"Unexpected error during CSV validation: {e}")
            return False, f"Unexpected error: {e}"
