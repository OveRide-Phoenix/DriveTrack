# DriveTrack

DriveTrack is a web application built with Flask that allows users to search for files in Google Drive using tags and other metadata.

## Features

- Search for files in Google Drive by tags, dates & other metadata.
- View search results with file details and links to Google Drive.
- Track and access file metadata in the application.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/OveRide-Phoenix/DriveTrack.git
   cd DriveTrack
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download and install MySQL Server:**
   - Visit the [MySQL website](https://www.mysql.com/) to download and install MySQL Server.
   - Follow the installation instructions for your operating system.

4. **Set up MySQL database:**
   - Create a new MySQL database for DriveTrack.
   - Configure the database connection in the `mysql_connector.py` file.

5. **Download and install Google Drive API credentials:**
   - Follow the instructions in the [Google Drive API documentation](https://developers.google.com/drive) to obtain credentials.
   - Save the credentials file as `credentials.json` in the project directory.

6. **Run the application:**
   ```bash
   python app.py
   ```
   The application will be accessible at `http://localhost:5000`.

## Usage

- Open the application in your web browser.
- Enter the Google Drive Link to the folder you want to search through (For Pre-processing)
- Use the search form to search for files by tags and dates.
- View the search results and click on file links to access files in Google Drive.
- Track and access file metadata in the application.

## Contributing

Contributions are welcome! Fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
