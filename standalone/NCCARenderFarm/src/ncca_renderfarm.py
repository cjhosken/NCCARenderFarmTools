from config import *

# Custom exceptions to be caught in the login page.
class NCCA_RenderfarmFailedConnection(Exception):
    """Raised when the user is unable to connect to the SFTP server
    If this is a recurring issue, check that RENDERFARM_ADDRESS and RENDERFARM_PORT are correct in config.py
    Otherwise, the server may not be accessible from the network
    """
    pass

class NCCA_RenderfarmInvalidLogin(Exception):
    """Raised when the user inputs an invalid username and password"""
    pass

class NCCA_RenderFarm(paramiko.SSHClient):
    def __init__(self, username, password):
        """Connect to the remote SFTP server"""
        super().__init__()

        self.username = username
        self.password = password

        # Multiple attemps because the program does not always connect to the renderfarm first try.
        for attempt in range(MAX_CONNECTION_ATTEMPTS):
            try:
                self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.connect(RENDERFARM_ADDRESS, port=RENDERFARM_PORT, username=self.username, password=self.password)
                self.sftp = self.open_sftp()
        
            except paramiko.AuthenticationException:
                raise NCCA_RenderfarmInvalidLogin()

            except (paramiko.SSHException, socket.gaierror) as e:
                if attempt >= MAX_CONNECTION_ATTEMPTS - 1:
                    raise NCCA_RenderfarmFailedConnection()

    def stat(self, remote_path):
        """Returns the stat of the given path on the remote SFTP server"""
        return self.sftp.stat(remote_path)

    def listdir(self, remote_path):
        """Returns a list of all children of the directory on the remote SFTP server"""
        return self.sftp.listdir(remote_path)
    
    def isdir(self, remote_path):
        """Checks if the given path is a directory on the remote SFTP server"""
        file_stat = self.sftp.stat(remote_path)
        return paramiko.stat.S_ISDIR(file_stat.st_mode)
            
    def exists(self, remote_path):
        """Checks if the given path exists on the remote SFTP server"""
        try:
            _ = self.sftp.stat(remote_path)
            return True
        except Exception:
            return False

    def upload(self, source_local_path, remote_path):
        """Uploads the source files from local to the SFTP server"""
        self.sftp.put(source_local_path, remote_path)

    def download(self, remote_path, target_local_path):
        """Downloads the file from remote SFTP server to local"""
        os.makedirs(os.path.dirname(target_local_path), exist_ok=True)
        self.sftp.get(remote_path, target_local_path)

    def delete(self, remote_path):
        """Deletes the file or directory from the remote SFTP server"""
        if self.exists(remote_path):
            if self.isdir(remote_path):
                self.sftp.rmdir(remote_path)
            else:
                self.sftp.remove(remote_path)

    def extract(self, remote_path):
        """TODO: Extracts a .zip or .tar on the remote SFTP server"""
        pass

    def compress(self, remote_path):
        """TODO: Compresses the remote directory into a .zip on the remote SFTP server"""
        pass