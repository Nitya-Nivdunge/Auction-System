from database import get_connection

def get_user_participated_bids(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # First get all the user's bids
    cursor.execute("""
        SELECT 
            b.id,
            b.auction_id,
            a.product_name,
            b.bid_amount AS my_bid,
            b.bid_time,
            a.winner_id = %s AS user_won,
            a.is_active
        FROM auctions a
        JOIN bids b ON a.id = b.auction_id
        WHERE b.user_id = %s
        ORDER BY b.auction_id, b.bid_time DESC
    """, (user_id, user_id))
    
    bids = cursor.fetchall()
    
    # Process results to create the proper display format
    processed_results = []
    last_bid_per_auction = {}
    
    # First, identify the last bid for each auction
    for bid in bids:
        bid_id, auction_id, product_name, my_bid, bid_time, user_won, is_active = bid
        if auction_id not in last_bid_per_auction:
            last_bid_per_auction[auction_id] = bid_id
    
    for bid in bids:
        bid_id, auction_id, product_name, my_bid, bid_time, user_won, is_active = bid
        
        # Get the current bid before this bid was placed
        cursor.execute("""
            SELECT COALESCE(MAX(bid_amount), 
                (SELECT min_price FROM auctions WHERE id = %s)) AS current_bid
            FROM bids
            WHERE auction_id = %s AND bid_time < %s
        """, (auction_id, auction_id, bid_time))
        
        current_bid = cursor.fetchone()[0]
        
        # Get the final bid if auction is completed
        final_bid = None
        if not is_active:
            cursor.execute("""
                SELECT current_price
                FROM auctions
                WHERE id = %s
            """, (auction_id,))
            final_bid = cursor.fetchone()[0]
        
        # Determine if this specific bid is the winning one
        is_winning_bid = False
        if user_won and bid_id == last_bid_per_auction[auction_id]:
            is_winning_bid = True
        
        processed_results.append((
            product_name,
            current_bid,
            my_bid,
            final_bid,
            bid_time,
            "Yes" if is_winning_bid else "No"
        ))
    
    conn.close()
    return sorted(processed_results, key=lambda x: x[4], reverse=True)  # Sort by bid_time desc