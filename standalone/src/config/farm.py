# This file contains the configuration variables that relate to the NCCA Renderfarm.

# The address and port that the renderfarm server is hosting from.
RENDERFARM_ADDRESS = "tete.bournemouth.ac.uk"
RENDERFARM_PORT = 22

# The number of connection attemps before raising a connection failed exception.
MAX_CONNECTION_ATTEMPTS = 3


# The NCCA Renderfarm has two "root" (home) paths.
#
# The RENDERFARM_ROOT (/home) is used for the general managing of files. (eg: download, upload, delete, view, etc.)
# 
# The RENDERFARM_RENDER_ROOT (/render) is the path that Qube uses for rendering.
# /render has the same information as /home, but is only used for rendering with Qube.
#
# Any file managing should be done with RENDERFARM_ROOT, and any paths used with Qube should start with RENDERFARM_RENDER_ROOT
RENDERFARM_ROOT="/home"
RENDERFARM_RENDER_ROOT="/render"

# The actual farm directory for users is /home/user. However, Maya, Houdini and other softwares create their own folders and files in /home/user.
# The purpose of RENDERFARM_FARM_DIR is to go one directory lower (/home/user/farm), so that all the extra folders can be forgotten. 
# This is also to avoid non-techy users messing with generated files.
RENDERFARM_FARM_DIR = "farm"
# NCCA_PACKAGE_DIR is hidden in /home/user, it holds files that need to be run off the farm. (eg: source.sh)
# NCCA_PACKAGE_DIR is reuploaded every time a user starts the application. This is so that updates to the files will be registered.
NCCA_PACKAGE_DIR = ".ncca"

# RENDER_FARM_PROJECT_DIR is the default directory to save uploaded projects to.
RENDERFARM_PROJECT_DIR="projects"
# RENDERFARM_OUTPUT_DIR is the default directory for Maya and Blender to save to.
RENDERFARM_OUTPUT_DIR="output"

# FARM_CPUS is the number of available cpus on the renderfarm.
FARM_CPUS = 8
# DEFAULT_CPU_USAGE is the default number of cpus that a user has when submitting a job.
DEFAULT_CPU_USAGE = 2

# How many milliseconds before the browser reloads files.
RENDERFARM_REFRESH_INTERVAL=30000