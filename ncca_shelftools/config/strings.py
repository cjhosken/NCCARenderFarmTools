# This file contains the text used for error dialogs, labels, and tooltips. 
# If you see a typo in any of those elements, it can be fixed here.

# ERROR DIALOG MESSAGES

NCCA_ERROR = {
    "title" : "NCCA Error",
    "message" : "Uh oh! An error occured. Please report a bug or contact the NCCA admin if this issue persists. {}"
}

NCCA_INVALID_LOGIN_ERROR = {
    "title" : "Login Error",
    "message" : "Invalid username or password. Please report a bug or contact the NCCA admin if this issue persists."
}

NCCA_CONNECTION_ERROR = {
    "title" : "Connection Error",
    "message" : "Connection to the NCCA Renderfarm failed. Please report a bug or contact the NCCA admin if this issue persists."
}

QUBE_EXE_ERROR = {
    "title" : "Qube Error",
    "message" : "Qube could not be found! Make sure that you have installed Qube from Apps Anywhere.  If you are on Linux, or this issue continues to occur, please report a bug or contact the NCCA admin."
}

QUBE_PY_ERROR = {
    "title" : "Qb Error",
    "message" : "Qb could not be found! Make sure that you have installed Qube from Apps Anywhere. If you are on Linux, or this issue continues to occur, please report a bug or contact the NCCA admin." 
}

IMAGE_ERROR = {
    "title" : "Image Error",
    "message" : "Error converting {} to .png"
}


# NON-ERROR DIALOG MESSAGES

NCCA_SUBMIT_MESSAGE = {
    "title" : "NCCA",
    "message" : "'{}' has been successfully added to the NCCA Renderfarm! \nID: {}"
}

OVERRIDE_DIALOG = {
    "title" : "Confirm Override",
    "message" : "A project with the job name '{}' already exists. Do you wish to override this project?"
}

DELETE_DIALOG = {
    "title" : "Confirm Delete",
    "message" : "Are you sure you want to delete '{}'?"
}


# LABELS
# These are the Labels that go alongside certain elements
NCCA_LOGIN_DIALOG_TITLE = "NCCA Renderfarm Login"
NCCA_LOGIN_USERNAME_LABEL = "Username:"
NCCA_LOGIN_PASSWORD_LABEL = "Password:"
NCCA_LOGIN_SAVE_LABEL = "Save Info"
NCCA_LOGIN_LOGIN_LABEL = "Login"

NCCA_VIEWER_DIALOG_TITLE = "NCCA Renderfarm Viewer"
NCCA_VIEWER_ACTION_OPEN_LABEL = "Open"
NCCA_VIEWER_ACTION_DOWNLOAD_LABEL = "Download"
NCCA_VIEWER_ACTION_DELETE_LABEL = "Delete"
NCCA_VIEWER_FILE_PROMPT="Save File As"
NCCA_VIEWER_FOLDER_PROMPT="Select Destination Folder"

NCCA_SUBMIT_DIALOG_TITLE = "NCCA Renderfarm Submit Tool"
NCCA_SUBMIT_PROJECTNAME_LABEL="Project Name"
NCCA_SUBMIT_CPUCOUNT_LABEL="CPU Count"
NCCA_SUBMIT_PROJECTFOLDER_LABEL="Project Folder"
NCCA_SUBMIT_PROJECTFOLDER_CAPTION = "Choose Folder on Farm"

NCCA_SUBMIT_STARTFRAME_LABEL="Start Frame"
NCCA_SUBMIT_ENDFRAME_LABEL="End Frame"
NCCA_SUBMIT_BYFRAME_LABEL="By Frame"
NCCA_SUBMIT_CLOSE_LABEL="Close"
NCCA_SUBMIT_SUBMIT_LABEL="Submit"

NCCA_MAYASUBMIT_DIALOG_TITLE = "NCCA Renderfarm Maya Submit Tool"
NCCA_MAYASUBMIT_RENDERER_LABEL = "Active Renderer"
NCCA_MAYASUBMIT_CAMERA_LABEL = "Render Camera"
NCCA_MAYASUBMIT_OUTPUT_LABEL = "Output File"
NCCA_MAYASUBMIT_OUTPUT_DEFAULT = "/output/frame_###.exr"
NCCA_MAYASUBMIT_EXTRA_LABEL = "Extra Commands"

NCCA_HOUSUBMIT_DIALOG_TITLE = "NCCA Renderfarm Houdini Submit Tool"
NCCA_HOUSUBMIT_ROP_LABEL = "Select ROP"

# TOOLTIPS
# Tooltips are the messages that are displayed when you hover over something. They're often used to give a desecription of what something does.
NCCA_SUBMIT_PROJECTNAME_TOOLTIP = "The name of the project as it will appear on the Qube GUI."
NCCA_SUBMIT_CPUCOUNT_TOOLTIP = "Number of CPUs to use, please be respectful of others and only use high numbers if farm is empty."
NCCA_SUBMIT_PROJECTFOLDER_TOOLTIP = "Select the project folder to upload. Make sure all the files needed for rendering are relatively referenced by the file in this folder."
NCCA_SUBMIT_STARTFRAME_TOOLTIP = "Start frame for rendering, set from settings but can be changed here."
NCCA_SUBMIT_ENDFRAME_TOOLTIP = "End frame for rendering, set from settings but can be changed here."
NCCA_SUBMIT_BYFRAME_TOOLTIP = "Frame step for rendering, set from settings but can be changed here."
NCCA_SUBMIT_CLOSE_TOOLTIP = "Close the submit dialog."
NCCA_SUBMIT_SUBMIT_TOOLTIP = "Submit job to the NCCA Renderfarm."

# MAYA TOOLTIPS
NCCA_MAYASUBMIT_RENDERER_TOOLTIP = "The active renderer to use on the farm."
NCCA_MAYASUBMIT_CAMERA_TOOLTIP = "The camera used for rendering."
NCCA_MAYASUBMIT_OUTPUT_TOOLTIP = "The file path in which rendered frames will be saved as. This will be saved on the farm."
NCCA_MAYASUBMIT_EXTRA_TOOLTIP = "Extra commands to be added verbatim to the render call."

# HOUDINI TOOLTIPS
NCCA_HOUSUBMIT_ROP_TOOLTIP = "Select the output ROP to render, these will be either in the /shop or /stage level"



# LINKS

INFO_WEB_LINK = "https://github.com/cjhosken/NCCARenderFarmTools"