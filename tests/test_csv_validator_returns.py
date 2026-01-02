import csv
from backup_manager.csv_validator import CSVValidator


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def test_header_validation_returns_four_values(tmp_path):
    file = tmp_path / "bad.csv"
    write_csv(file, [["Wrong", "Header"], ["Course", "https://example.com/courses/1"]])
    validator = CSVValidator(str(file))
    result = validator.validate_and_sanitize()
    assert isinstance(result, tuple)
    assert len(result) == 4
    is_valid, message, sanitized, duplicates = result
    assert not is_valid
    assert sanitized == []
    assert duplicates == []


def test_duplicate_courses_returned(tmp_path):
    file = tmp_path / "dup.csv"
    write_csv(
        file,
        [
            ["Course Name", "Course URL"],
            ["A Course", "https://example.com/courses/1"],
            ["A Course Duplicate", "https://example.com/courses/1"],
        ],
    )
    validator = CSVValidator(str(file))
    is_valid, message, sanitized, duplicates = validator.validate_and_sanitize()
    assert is_valid
    assert len(sanitized) == 1
    assert duplicates == [[3, "A Course Duplicate", "1"]]
