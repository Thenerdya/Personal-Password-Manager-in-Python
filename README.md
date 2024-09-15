🔐 Personal Password Manager in Python
This project is a Password Manager built with Python to store, retrieve, and generate passwords securely. The program uses encryption and hashing to protect sensitive information like credentials and allows easy management of passwords via a command-line interface.

Features
User Authentication: Master password protection with bcrypt hashing.
Password Encryption: AES encryption using cryptography to secure stored passwords.
Secure Storage: Store website, username, and passwords in an SQLite database.
Password Generation: Generate secure random passwords.
Password Strength Check: Evaluate the strength of new passwords.
Credential Management: Add, update, delete, and view credentials securely.
Backup & Restore: Easily back up and restore encrypted credentials.
Technologies Used
bcrypt: For hashing the master password.
cryptography: For encrypting and decrypting the stored passwords.
SQLite: To store the credentials in an encrypted database.
secrets: To generate secure random passwords.
Installation
Clone the repository:

bash
Copy code
git clone https://github.com/yourusername/password-manager.git
cd password-manager
Install dependencies:

bash
Copy code
pip install bcrypt cryptography
Run the program:

bash
Copy code
python password_manager.py
Usage
Set up a master password for the password manager.
Use the menu to add, view, update, or delete credentials.
Generate a new password when adding a credential or leave it blank to use a custom password.
Use the backup and restore options to save and reload your encrypted credential data.

Contribution
You can fix this project, raise issues, or submit pull requests. Contributions are welcome!
