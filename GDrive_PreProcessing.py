import mysql.connector
import sys  # Import the sys module to access command-line arguments
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import datetime

# Connect to MySQL database
def connect_to_database():
    print("Connected to database")
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="mediagdrive"
    )
    

# Connect to Google Drive
def connect_to_google_drive():
    gauth = GoogleAuth()
    gauth.LoadClientConfigFile('D:/PROJECTS/NEW_MTAM/credentials.json')
    gauth.LocalWebserverAuth()
    return GoogleDrive(gauth)

# Connect to Google Auth
def connect_to_google_auth():
    try:
        gauth = GoogleAuth()
        gauth.LoadClientConfigFile('D:/PROJECTS/NEW_MTAM/credentials.json')
        print(gauth.credentials)
        return gauth
    except Exception as e:
        print("Error connecting to Google Auth:", e)
        return None

#Inserting User Details and Returning User_id
def get_user_info(drive, db_connection):
    cursor = db_connection.cursor()
    user_info = {}
    try:
        about = drive.auth.service.about().get(fields="user").execute()
        user_info['email'] = about['user']['emailAddress']
        user_info['name'] = about['user']['displayName']
        
        cursor.execute(
            "INSERT INTO Users (email, username) VALUES (%s, %s)",
            (user_info['email'], user_info['name'])
        )
        db_connection.commit()
        
        # Fetch the last inserted user_id
        cursor.execute("SELECT LAST_INSERT_ID()")
        user_id = cursor.fetchone()[0]

        return user_id

    except Exception as e:
        print("Error retrieving user information:", e)
        return None
    finally:
        cursor.close()
