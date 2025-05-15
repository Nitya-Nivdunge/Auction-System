# Auction-System
Python tkinter GUI based auction system with MySQL database connectivity. Allows creating an auction and others users can bid for the product by placing higher bids. Users have the chat functionality to negotiate. The owner of auction can stop the auction anytime and the user with the highest bid gets the  product at the end of time. Saves chat-log

# Steps :
1. Create Database : Open MySQl Workbench / phpMyAdmin (if your using XAMPP) and create a database named " auction_system ".
2. Create Tables : Run the schema.sql file within auction_system database to create all the tables.
3. Start Server : Run server.py file
4. Start Application : Run main.py ( on multiple terminals )
5. Register & Login : On multiple terminals register with different credentials and Login with the same.
6. Create Auction : From one account create an auction by setting product information , min bid price , duration.
7. Place Bids : From other accounts users can place higher bids till timer ends which are updated across all accounts instantly.

# Additional Features :
1. The Auction Creator has the option to stop the auction timer before time.
2. Auctions have distributed chat section i.e individual chat node for each new auction.
3. Chat Logs are stored in a separate folder named chat_logs and also within the database.
4. Bidders can view what bids they have placed and whats the current bidding amount is.
5. Auction Owners can see all their Active / Closed auctions.
