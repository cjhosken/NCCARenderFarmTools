import os, json
from cryptography.fernet import Fernet

def load_saved_credentials(key):
    """
    Load and decrypt saved credentials.
    """
    save_path = os.path.expanduser("~/.ncca_env")
        
    if not os.path.exists(save_path):
        return None
        
    with open(save_path, "rb") as file:
        encrypted_credentials = file.read()
        
    try:
        decrypted_data = decrypt_credentials(key, encrypted_credentials)
        credentials = json.loads(decrypted_data.decode())
        return credentials
    except Exception as e:
        print(f"Error decrypting credentials: {str(e)}")
        return None
        
def decrypt_credentials(key, encrypted_credentials):
    """
    Decrypt username and password using Fernet symmetric decryption.
    """
    cipher_suite = Fernet(key)
    decrypted_data = cipher_suite.decrypt(encrypted_credentials)
    return decrypted_data

def save_user_info(key, username, password):
    """
    Save user info (username and password) to a secure location with encryption.
    """
    encrypted_credentials = encrypt_credentials(key, username, password)
    save_path = os.path.expanduser("~/.ncca_env")
        
    with open(save_path, "wb") as file:
        file.write(encrypted_credentials)

def remove_user_info():
    save_path = os.path.expanduser("~/.ncca_env")
    if os.path.exists(save_path):
        os.remove(save_path)

def encrypt_credentials(key, username, password):
    """
    Encrypt username and password using Fernet symmetric encryption.
    """
    cipher_suite = Fernet(key)
    credentials = {
        'username': username,
        'password': password
    }
    plaintext = json.dumps(credentials)
    encrypted_data = cipher_suite.encrypt(plaintext.encode())
    return encrypted_data

def generate_key(key_path):
    """
    Generate a new encryption key and save it to ~/.ncca_key.
    """
    key = Fernet.generate_key()
    with open(key_path, "wb") as key_file:
        key_file.write(key)