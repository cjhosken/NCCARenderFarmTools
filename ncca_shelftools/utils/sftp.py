import os, stat

def sftp_exists(sftp=None, remote_path=""):
    """
    Check if a file or directory exists on the remote SFTP server.

    Args:
    - sftp: SFTP connection object (not used in this placeholder function).
    - remote_path (str): Path to the remote file or directory.

    Returns:
    - bool: True if the file or directory exists, False otherwise.

    This is a placeholder function that always returns True.
    """
    try:
        sftp.stat(remote_path)
    except:
        return False
    return True

def sftp_isdir(sftp=None, remote_path=""):
    """
    Check if a path on the remote SFTP server is a directory.

    Args:
    - sftp: SFTP connection object (not used in this placeholder function).
    - remote_path (str): Path to the remote file or directory.

    Returns:
    - bool: True if the path is a directory, False otherwise.

    This is a placeholder function that always returns False.
    """
    try:
        return stat.S_ISDIR(sftp.stat(remote_path).st_mode)
    except FileNotFoundError:
        return False

def sftp_isfile(sftp=None, remote_path=""):
    """
    Check if a path on the remote SFTP server is a file.

    Args:
    - sftp: SFTP connection object (not used in this placeholder function).
    - remote_path (str): Path to the remote file or directory.

    Returns:
    - bool: True if the path is a file, False otherwise.

    This is a placeholder function that always returns False.
    """
    try:
        return stat.S_ISREG(sftp.stat(remote_path).st_mode)
    except FileNotFoundError:
        return False

def sftp_download(sftp=None, remote_path="", local_path=""):
    """
    Download a file or directory from the remote SFTP server to the local machine.

    Args:
    - sftp: SFTP connection object.
    - remote_path (str): Path to the remote file or directory.
    - local_path (str): Path to save the downloaded file or directory locally.
    """
    # Ensure the SFTP connection object is valid
    if sftp is None:
        raise ValueError("SFTP connection object cannot be None.")

    try:
        # Check if the remote path is a directory
        if sftp_isdir(sftp, remote_path):  # Directory mode check
            # If it's a directory, create the local directory
            os.makedirs(local_path, exist_ok=True)
            
            # List contents of the remote directory
            for item in sftp.listdir(remote_path):
                remote_item_path = os.path.join(remote_path, item)
                local_item_path = os.path.join(local_path, item)
                
                # Recursively download each item
                sftp_download(sftp, remote_item_path, local_item_path)
        else:
            # If it's a file, download it
            sftp.get(remote_path, local_path)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def sftp_upload(sftp=None, local_path="", remote_path=""):
    """
    Recursively upload a file or directory from the local machine to the remote SFTP server.

    Args:
    - sftp: SFTP connection object.
    - local_path (str): Path to the local file or directory.
    - remote_path (str): Path to save the uploaded file or directory on the remote server.
    """
    # Check if the local path is a directory
    if os.path.isdir(local_path):
        # Ensure the remote directory exists
        try:
            sftp.mkdir(remote_path)
        except IOError:
            # Directory already exists or error occurred (skip creating)
            pass

        # Iterate over the directory contents
        for item in os.listdir(local_path):
            local_item_path = os.path.join(local_path, item)
            remote_item_path = os.path.join(remote_path, item).replace("\\", "/")

            # Recursively upload each file or directory
            sftp_upload(sftp, local_item_path, remote_item_path)
    else:
        # Upload the file
        sftp.put(local_path, remote_path)

def sftp_delete(sftp, remote_path):
    """
    Recursively delete a file or directory on the remote SFTP server.

    Args:
    - sftp: SFTP connection object.
    - remote_path (str): Path to the remote file or directory to delete.
    """
    try:
        if sftp_isdir(sftp, remote_path):
            # If it's a directory, list all its contents
            for item in sftp.listdir(remote_path):
                item_path = remote_path + "/" + item
                sftp_delete(sftp, item_path)  # Recursively delete each item
            
            # After all contents are deleted, remove the directory itself
            sftp.rmdir(remote_path)
        else:
            # If it's a file, delete it
            sftp.remove(remote_path)
    except IOError as e:
        print(f"Failed to delete {remote_path}: {e}")

def sftp_setup(sftp=None, username=""):
    """
    Sets up the SFTP environment for the given username by ensuring the necessary directories exist and uploading a payload script.

    Directory Structure:

    /home/
        username/
            .ncca/
            farm/
                projects/
                output/
    
    Args:
        sftp: SFTP client object used to perform SFTP operations.
        username (str): The username for which the SFTP environment is being set up.
    """
    
    # Define the home directory and NCCA script path for the given username
    FARM_HOME = f"/home/{username}"
    NCCA_SCRIPT_PATH = FARM_HOME + "/.ncca"

    # Check if the NCCA script path exists, and delete it if it does
    if sftp_exists(sftp, NCCA_SCRIPT_PATH):
        sftp_delete(sftp, NCCA_SCRIPT_PATH)

    # Upload the payload script to the NCCA script path
    sftp_upload(sftp, "../payload", NCCA_SCRIPT_PATH)

    # Define the farm directory and its subdirectories
    FARM_DIR = FARM_HOME + "/farm"
    PROJECT_DIR = FARM_DIR + "/projects"
    OUTPUT_DIR = FARM_DIR + "/output"

    # Check if the farm directory exists, and create it if it does not
    if not sftp_exists(FARM_DIR):
        sftp.mkdir(FARM_DIR)

    # Check if the project directory exists, and create it if it does not
    if not sftp_exists(PROJECT_DIR):
        sftp.mkdir(PROJECT_DIR)
    
    # Check if the output directory exists, and create it if it does not
    if not sftp_exists(OUTPUT_DIR):
        sftp.mkdir(OUTPUT_DIR)