import mysql.connector


def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="mediagdrive"
    )
