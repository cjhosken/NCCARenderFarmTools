# This file contains the global variables used for communicating with the renderfarm.

RENDERFARM_ADDRESS = "tete.bournemouth.ac.uk"
RENDERFARM_PORT = 22

MAX_CONNECTION_ATTEMPTS = 3

# DEFAULT_CPU_USAGE can be left at 2, but if more CPUS are added to the renderfarm make sure to increase MAX_CPUS.
DEFAULT_CPU_USAGE = 2
MAX_CPUS = 8

# HOUDINI_FARM_PATH and MAYA_FARM_PATH are paths to the software bins on the renderfarm.
HOUDINI_FARM_PATH = "/path/to/houdini"
MAYA_FARM_PATH = "/path/to/maya"
