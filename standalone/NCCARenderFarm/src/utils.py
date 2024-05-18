import os
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
    
def get_renderfarm(username, password):
    renderfarm = NCCA_RenderFarm.create("tete.bournemouth.ac.uk", username, password)

    return renderfarm