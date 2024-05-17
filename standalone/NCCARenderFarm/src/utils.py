import os
from dotenv import load_dotenv
from renderfarm import NCCA_RenderFarm

def get_os_type():
    """Get the operating system type."""
    if os.name == 'posix':
        return 'linux'
    elif os.name == 'nt':
        return 'windows'
    else:
        return 'other'

def get_user_name():
    """Get the user name depending on the operating system."""
    if get_os_type() == 'linux':
        return os.getlogin()  # On Linux, use os.getlogin()
    elif get_os_type() == 'windows':
        return os.environ.get('USERNAME')  # On Windows, use the USERNAME environment variable
    else:
        return None  # Return None for other operating systems
    
def get_renderfarm():
    dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
    load_dotenv(dotenv_path)

    username = os.environ.get("USERNAME")
    password = os.environ.get("PASSWORD")

    renderfarm = NCCA_RenderFarm("tete.bournemouth.ac.uk", username, password)

    return renderfarm