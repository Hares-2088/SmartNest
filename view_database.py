# This script is used to view the existing users in the database and add a default user if none exist.
import sqlite3
from werkzeug.security import generate_password_hash

DB_FILE = "smartnest.db"

def view_users():
    """Function to view existing users in the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM users")
    rows = cursor.fetchall()
    conn.close()

    if rows:
        print("Existing users in the database:")
        for row in rows:
            print(f"ID: {row[0]}, Username: {row[1]}, Password Hash: {row[2]}")
    else:
        print("No users found in the database.")

def add_default_user(username, password):
    """Function to add a default user to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check if the username already exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        print(f"User '{username}' already exists in the database. Skipping addition.")
    else:
        # Add the user if they don't exist
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        print(f"Default user '{username}' added successfully.")

    conn.close()
    
if __name__ == "__main__":
    print("Viewing existing users:")
    view_users()

    print("\nAdding default user:")
    add_default_user("admin", "default123")

    print("\nViewing users after adding default:")
    view_users()
    
def update_admin_password(new_password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
    cursor.execute("UPDATE users SET password = ? WHERE username = 'admin'", (hashed_password,))
    conn.commit()
    conn.close()
    print(f"Password for 'admin' updated successfully.")

if __name__ == "__main__":
    update_admin_password("pwd")
