from backup_manager.csv_validator import CSVValidator

# Replace with the path to your test CSV file
CSV_FILEPATH = "ignore/test_courses.csv"

if __name__ == "__main__":
    validator = CSVValidator(CSV_FILEPATH)
    is_valid, message = validator.validate()
    
    print(message)
    if not is_valid:
        print("Validation failed.")
    else:
        print("Validation successful!")
