import mysql.connector

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
