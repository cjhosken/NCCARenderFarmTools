# The config folder holds all the global variables used in the application.

import os, platform

# import the variables from other config files.
from .software import *
from .renderfarm import *
from .strings import *
from .environment import *

# Get the current operating system, this could be 'windows', 'linux', or 'darwin' (however darwin is not supported)
OPERATING_SYSTEM = platform.system().lower()

# On linux, home will default to /home/user/
# On windows, home will default to C:\Users\user\
# On windows in the NCCA Labs, home will default to H:\\bournemouth.ac.uk\data\student\home\FMC\user\ 

homeshare = os.getenv("HOMESHARE")

HOME_DIR = homeshare if homeshare is not None else os.path.expanduser("~")

# The NCCA_DIR is the where all the scripts are located
NCCA_DIR = os.path.join(HOME_DIR, ".ncca")

# The NCCA_KEY_PATH holds the key used for encryption. See /ncca_shelftools/ncca_renderfarm/login.py and /ncca_shelftools/ncca_renderfarm/crypt.py for more info.
NCCA_KEY_PATH = os.path.join(HOME_DIR, ".ncca_key")

# The NCCA_ENV_PATH holds the users encypted login info. See /ncca_shelftools/ncca_renderfarm/login.py and /ncca_shelftools/ncca_renderfarm/crypt.py for more info.
NCCA_ENV_PATH = os.path.join(HOME_DIR, ".ncca_env")