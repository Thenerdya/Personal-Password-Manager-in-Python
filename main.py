import bcrypt
import sqlite3
import os
import base64
import secrets
from cryptography.fernet import Fernet
from getpass import getpass

# Database and encryption setup
DB_FILE = "password_manager.db"
KEY_FILE = "encryption_key.key"

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)

def load_key():
    return open(KEY_FILE, "rb").read()

if not os.path.exists(KEY_FILE):
    generate_key()
encryption_key = load_key()
cipher = Fernet(encryption_key)

# Database setup
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS master_password (
            id INTEGER PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Master Password Handling
def set_master_password():
    password = getpass("Set master password: ").encode('utf-8')
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO master_password (id, password_hash) VALUES (?, ?)", (1, hashed))
    conn.commit()
    conn.close()

def verify_master_password():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM master_password WHERE id = ?", (1,))
    stored_hash = cursor.fetchone()
    conn.close()

    if stored_hash:
        password = getpass("Enter master password: ").encode('utf-8')
        if bcrypt.checkpw(password, stored_hash[0]):
            return True
        else:
            print("Invalid password.")
            return False
    else:
        print("No master password found, please set one.")
        set_master_password()
        return verify_master_password()

# Password Storage and Retrieval
def add_credential():
    website = input("Website: ")
    username = input("Username: ")
    password = getpass("Password (leave blank to generate): ")
    if not password:
        password = generate_password()

    encrypted_password = cipher.encrypt(password.encode()).decode()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO credentials (website, username, password) VALUES (?, ?, ?)", (website, username, encrypted_password))
    conn.commit()
    conn.close()
    print(f"Credentials for {website} saved.")

def view_credentials():
    website = input("Enter website to search for credentials: ")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM credentials WHERE website = ?", (website,))
    rows = cursor.fetchall()
    conn.close()

    if rows:
        for row in rows:
            username, encrypted_password = row
            password = cipher.decrypt(encrypted_password.encode()).decode()
            print(f"Website: {website}, Username: {username}, Password: {password}")
    else:
        print(f"No credentials found for {website}.")

# Update and Delete Credentials
def update_credential():
    website = input("Enter website to update credentials: ")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM credentials WHERE website = ?", (website,))
    row = cursor.fetchone()

    if row:
        new_username = input(f"New Username (leave blank to keep '{row[0]}'): ") or row[0]
        new_password = getpass(f"New Password (leave blank to keep current): ")
        if new_password:
            new_password = cipher.encrypt(new_password.encode()).decode()
        else:
            new_password = row[1]

        cursor.execute("UPDATE credentials SET username = ?, password = ? WHERE website = ?", (new_username, new_password, website))
        conn.commit()
        print(f"Credentials for {website} updated.")
    else:
        print(f"No credentials found for {website}.")

    conn.close()

def delete_credential():
    website = input("Enter website to delete credentials: ")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM credentials WHERE website = ?", (website,))
    conn.commit()
    conn.close()
    print(f"Credentials for {website} deleted.")

# Password Generator
def generate_password(length=12, special=True, numbers=True, uppercase=True):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    if uppercase:
        alphabet += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if numbers:
        alphabet += "0123456789"
    if special:
        alphabet += "!@#$%^&*()"

    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    print(f"Generated password: {password}")
    return password

# Password Strength Check
def check_password_strength(password):
    length = len(password)
    categories = [
        bool(any(c.islower() for c in password)),
        bool(any(c.isupper() for c in password)),
        bool(any(c.isdigit() for c in password)),
        bool(any(c in "!@#$%^&*()" for c in password))
    ]
    strength = sum(categories)

    if length >= 12 and strength >= 3:
        return "Strong"
    elif length >= 8 and strength >= 2:
        return "Medium"
    else:
        return "Weak"

# Backup and Restore
def backup_credentials():
    backup_file = input("Enter backup file name: ")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM credentials")
    rows = cursor.fetchall()
    with open(backup_file, "w") as file:
        for row in rows:
            file.write(f"{row[1]} {row[2]} {row[3]}\n")
    conn.close()
    print(f"Backup saved to {backup_file}.")

def restore_credentials():
    backup_file = input("Enter backup file name to restore: ")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    with open(backup_file, "r") as file:
        for line in file:
            website, username, encrypted_password = line.strip().split()
            cursor.execute("INSERT INTO credentials (website, username, password) VALUES (?, ?, ?)", (website, username, encrypted_password))
    conn.commit()
    conn.close()
    print("Backup restored.")

# Main Menu
def main_menu():
    print("Password Manager")
    if not verify_master_password():
        return
    
    while True:
        print("\nMenu:")
        print("1. Add Credential")
        print("2. View Credential")
        print("3. Update Credential")
        print("4. Delete Credential")
        print("5. Generate Password")
        print("6. Backup Credentials")
        print("7. Restore Credentials")
        print("8. Exit")
        
        choice = input("Choose an option: ")
        
        if choice == '1':
            add_credential()
        elif choice == '2':
            view_credentials()
        elif choice == '3':
            update_credential()
        elif choice == '4':
            delete_credential()
        elif choice == '5':
            generate_password()
        elif choice == '6':
            backup_credentials()
        elif choice == '7':
            restore_credentials()
        elif choice == '8':
            break
        else:
            print("Invalid option. Please try again.")

# Initialize database and run the program
init_db()
main_menu()
