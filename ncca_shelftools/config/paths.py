import os, platform

OPERATING_SYSTEM = platform.system().lower()
HOME_DIR = os.path.expanduser("~")

NCCA_DIR = os.path.join(HOME_DIR, ".ncca")
NCCA_KEY_PATH = os.path.join(HOME_DIR, ".ncca_key")
NCCA_ENV_PATH = os.path.join(HOME_DIR, ".ncca_env")
