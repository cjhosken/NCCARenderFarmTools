# This file contains the general configuration variables for the app.
import os

APPLICATION_NAME = "NCCA Farmer 2024"
# APPLICATION_VERSION Should only really be changed on large rewrites.
APPLICATION_VERSION = "1.0.0"

# In terms of contributing to the code, anyone is free to. Just try not to break anything.
# If you feel that you've contributed large amounts to the project, feel free to add yourself to APPLICATION_AUTHORS.
# This is done on a trust basis. Please don't remove other people's names without their permission.

APPLICATION_AUTHORS = ["Christopher Hosken"]
# Description of the application.
APPLICATION_DESCRIPTION = "A cross-platform tool that allows users to interact with the NCCA Renderfarm."

# The message that is first displayed when the application is run from a command line terminal.
APPLICATION_CLI_HEADER = f"""{APPLICATION_NAME}
{APPLICATION_VERSION}
{APPLICATION_DESCRIPTION}
Written by: {APPLICATION_AUTHORS}
"""

HOME_DIR = os.path.expanduser("~")
NCCA_DIR = os.path.join(HOME_DIR, ".ncca")
NCCA_KEY_PATH = os.path.join(HOME_DIR, ".ncca_key")
NCCA_ENV_PATH = os.path.join(HOME_DIR, ".ncca_env")