# Function to extract upload date from Google Drive file metadata
def extract_upload_date(file_metadata):
    if 'createdDate' in file_metadata:
        # Use createdDate if available
        upload_date_str = file_metadata['createdDate']
    elif 'modifiedDate' in file_metadata:
        # Use modifiedDate if createdDate is not available
        upload_date_str = file_metadata['modifiedDate']
    else:
        # If neither createdDate nor modifiedDate is available, return None
        return None
    
    # Convert upload_date_str to datetime object
    upload_date = datetime.datetime.strptime(upload_date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    
    return upload_date

def insert_file_metadata(file_id, filename, file_type, file_size, parent_folder_id, upload_date, user_id, db_connection):
    cursor = db_connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO FileMetadata (file_id, filename, file_type, file_size, parent_folder_id, upload_date, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (file_id, filename, file_type, file_size, parent_folder_id, upload_date, user_id)
        )
        print("metadata inserted")
        db_connection.commit()
        return cursor.lastrowid
    except mysql.connector.Error as err:
        print("Error inserting file metadata into database:", err)
        db_connection.rollback()
        return None
    finally:
        cursor.close()

# Function to insert data into the Tags table
def insert_tag(tag_name, db_connection):
    cursor = db_connection.cursor()
    try:
        # Check if the tag_name already exists in the Tags table
        cursor.execute(
            "SELECT tag_id FROM Tags WHERE tag_name = %s", (tag_name,)
        )
        existing_tag = cursor.fetchone()
        
        if existing_tag:
            # If the tag already exists, return its tag_id
            return existing_tag[0]
        else:
            # If the tag doesn't exist, insert it into the Tags table
            cursor.execute(
                "INSERT INTO Tags (tag_name) VALUES (%s)",
                (tag_name,)
            )
            db_connection.commit()
            return cursor.lastrowid
    except mysql.connector.Error as err:
        print("Error inserting or retrieving tag from database:", err)
        db_connection.rollback()
        return None
    finally:
        cursor.close()


# Function to insert data into the FileTag table
def insert_file_tag(file_id, tag_id, db_connection):
    cursor = db_connection.cursor()
    try:
        # Insert the file-tag relationship into the FileTag table
        cursor.execute(
            "INSERT INTO FileTag (file_id, tag_id) VALUES (%s, %s)", 
            (file_id, tag_id)
        )
        db_connection.commit()
    except mysql.connector.Error as err:
        print("Error inserting file tag into database:", err)
        db_connection.rollback()
    finally:
        cursor.close()


# Fetch all files and folders in a folder recursively
def get_all_files_and_folders(folder_id, drive_service):
    file_list = drive_service.ListFile(
        {'q': "'{}' in parents and trashed=false".format(folder_id)}).GetList()
    all_files_and_folders = []
    for file_or_folder in file_list:
        all_files_and_folders.append(file_or_folder)
        if file_or_folder['mimeType'] == 'application/vnd.google-apps.folder':
            # Recursively fetch files and folders within subfolders
            all_files_and_folders.extend(get_all_files_and_folders(
                file_or_folder['id'], drive_service))
    return all_files_and_folders

# Get folder name by ID
def get_folder_name_by_id(folder_id, drive_service):
    folder = drive_service.auth.service.files().get(fileId=folder_id).execute()
    return folder['title']

# Get folder metadata by ID
def get_folder_metadata(folder_id, drive_service):
    folder = drive_service.auth.service.files().get(fileId=folder_id).execute()
    return folder

# Extract folder names from file path
def extract_folder_names(file_metadata, drive_service):
    folder_names = []

    def recursive_folder_names(folder_metadata):
        nonlocal folder_names
        for folder in folder_metadata['parents']:
            if 'title' in folder:
                folder_names.append(folder['title'])
            elif 'id' in folder:
                folder_name = get_folder_name_by_id(
                    folder['id'], drive_service)
                folder_names.append(folder_name)
                # Recursively fetch folder names for parent folders
                recursive_folder_names(
                    get_folder_metadata(folder['id'], drive_service))
            else:
                # Handle the case when neither 'title' nor 'id' key is present in folder metadata
                # You can log a warning or handle it based on your application's requirements
                print("Warning: Folder metadata does not contain 'title' or 'id' key")

    recursive_folder_names(file_metadata)
    return folder_names

# Add tags to file in database based on folder names
def add_tags_to_file(file_id, folder_names, db_connection):
    cursor = db_connection.cursor()
    try:
        for tag_name in folder_names:
            tag_id = insert_tag(tag_name, db_connection)
            insert_file_tag(file_id, tag_id, db_connection)  # Pass cursor instead of db_connection
        # Commit the transaction after all file tags have been inserted
        db_connection.commit()
    except mysql.connector.Error as err:
        print("Error inserting data into database:", err)
        db_connection.rollback()
    finally:
        cursor.close()

# Function to print the file_tags table
def print_file_tags_table(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM FileTag")
    rows = cursor.fetchall()
    print("File Tags Table:")
    for row in rows:
        print(row)
    cursor.close()

def extract_id_from_url(url):
    # Split the URL by '/'
    parts = url.split('/')
    # Reverse the list of parts and iterate over it
    for part in reversed(parts):
        # If the part is not empty, return it as the ID
        if part:
            return part
    # Return None if no ID is found
    return None

def file_exists(file_id, db_connection):
    cursor = db_connection.cursor()
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM FileMetadata WHERE file_id = %s", (file_id,)
        )
        result = cursor.fetchone()[0]
        return result > 0  # If count > 0, file exists
    except mysql.connector.Error as err:
        print("Error checking file existence in database:", err)
        return False
    finally:
        cursor.close()


# Main function
def main():
    print("Connecting to database...")
    db_connection = connect_to_database()
    print("Connecting to Google Drive...")
    drive_service = connect_to_google_drive()
    gauth = connect_to_google_auth()

    if not gauth:
        print("Google Auth connection failed. Exiting...")
        return

    # Extract Google Drive link from command-line arguments
    if len(sys.argv) < 2:
        print("Please provide the Google Drive link as a command-line argument.")
        return

    google_drive_link = sys.argv[1]
    print("Google Drive Link:", google_drive_link)

    # Example: Folder ID where your files are stored
    folder_id = extract_id_from_url(google_drive_link)
    print("Fetching files and folders from Google Drive...")
    files_and_folders = get_all_files_and_folders(folder_id, drive_service)
    user_id = get_user_info(drive_service, db_connection)

    for file_or_folder in files_and_folders:
        if 'id' in file_or_folder:
            file_id = file_or_folder['id']
            folder_names = extract_folder_names(file_or_folder, drive_service)
            add_tags_to_file(file_id, folder_names, db_connection)

            # Check if the file has already been processed
            if file_exists(file_id, db_connection):
                print(f"File {file_id} already processed. Skipping...")
                continue
            
            # Insert data into FileMetadata table
            file_name = file_or_folder['title']
            file_type = file_or_folder['mimeType']
            file_size = file_or_folder.get('fileSize', None)
            if file_type != "application/vnd.google-apps.folder":
                # Retrieve the file's metadata to get its parent folder ID
                file_metadata = drive_service.auth.service.files().get(fileId=file_id, fields="parents").execute()
                if 'parents' in file_metadata:
                    parent_folder = file_metadata['parents'][-1]
                    parent_folder_link = parent_folder['parentLink']
                    parent_folder_id = extract_id_from_url(parent_folder_link)
                else:
                    parent_folder_id = None
            else:
                parent_folder_id = None
            if user_id:
                file_metadata_date = drive_service.auth.service.files().get(fileId=file_id).execute()
                upload_date = extract_upload_date(file_metadata_date)
                insert_file_metadata(file_id, file_name, file_type, file_size, parent_folder_id, upload_date, user_id, db_connection)

    print_file_tags_table(db_connection)
    db_connection.close()

if __name__ == "__main__":
    main()