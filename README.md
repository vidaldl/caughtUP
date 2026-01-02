# Course Backup Manager for Canvas LMS

## Overview

The Course Backup Manager is a tool designed to automate the backup of course content from Canvas LMS. It provides a graphical user interface (GUI) to manage and automate the backup process, ensuring that course content is safely stored and easily accessible.

## Features

- **CSV Upload**: Upload a CSV file containing course names and URLs.
- **Token Management**: Manage API tokens for authentication with Canvas LMS.
- **Course Backup**: Trigger course content exports from Canvas, download the exported content, and manage the backups.
- **Progress Tracking**: Display the progress of each course backup and overall progress.
- **Retry Mechanism**: Retry failed backups.
- **Configuration Management**: Change the default backup folder and save configurations.


## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/vidaldl/caughtUP.git
    cd CaughtUP
    ```

2. **Create and activate a virtual environment**:
    ```sh
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. **Install the required packages**:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. **Run the application**:
    ```sh
    python main.py
    ```

2. **Upload CSV**:
    - Click on the "Upload CSV" button and select the CSV file containing course names and URLs.

3. **Manage API Token**:
    - Enter your Canvas LMS API token in the provided field.

4. **Start Backup**:
    - Click on the "Start Backup" button to begin the backup process.
    - Monitor the progress in the progress bar and table view.

5. **Retry Failed Backups**:
    - If any backups fail, click on the "Retry Failed" button to retry them.

6. **Change Backup Folder**:
    - Click on the "File" button and then on "Change Default Backup Folder" to change the default backup folder.

## Configuration

- **Default Backup Folder**: The default folder where backups are stored can be changed in File->Change Default Backup Folder.
- **API Base URL**: The base URL for the Canvas LMS API can be configured in the settings.

## Logging

- Logs are stored in the `logs/` directory. You can view detailed logs for troubleshooting.


## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

