# server.py
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
from database import get_connection
from datetime import datetime
import os

class AuctionServer:
    def __init__(self):
        # Initialize any server-side state
        os.makedirs("chat_logs", exist_ok=True)
        
    def create_auction(self, product_name, min_price, created_by, end_time):
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO auctions (product_name, min_price, created_by, end_time, current_price, is_active)
            VALUES (%s, %s, %s, %s, %s, 1)
        """, (product_name, min_price, created_by, end_time, min_price))
        
        auction_id = cur.lastrowid
        
        # Create chat file
        with open(f"chat_logs/auction_{auction_id}.txt", "w", encoding="utf-8") as f:
            f.write(f"--- Auction for {product_name} started ---\n")
        
        conn.commit()
        cur.close()
        conn.close()
        
        return auction_id
    
    def get_active_auctions(self):
        # Existing implementation moved to server
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT a.id, u.username, a.product_name, a.current_price, a.end_time
            FROM auctions a
            JOIN users u ON a.created_by = u.id
            WHERE a.end_time > %s AND a.is_active = 1
            ORDER BY a.end_time ASC
        """, (datetime.now(),))
        
        results = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Convert to list of lists for XML-RPC transport
        return [list(row) for row in results]
    
    # Add other methods (place_bid, user authentication, etc.)

# Set up the XML-RPC server
server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
server.register_instance(AuctionServer())
print("Auction server running on port 8000...")
server.serve_forever()