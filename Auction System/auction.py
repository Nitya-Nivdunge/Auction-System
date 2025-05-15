from database import get_connection
from datetime import datetime

def create_auction(product_name, min_price, created_by, end_time):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO auctions (product_name, min_price, created_by, end_time, current_price, is_active)
        VALUES (%s, %s, %s, %s, %s, 1)
    """, (product_name, min_price, created_by, end_time, min_price))
    
    auction_id = cur.lastrowid
    
    # Create chat file
    import os
    os.makedirs("chat_logs", exist_ok=True)
    with open(f"chat_logs/auction_{auction_id}.txt", "w", encoding="utf-8") as f:
        f.write(f"--- Auction for {product_name} started ---\n")
    
    conn.commit()
    cur.close()
    conn.close()
    
    return auction_id

def get_active_auctions():
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
    
    return results

def get_user_auctions(user_id):
    conn = get_connection()
    cur = conn.cursor()
    
    # Get active auctions created by the user
    cur.execute("""
        SELECT id, product_name, current_price, end_time
        FROM auctions 
        WHERE created_by = %s AND (end_time > %s OR is_active = 1)
        ORDER BY end_time ASC
    """, (user_id, datetime.now()))
    
    active_auctions = cur.fetchall()
    
    # Get completed auctions created by the user
    cur.execute("""
        SELECT a.product_name, a.created_at, a.min_price, a.current_price, 
               IFNULL(u.username, 'No Winner') as winner_name
        FROM auctions a
        LEFT JOIN users u ON a.winner_id = u.id
        WHERE a.created_by = %s AND (a.end_time <= %s OR a.is_active = 0)
        ORDER BY a.end_time DESC
    """, (user_id, datetime.now()))
    
    completed_auctions = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return active_auctions, completed_auctions

def stop_auction(auction_id):
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Mark auction as inactive
        cur.execute("""
            UPDATE auctions
            SET is_active = 0
            WHERE id = %s
        """, (auction_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except:
        conn.close()
        return False