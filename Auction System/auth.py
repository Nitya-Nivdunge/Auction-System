from database import get_connection
import hashlib

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    """Register a new user."""
    if not username or not password:
        return False
        
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        conn.close()
        return False
    
    # Hash the password
    hashed_password = hash_password(password)
    
    # Insert new user
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                  (username, hashed_password))
    conn.commit()
    conn.close()
    
    return True

def login_user(username, password):
    """Verify user credentials and return user ID if valid."""
    if not username or not password:
        return None
        
    conn = get_connection()
    cursor = conn.cursor()
    
    # Hash the password
    hashed_password = hash_password(password)
    
    # Check credentials
    cursor.execute("SELECT id FROM users WHERE username = %s AND password = %s", 
                  (username, hashed_password))
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None