from paramiko import *

from styles import MAX_CONNECTION_ATTEMPTS

class NCCA_Error(Exception):
    pass

class NCCA_RenderfarmConnectionFailed(NCCA_Error):
    pass

class NCCA_RenderfarmIncorrectLogin(NCCA_Error):
    pass


class NCCA_RenderFarm(SSHClient):
    def __init__(self, username, password):
        super().__init__()

        self.username = username
        self.password = password

        for attempt in range(MAX_CONNECTION_ATTEMPTS):
            try:
                self.set_missing_host_key_policy(AutoAddPolicy())
                self.connect("tete.bournemouth.ac.uk", port=22, username=self.username, password=self.password)
                self.sftp = self.open_sftp()
        
            except paramiko.AuthenticationException:
                raise NCCA_RenderfarmIncorrectLogin()

            except (paramiko.SSHException, socket.gaierror) as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < attempts - 1:
                    print("Retrying...")
                    time.sleep(1)  # Wait for a second before retrying
                else:
                    raise NCCA_RenderfarmConnectionFailed(f"Connection failed after {attempts} attempts")

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

    def delete(self, remote_path):
        """Deletes the file or directory from the remote SFTP server"""
        if self.exists(remote_path):
            if self.isdir(remote_path):
                self.sftp.rmdir(remote_path)
            else:
                self.sftp.remove(remote_path)

    def isdir(self, path):
        """
        Check if the given path is a directory.
        """
        try:
            file_stat = self.sftp.stat(path)
            return stat.S_ISDIR(file_stat.st_mode)
        except (IOError, FileNotFoundError):
            return False
        
    def exists(self, path):
        print("Checking existence of:", path)  # Print the path being checked
        try:
            file_stat = self.sftp.stat(path)
            print("File status:", file_stat)  # Print the file status if retrieved successfully
            return True
        except Exception as e:
            print("Error:", e)  # Print any exceptions that occur
            return False

    def stat(self, path):
        return self.sftp.stat(path)

    def listdir(self, path):
        return self.sftp.listdir(path)