import mysql.connector

def get_db_connection(): 
    return mysql.connector.connect( host="localhost", # Update if needed 
                                   user="root", # Update with your MySQL username 
                                   password="", # Update with your MySQL password 
                                   database="auction_db" # Make sure this DB exists 
                                )