import mysql.connector
import humanize

# Connect to MySQL database
def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="mediagdrive"
    )

# Search for files by tag and/or date
def search_files_by_tag(tag=None, date=None):
    db_connection = connect_to_database()
    cursor = db_connection.cursor(dictionary=True)
    try:
        if tag and date:
            # Search files by tag and date
            cursor.execute(
                "SELECT fm.file_id, fm.filename, fm.file_type, fm.file_size, fm.upload_date, u.username, fm.parent_folder_id " +
                "FROM FileMetadata fm " +
                "JOIN FileTag ft ON fm.file_id = ft.file_id " +
                "JOIN Tags t ON ft.tag_id = t.tag_id " +
                "JOIN Users u ON fm.user_id = u.user_id " +
                "WHERE t.tag_name = %s AND fm.upload_date = %s", (tag, date)
            )
        elif tag:
            # Search files by tag only
            cursor.execute(
                "SELECT fm.file_id, fm.filename, fm.file_type, fm.file_size, fm.upload_date, u.username, fm.parent_folder_id " +
                "FROM FileMetadata fm " +
                "JOIN FileTag ft ON fm.file_id = ft.file_id " +
                "JOIN Tags t ON ft.tag_id = t.tag_id " +
                "JOIN Users u ON fm.user_id = u.user_id " +
                "WHERE t.tag_name = %s", (tag,)
            )
        elif date:
            # Search files by date only
            cursor.execute(
                "SELECT fm.file_id, fm.filename, fm.file_type, fm.file_size, fm.upload_date, u.username, fm.parent_folder_id " +
                "FROM FileMetadata fm " +
                "JOIN Users u ON fm.user_id = u.user_id " +
                "WHERE fm.upload_date = %s", (date,)
            )
        else:
            # No tag or date provided
            return None

        files = cursor.fetchall()
        return files
    except mysql.connector.Error as err:
        print("Error searching files:", err)
        return None
    finally:
        cursor.close()
        db_connection.close()

# Function to handle search requests
def search_files_with_tag(tag=None, date=None):
    matching_files = search_files_by_tag(tag=tag, date=date)
    return matching_files

def query_metadata_from_database(filename):
    # Connect to the MySQL database
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="mediagdrive"
    )

    cursor = connection.cursor()

    try:
        # Construct the SQL query to fetch metadata based on the filename
        query = "SELECT filename, file_type, file_size, upload_date FROM filemetadata WHERE filename = %s"
        cursor.execute(query, (filename,))
        
        # Fetch the result
        result = cursor.fetchone()
        
        # Get the column names
        column_names = [i[0] for i in cursor.description]

        # Define mapping for custom keys
        key_mapping = {
            'filename': 'File Name',
            'file_type': 'File Type',
            'file_size': 'File Size',
            'upload_date': 'Upload Date'
        }

        # Format the result with custom keys
        formatted_result = {}
        for column, value in zip(column_names, result):
            formatted_result[key_mapping[column]] = value
        for i in  formatted_result:
            if i == "File Size":
                if formatted_result[i] != None:
                    formatted_result[i] = humanize.naturalsize(formatted_result[i], binary=True)
                else:
                    formatted_result[i] = "-"
            elif i == "File Type":
                
                parts = formatted_result[i].split('/')
                formatted_result[i] = parts[-1]
                if formatted_result[i] == "vnd.google-apps.folder":
                    formatted_result[i] = "Folder"
            print(formatted_result[i])
        # Close cursor and connection
        cursor.close()
        connection.close()

        return formatted_result  # Return formatted metadata
    except Exception as e:
        # Handle any errors
        print("Error fetching metadata:", e)
        return None
