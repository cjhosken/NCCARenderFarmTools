# This file contains the general configuration variables for the app.
import os

APPLICATION_NAME = "NCCA Renderfarm 2024"
# APPLICATION_VERSION Should only really be changed on large rewrites.
APPLICATION_VERSION = "1.0.0"

# In terms of contributing to the code, anyone is free to. Just try not to break anything.
# If you feel that you've contributed large amounts to the project, feel free to add yourself to APPLICATION_AUTHORS.
# This is done on a trust basis. Please don't remove other people's names without permission.

APPLICATION_AUTHORS = ["Christopher Hosken"]
# Description of the application.
APPLICATION_DESCRIPTION = "A cross-platform tool that allows users to interact with the NCCA Renderfarm."

# The message that is first displayed when the application is run from a command line terminal.
APPLICATION_CLI_HEADER = f"""{APPLICATION_NAME}
{APPLICATION_VERSION}
{APPLICATION_DESCRIPTION}
Written by: {APPLICATION_AUTHORS}
"""

# Environment encryption variables. These can be changed, although there shouldn't be a need to.
#
# When the user chooses to save their details on sign in, their username and password is saved to the NCCA_ENVIRONMENT_PATH.
# To avoid having the details directly visible, they're encrypted.
NCCA_ENVIRONMENT_PATH = os.path.expanduser('~/.ncca')
# NCCA_ENCRYPTION_KEY_TEXT is how the details are encrypted. Different strings will result in different encryptions.
NCCA_ENCRYPTION_KEY_TEXT="NCCA_ENCRYPTION_KEY"

# NCCA_USERNAME_KEY_TEXT and NCCA_PASSWORD_KEY_TEXT are json keys for the details. For example:
#
# NCCA_USERNAME : "username"
# NCCA_PASSWORD : "password"
#
# This is for an extra layer of encryption.

NCCA_USERNAME_KEY_TEXT="NCCA_USERNAME"
NCCA_PASSWORD_KEY_TEXT="NCCA_PASSWORD"



# When downloading files f ro
LOCAL_TEMP_FOLDER = "tmp"