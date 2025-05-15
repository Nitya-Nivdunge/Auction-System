import tkinter as tk
from tkinter import messagebox, ttk
from auth import register_user, login_user
from auction import create_auction, get_active_auctions, get_user_auctions, stop_auction
from bid import place_bid
from dashboard import get_user_participated_bids
from chat import save_chat
from datetime import datetime, timedelta
import os
import threading
import time

class AuctionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Distributed Auction System")
        self.user_id = None
        self.username = None
        self.stop_refresh_thread = False
        self.timer_data = {}  # To store end times and auction IDs
        self.show_home()

    def show_home(self):
        self.clear()
        tk.Label(self.root, text="Welcome to the Distributed Auction System", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Register", command=self.show_register).pack(pady=5)
        tk.Button(self.root, text="Login", command=self.show_login).pack(pady=5)

    def show_register(self):
        self.clear()
        tk.Label(self.root, text="Register", font=("Arial", 14)).pack(pady=5)
        tk.Label(self.root, text="Username").pack()
        self.reg_username = tk.Entry(self.root)
        self.reg_username.pack()
        tk.Label(self.root, text="Password").pack()
        self.reg_password = tk.Entry(self.root, show="*")
        self.reg_password.pack()
        tk.Button(self.root, text="Register", command=self.register).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.show_home).pack()

    def register(self):
        uname = self.reg_username.get()
        pwd = self.reg_password.get()
        if register_user(uname, pwd):
            messagebox.showinfo("Success", "User registered! Please login.")
            self.show_login()
        else:
            messagebox.showerror("Error", "Username already exists or registration failed.")

    def show_login(self):
        self.clear()
        tk.Label(self.root, text="Login", font=("Arial", 14)).pack(pady=5)
        tk.Label(self.root, text="Username").pack()
        self.log_username = tk.Entry(self.root)
        self.log_username.pack()
        tk.Label(self.root, text="Password").pack()
        self.log_password = tk.Entry(self.root, show="*")
        self.log_password.pack()
        tk.Button(self.root, text="Login", command=self.login).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.show_home).pack()

    def login(self):
        uname = self.log_username.get()
        pwd = self.log_password.get()
        uid = login_user(uname, pwd)
        if uid:
            self.user_id = uid
            self.username = uname
            self.show_dashboard()
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password")

    def show_dashboard(self):
        self.clear()
        
        # Create a navigation frame
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(fill="x", pady=5)
        
        tk.Label(nav_frame, text=f"Welcome {self.username}", font=("Arial", 14)).pack(side="left", padx=10)
        
        # Navigation buttons
        tk.Button(nav_frame, text="Active Auctions", command=self.show_dashboard).pack(side="left", padx=5)
        tk.Button(nav_frame, text="My Bids", command=self.show_my_bids_page).pack(side="left", padx=5)
        tk.Button(nav_frame, text="My Auctions", command=self.show_my_auctions).pack(side="left", padx=5)
        tk.Button(nav_frame, text="Create Auction", command=self.create_auction_ui).pack(side="left", padx=5)
        tk.Button(nav_frame, text="Logout", command=self.logout).pack(side="right", padx=10)
        
        # Auctions list
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        tk.Label(list_frame, text="Active Auctions", font=("Arial", 12)).pack(pady=5)
        
        # Create treeview for auctions
        self.tree = ttk.Treeview(list_frame, columns=("ID", "Creator", "Product", "Current Bid", "Ends In"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Creator", text="Creator")
        self.tree.heading("Product", text="Product")
        self.tree.heading("Current Bid", text="Current Bid")
        self.tree.heading("Ends In", text="Ends In")
        self.tree.pack(fill="both", expand=True)
        
        # Action buttons
        action_frame = tk.Frame(self.root)
        action_frame.pack(fill="x", pady=5)
        
        tk.Button(action_frame, text="Place Bid", command=self.place_bid_ui).pack(side="left", padx=5)
        tk.Button(action_frame, text="Chat", command=self.open_chat_for_selected).pack(side="left", padx=5)
        tk.Button(action_frame, text="Refresh", command=self.refresh_auctions).pack(side="left", padx=5)
        
        # Stop any existing thread
        self.stop_refresh_thread = True
        # Get initial auction data
        self.refresh_auctions(init=True)
        
        # Start the refresh thread for auction data
        self.stop_refresh_thread = False
        threading.Thread(target=self.auction_refresh_thread, daemon=True).start()
        
        # Start the timer thread for smooth countdown
        threading.Thread(target=self.timer_thread, daemon=True).start()

    def logout(self):
        # Ensure threads are stopped before logging out
        self.stop_refresh_thread = True
        self.user_id = None
        self.username = None
        self.show_home()

    def auction_refresh_thread(self):
        """Thread to periodically refresh auction data from the database"""
        while not self.stop_refresh_thread:
            # Call refresh_auctions method but don't start another thread
            try:
                # Schedule the refresh on the main thread
                self.root.after(0, lambda: self.refresh_auctions(init=False))
                time.sleep(5)  # Refresh database data every 5 seconds
            except Exception as e:
                print(f"Error in refresh thread: {e}")
            
            # Check if we should stop
            if self.stop_refresh_thread:
                break

    def timer_thread(self):
        """Thread to update countdown timers every second"""
        while not self.stop_refresh_thread:
            try:
                if hasattr(self, 'tree'):
                    # Schedule the UI update on the main thread
                    self.root.after(0, self.update_countdown_timers)
                time.sleep(1)  # Update timers every 1 second
            except Exception as e:
                print(f"Error in timer thread: {e}")
            
            # Check if we should stop
            if self.stop_refresh_thread:
                break

    def update_countdown_timers(self):
        """Update just the countdown timers in the UI"""
        if not hasattr(self, 'tree'):
            return
            
        current_time = datetime.now()
        
        # For each auction in the tree, update just the time
        for item_id in self.tree.get_children():
            auction_id = str(item_id)
            
            if auction_id in self.timer_data:
                end_time = self.timer_data[auction_id]
                time_left = end_time - current_time
                
                if time_left.total_seconds() > 0:
                    # Update just the time column
                    values = self.tree.item(item_id, 'values')
                    if values and len(values) >= 5:
                        # Preserve all values except the time
                        new_values = list(values)
                        new_values[4] = str(time_left).split(".")[0]  # Format as HH:MM:SS
                        self.tree.item(item_id, values=new_values)
                else:
                    # Auction has ended, will be removed on next refresh
                    new_values = list(self.tree.item(item_id, 'values'))
                    new_values[4] = "ENDED"
                    self.tree.item(item_id, values=new_values)

    def refresh_auctions(self, init=False):
        """Refresh auction data from database"""
        if not hasattr(self, 'tree'):
            return
            
        # If this is not an init call, just get the data but don't clear the tree
        if not init:
            # Get current auction data
            auctions = get_active_auctions()
            auction_ids = set(str(auc[0]) for auc in auctions)
            
            # Remove auctions that are no longer active
            for item_id in self.tree.get_children():
                if item_id not in auction_ids:
                    self.tree.delete(item_id)
                    if item_id in self.timer_data:
                        del self.timer_data[item_id]
            
            # Update or add auctions
            for auc in auctions:
                auction_id, creator_name, product_name, current_price, end_time = auc
                auction_id_str = str(auction_id)
                
                # Parse end time
                end = datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S")
                self.timer_data[auction_id_str] = end
                
                # Check if item exists
                item_exists = auction_id_str in self.tree.get_children()
                
                if item_exists:
                    # Just update price (time is updated by timer thread)
                    item_values = list(self.tree.item(auction_id_str, 'values'))
                    item_values[3] = current_price  # Update current price
                    self.tree.item(auction_id_str, values=item_values)
                else:
                    # Add new auction
                    left = end - datetime.now()
                    self.tree.insert("", "end", iid=auction_id_str,
                                    values=(auction_id, creator_name, product_name, 
                                            current_price, str(left).split(".")[0]))
        else:
            # Clear existing entries on init
            for row in self.tree.get_children():
                self.tree.delete(row)
            
            # Clear timer data
            self.timer_data = {}
                
            # Get and display active auctions
            for auc in get_active_auctions():
                # Parse end time and calculate remaining time
                auction_id, creator_name, product_name, current_price, end_time = auc
                auction_id_str = str(auction_id)
                
                end = datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S")
                self.timer_data[auction_id_str] = end
                
                left = end - datetime.now()
                
                # Insert into treeview
                self.tree.insert("", "end", iid=auction_id_str,
                                values=(auction_id, creator_name, product_name, 
                                        current_price, str(left).split(".")[0]))

    def show_my_bids_page(self):
        # Stop timer threads before changing page
        self.stop_refresh_thread = True
        
        self.clear()
        
        # Create a navigation frame
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(fill="x", pady=5)
        
        tk.Label(nav_frame, text=f"Welcome {self.username}", font=("Arial", 14)).pack(side="left", padx=10)
        
        # Navigation buttons
        tk.Button(nav_frame, text="Active Auctions", command=self.show_dashboard).pack(side="left", padx=5)
        tk.Button(nav_frame, text="My Bids", command=self.show_my_bids_page).pack(side="left", padx=5)
        tk.Button(nav_frame, text="My Auctions", command=self.show_my_auctions).pack(side="left", padx=5)
        tk.Button(nav_frame, text="Create Auction", command=self.create_auction_ui).pack(side="left", padx=5)
        tk.Button(nav_frame, text="Logout", command=self.logout).pack(side="right", padx=10)
        
        # My bids content
        content_frame = tk.Frame(self.root)
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        tk.Label(content_frame, text="My Bids History", font=("Arial", 12)).pack(pady=5)
        
        # Create treeview for bid history with updated columns
        tree = ttk.Treeview(content_frame, columns=("Product", "Current Bid", "My Bid", "Final Bid", "Bid Time", "Won"), show="headings")
        tree.heading("Product", text="Product")
        tree.heading("Current Bid", text="Current Bid")
        tree.heading("My Bid", text="My Bid")
        tree.heading("Final Bid", text="Final Bid")
        tree.heading("Bid Time", text="Bid Time")
        tree.heading("Won", text="Won")
        tree.pack(fill="both", expand=True)
        
        # Populate with user's bid history
        for row in get_user_participated_bids(self.user_id):
            tree.insert("", "end", values=row)

    def show_my_auctions(self):
        # Stop timer threads before changing page
        self.stop_refresh_thread = True
        
        self.clear()
        
        # Create a navigation frame
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(fill="x", pady=5)
        
        tk.Label(nav_frame, text=f"Welcome {self.username}", font=("Arial", 14)).pack(side="left", padx=10)
        
        # Navigation buttons
        tk.Button(nav_frame, text="Active Auctions", command=self.show_dashboard).pack(side="left", padx=5)
        tk.Button(nav_frame, text="My Bids", command=self.show_my_bids_page).pack(side="left", padx=5)
        tk.Button(nav_frame, text="My Auctions", command=self.show_my_auctions).pack(side="left", padx=5)
        tk.Button(nav_frame, text="Create Auction", command=self.create_auction_ui).pack(side="left", padx=5)
        tk.Button(nav_frame, text="Logout", command=self.logout).pack(side="right", padx=10)
        
        # My auctions content
        content_frame = tk.Frame(self.root)
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create tabs for active and completed auctions
        tab_control = ttk.Notebook(content_frame)
        
        active_tab = ttk.Frame(tab_control)
        completed_tab = ttk.Frame(tab_control)
        
        tab_control.add(active_tab, text="Active Auctions")
        tab_control.add(completed_tab, text="Completed Auctions")
        tab_control.pack(expand=1, fill="both")
        
        # Active auctions treeview
        active_tree = ttk.Treeview(active_tab, columns=("ID", "Product", "Current Bid", "End Time"), show="headings")
        active_tree.heading("ID", text="ID")
        active_tree.heading("Product", text="Product")
        active_tree.heading("Current Bid", text="Current Bid")
        active_tree.heading("End Time", text="End Time")
        active_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Completed auctions treeview
        completed_tree = ttk.Treeview(completed_tab, columns=("Product", "Date Created", "Initial Price", "Final Bid", "Winner"), show="headings")
        completed_tree.heading("Product", text="Product")
        completed_tree.heading("Date Created", text="Date Created")
        completed_tree.heading("Initial Price", text="Initial Price")
        completed_tree.heading("Final Bid", text="Final Bid")
        completed_tree.heading("Winner", text="Winner")
        completed_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Action buttons for active auctions
        action_frame = tk.Frame(active_tab)
        action_frame.pack(fill="x", pady=5)
        
        def stop_selected_auction():
            selected = active_tree.selection()
            if not selected:
                messagebox.showinfo("Select Auction", "Please select an auction to stop")
                return
                
            auction_id = int(selected[0])
            if stop_auction(auction_id):
                messagebox.showinfo("Success", "Auction stopped successfully")
                self.show_my_auctions()  # Refresh
            else:
                messagebox.showerror("Error", "Failed to stop auction")
        
        tk.Button(action_frame, text="Stop Auction", command=stop_selected_auction).pack(side="left", padx=5)
        tk.Button(action_frame, text="Chat", command=lambda: self.open_chat_window(active_tree.selection()[0]) if active_tree.selection() else messagebox.showinfo("Select Auction", "Please select an auction")).pack(side="left", padx=5)
        
        # Populate the trees with user's auctions
        active_auctions, completed_auctions = get_user_auctions(self.user_id)
        
        for auc in active_auctions:
            auction_id, product_name, current_price, end_time = auc
            active_tree.insert("", "end", iid=str(auction_id), values=(auction_id, product_name, current_price, end_time))
            
        for auc in completed_auctions:
            product_name, date_created, initial_price, final_bid, winner_name = auc
            completed_tree.insert("", "end", values=(product_name, date_created, initial_price, final_bid, winner_name if winner_name else "No winner"))

    def create_auction_ui(self):
        win = tk.Toplevel(self.root)
        win.title("Create Auction")
        win.geometry("300x250")
        
        tk.Label(win, text="Create New Auction", font=("Arial", 14)).pack(pady=10)
        
        tk.Label(win, text="Product Name").pack()
        pname = tk.Entry(win, width=30)
        pname.pack(pady=5)
        
        tk.Label(win, text="Minimum Price ($)").pack()
        price = tk.Entry(win, width=30)
        price.pack(pady=5)
        
        tk.Label(win, text="Duration (minutes)").pack()
        mins = tk.Entry(win, width=30)
        mins.pack(pady=5)
        
        def submit():
            try:
                end_time = datetime.now() + timedelta(minutes=int(mins.get()))
                create_auction(pname.get(), float(price.get()), self.user_id, end_time.strftime("%Y-%m-%d %H:%M:%S"))
                messagebox.showinfo("Success", "Auction created successfully!")
                win.destroy()
                self.refresh_auctions(init=True)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        tk.Button(win, text="Create Auction", command=submit).pack(pady=10)

    def place_bid_ui(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Auction", "Please select an auction to place a bid")
            return
            
        auction_id = int(selected[0])
        
        # Get the auction creator to prevent self-bidding
        item = self.tree.item(selected[0])
        creator_name = item['values'][1]  # Creator is the second column
        
        # Check if user is the creator
        if creator_name == self.username:
            messagebox.showwarning("Not Allowed", "You cannot bid on your own auction")
            return
        
        win = tk.Toplevel(self.root)
        win.title("Place Bid")
        win.geometry("300x150")
        
        tk.Label(win, text="Place Your Bid", font=("Arial", 14)).pack(pady=10)
        
        tk.Label(win, text="Your Bid Amount ($)").pack()
        amt = tk.Entry(win, width=30)
        amt.pack(pady=5)
        
        def submit():
            try:
                bid_amt = float(amt.get())
                success, lamport_time = place_bid(self.user_id, auction_id, bid_amt)
                
                if success:
                    messagebox.showinfo("Success", f"Bid placed successfully! Lamport Clock: {lamport_time}")
                else:
                    messagebox.showwarning("Failed", "Bid amount is too low or auction has ended.")
                
                win.destroy()
                self.refresh_auctions(init=True)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        tk.Button(win, text="Submit Bid", command=submit).pack(pady=10)

    def open_chat_for_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Auction", "Please select an auction to open chat")
            return
            
        auction_id = int(selected[0])
        self.open_chat_window(auction_id)

    def open_chat_window(self, auction_id):
        # Create a new window for chat
        chat_win = tk.Toplevel(self.root)
        chat_win.title(f"Auction #{auction_id} Chat")
        chat_win.geometry("400x500")
        
        # Chat display area
        chat_frame = tk.Frame(chat_win)
        chat_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add a scrollbar to the chat display
        scrollbar = tk.Scrollbar(chat_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create the chat display text widget
        chat_display = tk.Text(chat_frame, state='normal', height=20, width=45, yscrollcommand=scrollbar.set)
        chat_display.pack(fill="both", expand=True)
        scrollbar.config(command=chat_display.yview)
        
        # Load existing chat messages
        log_file = f"chat_logs/auction_{auction_id}.txt"
        os.makedirs("chat_logs", exist_ok=True)
        
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                chat_display.insert(tk.END, f.read())
        
        chat_display.see(tk.END)  # Scroll to bottom
        chat_display.config(state='disabled')  # Make read-only
        
        # Message entry area
        entry_frame = tk.Frame(chat_win)
        entry_frame.pack(fill="x", padx=10, pady=5)
        
        msg_entry = tk.Entry(entry_frame, width=40)
        msg_entry.pack(side=tk.LEFT, fill="x", expand=True)
        msg_entry.focus()  # Put cursor in entry box
        
        def send_msg():
            msg = msg_entry.get().strip()
            if msg:
                # Save the message
                formatted_msg = save_chat(auction_id, self.username, msg)
                
                # Update the chat display
                chat_display.config(state='normal')
                chat_display.insert(tk.END, formatted_msg + "\n")
                chat_display.see(tk.END)  # Scroll to bottom
                chat_display.config(state='disabled')
                
                # Clear the entry box
                msg_entry.delete(0, tk.END)
        
        # Bind Enter key to send message
        msg_entry.bind("<Return>", lambda event: send_msg())
        
        # Send button
        send_btn = tk.Button(entry_frame, text="Send", command=send_msg)
        send_btn.pack(side=tk.RIGHT, padx=5)
    
    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()