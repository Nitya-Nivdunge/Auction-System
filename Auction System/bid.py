from database import get_connection
from lamport_clock import clock
from datetime import datetime

def place_bid(user_id, auction_id, amount):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if user is the auction creator
    cursor.execute("SELECT created_by FROM auctions WHERE id = %s", (auction_id,))
    creator_id = cursor.fetchone()[0]
    
    if creator_id == user_id:
        conn.close()
        return False, clock.time
    
    # Get the current highest bid
    cursor.execute("""
        SELECT current_price, end_time, is_active 
        FROM auctions 
        WHERE id = %s
    """, (auction_id,))
    
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, clock.time
    
    current_price, end_time, is_active = row
    
    # Check if auction is active and not expired
    if not is_active or datetime.now() > end_time:
        conn.close()
        return False, clock.time
    
    if amount > current_price:
        # Update the auction with new current price and winner
        cursor.execute("UPDATE auctions SET current_price = %s, winner_id = %s WHERE id = %s",
                      (amount, user_id, auction_id))
        
        # Insert into bids table
        cursor.execute("INSERT INTO bids (auction_id, user_id, bid_amount, lamport_time) VALUES (%s, %s, %s, %s)",
                      (auction_id, user_id, amount, clock.time))
        
        # Lamport tick
        lamport_time = clock.tick()
        
        conn.commit()
        conn.close()
        
        return True, lamport_time
    else:
        conn.close()
        return False, clock.time