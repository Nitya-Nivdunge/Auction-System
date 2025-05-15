from datetime import datetime
from database import get_connection
import os

def save_chat(auction_id, username, message):
    # Get current timestamp
    timestamp = datetime.now().strftime("%H:%M:%S")
    date = datetime.now().strftime("%Y-%m-%d")
    formatted_msg = f"[{username} {timestamp}] [{date}]: {message}"
    
    # Save to database
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO chat (auction_id, username, message, timestamp, date) VALUES (%s, %s, %s, %s, %s)",
                  (auction_id, username, message, timestamp, date))
    
    # Also update the chat_log field in the auctions table
    cursor.execute("UPDATE auctions SET chat_log = CONCAT(IFNULL(chat_log, ''), %s) WHERE id = %s",
                  (formatted_msg + "\n", auction_id))
    
    conn.commit()
    conn.close()
    
    # Create directory if it doesn't exist
    os.makedirs("chat_logs", exist_ok=True)
    
    # Save to .txt file
    with open(f"chat_logs/auction_{auction_id}.txt", "a", encoding="utf-8") as f:
        f.write(formatted_msg + "\n")
        
    return formatted_msg