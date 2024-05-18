import paramiko
import stat
import os

class InvalidCredentialsException(Exception):
    """Exception raised for invalid credentials."""
    pass

class ConnectionFailedException(Exception):
    """Exception raised for connection failures."""
    pass

class NCCA_RenderFarm(paramiko.SSHClient):
    def __init__(self, sftp):
        super().__init__()
        self.sftp = sftp

    @classmethod
    def create(cls, hostname, username, password, port=22):
        """Class method to create an instance and connect to the SFTP server"""
        client = cls(None)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            client.connect(hostname=hostname, port=port, username=username, password=password)
            sftp = client.open_sftp()
            print(f"Connected to {hostname} as {username}.")
            return cls(sftp)
        except paramiko.AuthenticationException as e:
            raise InvalidCredentialsException(f"Incorrect username or password")
        except (paramiko.SSHException, OSError) as err:
            raise ConnectionFailedException(f"Unable to connect to {hostname}: {err}")
        except Exception as err:
            print(f"Failed to connect to {hostname} as {username}: {err}")
            return None

    def disconnect(self):
        """Closes the SFTP connection"""
        if self.sftp:
            self.sftp.close()
        self.close()
        print("Disconnected from host")

    def list_dir(self, remote_path):
        """Lists all the visible files and directories in the specified path and returns them"""
        try:
            return [item for item in self.sftp.listdir(remote_path) if not item.startswith(".")]
        except Exception as err:
            raise Exception(f"Failed to list directory {remote_path}: {err}")

    def is_dir(self, remote_path: str) -> bool:
        """Checks if the given remote path is a directory"""
        try:
            attributes = self.sftp.stat(remote_path)
            return stat.S_ISDIR(attributes.st_mode)
        except FileNotFoundError:
            return False

    def upload(self, source_local_path, remote_path):
        """Uploads the source files from local to the SFTP server"""
        try:
            print(f"Uploading to [(remote path: {remote_path}); (source local path: {source_local_path})]")
            self.sftp.put(source_local_path, remote_path)
            print("Upload completed")
        except Exception as err:
            raise Exception(f"Upload failed: {err}")

    def download(self, remote_path, target_local_path):
        """Downloads the file from remote SFTP server to local"""
        try:
            print(f"Downloading from [(remote path: {remote_path}); (local path: {target_local_path})]")

            # Create the target directory if it does not exist
            os.makedirs(os.path.dirname(target_local_path), exist_ok=True)

            self.sftp.get(remote_path, target_local_path)
            print("Download completed")
        except Exception as err:
            raise Exception(f"Download failed: {err}")
