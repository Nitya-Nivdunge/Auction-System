from database import init_db
import tkinter as tk
from gui import AuctionApp

def main():
    # Initialize database
    init_db()
    
    # Start the GUI application
    root = tk.Tk()
    root.title("Distributed Auction System")
    root.geometry("800x600")
    app = AuctionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()