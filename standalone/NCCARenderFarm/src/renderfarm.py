import paramiko
import stat
import os


class NCCA_RenderFarm(paramiko.SSHClient):
    def __init__(self, hostname, username, password, port=22):
        super().__init__()
        """Constructor Method"""
        # Set connection object to None (initial value)
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        """Connects to the sftp server and returns the sftp connection object"""
        try:
            # Get the sftp connection object
            self.connect(hostname=hostname, port=port, username=username, password=password)
        except Exception as err:
            raise Exception(err)
        finally:
            print(f"Connected to {hostname} as {username}.")

        self.root = self.open_sftp()

    def get_home(self):
        return self.root

    def disconnect(self):
        """Closes the sftp connection"""
        self.files.close()
        self.close()
        print(f"Disconnected from host")

    def list_dir(self, remote_path):
        is_hidden = lambda item: not item.startswith(".")

        """lists all the files and directories in the specified path and returns them"""
        try:
            return list(filter(is_hidden, self.root.listdir(remote_path)))

        except Exception as err:
            raise Exception(f"Failed to list directory {remote_path}: {err}")
        
    def is_dir(self, remote_path: str) -> bool:
        """
        Check if the given remote path is a directory.
        """
        try:
            # Get attributes of the remote path
            attributes = self.root.stat(remote_path)
            # Check if it's a directory
            return stat.S_ISDIR(attributes.st_mode)
        except FileNotFoundError:
            # File does not exist
            return False


    def upload(self, source_local_path, remote_path):
        """
        Uploads the source files from local to the sftp server.
        """

        try:
            print(
                f"uploading to [(remote path: {remote_path});(source local path: {source_local_path})]"
            )

            # Download file from SFTP
            self.put(source_local_path, remote_path)
            print("upload completed")

        except Exception as err:
            raise Exception(err)
        
    def download(self, remote_path, target_local_path):
        """
        Downloads the file from remote sftp server to local.
        Also, by default extracts the file to the specified target_local_path
        """

        try:
            print(
                f"downloading from [(remote path : {remote_path});(local path: {target_local_path})]"
            )

            # Create the target directory if it does not exist
            path, _ = os.path.split(target_local_path)
            if not os.path.isdir(path):
                try:
                    os.makedirs(path)
                except Exception as err:
                    raise Exception(err)

            # Download from remote sftp server to local
            self.get(remote_path, target_local_path)
            print("download completed")

        except Exception as err:
            raise Exception(err)
