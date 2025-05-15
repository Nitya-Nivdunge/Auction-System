import mysql.connector
import os

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Use your MySQL password
        database="auction_system"
    )

def init_db():
    """
    Check if database exists, but don't recreate it if it already exists.
    Only create directory for chat logs.
    """
    try:
        # Just try to connect to see if the database exists
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Use your MySQL password
            database="auction_system"
        )
        conn.close()
    except mysql.connector.Error:
        # If database doesn't exist, notify user to run the SQL script
        print("Database 'auction_system' not found. Please run the setup SQL script first.")
    
    # Create chat_logs directory
    import os
    os.makedirs("chat_logs", exist_ok=True)