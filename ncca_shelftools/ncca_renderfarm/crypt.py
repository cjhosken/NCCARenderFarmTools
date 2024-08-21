# /ncca_shelftools/ncca_renderfarm/crypt.py contains all the necessary functions for loading, saving, and removing encrypted login details.
# It stores the encrypted environment variables (username, password) in NCCA_ENV_PATH
# The encryption key is stored in NCCA_KEY_PATH
# NCCA_ENV_PATH and NCCA_KEY_PATH can be found in /ncca_shelftools/config/__init__.py

import json
from config import *
from utils import *

install(["cryptography"])
from cryptography.fernet import Fernet


def load_saved_credentials(key):
    """
    Load and decrypt saved credentials.

    Args:
        key (bytes): The key used for decryption.

    Returns:
        dict: The decrypted credentials as a dictionary, or None if an error occurs or file doesn't exist.
    """
    
    # Check if the credentials file exists
    if not os.path.exists(NCCA_ENV_PATH):
        return None
    
    # Read the encrypted credentials from the file
    with open(NCCA_ENV_PATH, "rb") as file:
        encrypted_credentials = file.read()
    
    try:
        # Decrypt the credentials
        decrypted_data = decrypt_credentials(key, encrypted_credentials)
        # Load the JSON data from the decrypted credentials
        credentials = json.loads(decrypted_data.decode())
        return credentials
    except Exception as e:
        # Return 'None' if decryption fails
        return None

def decrypt_credentials(key, encrypted_credentials):
    """
    Decrypt username and password using Fernet symmetric decryption.

    Args:
        key (bytes): The key used for decryption.
        encrypted_credentials (bytes): The encrypted credentials.

    Returns:
        bytes: The decrypted data.
    """
    # Initialize the Fernet cipher suite with the provided key
    cipher_suite = Fernet(key)
    # Decrypt the encrypted credentials
    decrypted_data = cipher_suite.decrypt(encrypted_credentials)
    return decrypted_data

def save_user_info(key, username, password):
    """
    Save user info (username and password) to a secure location with encryption.

    Args:
        key (bytes): The key used for encryption.
        username (str): The username to save.
        password (str): The password to save.
    """
    # Encrypt the user credentials
    encrypted_credentials = encrypt_credentials(key, username, password)
    
    # Write the encrypted credentials to the file
    with open(NCCA_ENV_PATH, "wb") as file:
        file.write(encrypted_credentials)

def remove_user_info():
    """
    Remove the saved user info file.
    """
    # Check if the credentials file exists and remove it
    if os.path.exists(NCCA_ENV_PATH):
        os.remove(NCCA_ENV_PATH)

def encrypt_credentials(key, username, password):
    """
    Encrypt username and password using Fernet symmetric encryption.

    Args:
        key (bytes): The key used for encryption.
        username (str): The username to encrypt.
        password (str): The password to encrypt.

    Returns:
        bytes: The encrypted data.
    """
    # Initialize the Fernet cipher suite with the provided key
    cipher_suite = Fernet(key)
    # Create a dictionary of the user credentials
    credentials = {
        'username': username,
        'password': password
    }
    # Convert the credentials to a JSON string
    plaintext = json.dumps(credentials)
    # Encrypt the JSON string
    encrypted_data = cipher_suite.encrypt(plaintext.encode())
    return encrypted_data

def generate_key():
    """
    Generate a new encryption key and save it to the specified path.
    """
    
    # Check if the key file already exists
    if not os.path.exists(NCCA_KEY_PATH):
        # Generate a new Fernet encryption key
        key = Fernet.generate_key()

        # Write the generated key to the specified file
        with open(NCCA_KEY_PATH, "wb") as key_file:
            key_file.write(key)

def load_key():
    """
    Load the encryption key from the specified path.

    Returns:
        bytes: The encryption key.
    """
    # Read and return the encryption key from the key file
    with open(NCCA_KEY_PATH, "rb") as key_file:
        return key_file.read()
