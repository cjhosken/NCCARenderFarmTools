# This file contains the general configuration variables for the app strings.
# This includes default error messages, buttons, labels, etc.
#
# some files look like "{} is very cool". This because they're used with format() elsewhere in the script.
#
# eg: FACT="{} is so great!".format("Bournemouth")
#

# Message Boxes

MESSAGEBOX_DEFAULT_TITLE="NCCA Message Box"
MESSAGEBOX_OK_DEFAULT_TEXT="Ok"
MESSAGEBOX_YES_DEFAULT_TEXT="Yes"
MESSAGEBOX_NO_DEFAULT_TEXT="No"
MESSAGEBOX_CANCEL_DEFAULT_TEXT="Cancel"

MESSAGE_INFO_HEADER="NCCA Info | "
MESSAGE_INFO_CONFIRM_TEXT="Ok"

MESSAGE_WARNING_HEADER="NCCA Warning | "
MESSAGE_WARNING_CONFIRM_TEXT="Ok"

MESSAGE_FATAL_HEADER="NCCA Fatal | "
MESSAGE_FATAL_CONFIRM_TEXT="Quit"

MESSAGE_QUESTION_HEADER="NCCA Question | "
MESSAGE_QUESTION_YES_TEXT="Yes"
MESSAGE_QUESTION_NO_TEXT="No"

MESSAGE_OVERRIDE_HEADER="NCCA Override | "
MESSAGE_OVERRIDE_YES_TEXT="Yes"
MESSAGE_OVERRIDE_NO_TEXT="No"
MESSAGE_OVERRIDE_CANCEL_TEXT="Cancel"

# Custom Labels
MESSAGE_QUBE_LABEL = "Qube"
QB_IMPORT_ERROR_MESSAGE = "Make sure that you have installed Qube 7.5.2 (Client Only) from Apps Anywhere before starting the application." 

# Local DCC Errors:

NO_HOUDINI_TITLE="Houdini"
NO_HOUDINI_LABEL="Hython could not be found on this machine. Proceeding without Houdini scene info."

NO_NUKEX_TITLE="NukeX"
NO_NUKEX_LABEL="NukeX could not be found on this machine. Proceeding without NukeX scene info."

NO_KATANA_TITLE="Katana"
NO_KATANA_LABEL="Katana could not be found on this machine. Proceeding without Katana scene info."

NO_MAYA_TITLE=""
NO_MAYA_LABEL="Mayapy could not be found on this machine. Proceeding without Maya scene info."

UNSUPPORTED_SOFTWARE_TITLE = "Unsupported"
UNSUPPORTED_SOFTWARE_LABEL="{} is not supported. Please choose a supported software file. "

MESSAGE_CONTACT_LABEL = "If this issue persists, please report a bug at https://github.com/cjhosken/NCCARenderFarmTools/issues, or contact a member of the NCCA."




# Dialog Labels

RENAME_PLACEHOLDER = "Rename"
RENAME_EXISTING_TITLE = "Rename"
RENAME_EXISTING_LABEL = "{} already exists."


WIPED_TITLE="Wiped"
WIPED_LABEL = "{} has been wiped!"


UPLOAD_FOLDERS_TITLE="Select folder(s) to upload"
UPLOAD_FILES_TITLE="Select file(s) to upload"


DELETE_CONFIRM_TITLE="Confirm Deletion"
DELETE_CONFIRM_LABEL="Are you sure you want to wipe {}? This will delete ALL files."
DELETE_CONFIRM_GENERAL_LABEL="Are you sure you want to delete the select item(s)"


DOWNLOAD_DESTINATION_TITLE="Select destination folder for download"
DOWNLOAD_DESTINATION_CAPTION=""
DOWNLOAD_DESTINATION_FILTER="All Files (*)"

PATH_EXISTING_TITLE="Path"
PATH_EXISTING_LABEL="{} already exists."
PATH_EXISTING_OVERRIDE_LABEL="{} already exists. What do you want to do?"


MOVE_CONFIRM_TITLE="Move"
MOVE_CONFIRM_LABEL="Are you suree you want to move {} to {}?"
MOVE_CONFIRM_GENERAL_LABEL="Are you sure you want move the selected items to {}?"



# File Browsers
DIR_SELECT_LABEL = "Select Directory"
DCC_FILE_SELECT_LABEL = "Select Application File"
DCC_FILE_FILTER="All Files (*)"


FOLDER_DIALOG_PLACEHOLDER="Folder Name"
FOLDER_DIALOG_DEFAULT="Folder"
FOLDER_DIALOG_CONFIRM="Add Folder"

INPUT_DIALOG_PLACEHOLDER="Input Text"
INPUT_DIALOG_DEFAULT=""
INPUT_DIALOG_CONFIRM_TEXT="Submit"


# Farm Actions
LAUNCH_QUBE_ACTION_LABEL="Qube!"
NEW_FOLDER_ACTION_LABEL="New folder"
UPLOAD_FILES_ACTION_LABEL="Upload files"
UPLOAD_FOLDERS_ACTION_LABEL="Upload folders"
SUBMIT_PROJECT_ACTION_LABEL="Submit project"

SUBMIT_RENDER_JOB_ACTION_LABEL="Submit Render Job"

OPEN_ACTION_LABEL="Open"
DOWNLOAD_ACTION_LABEL="Download"
RENAME_ACTION_LABEL="Rename"
DELETE_ACTION_LABEL="Delete"
RELOAD_ACTION_LABEL="Reload farm"
WIPE_ACTION_LABEL="Wipe farm"


# Login

LOGIN_WINDOW_SUBTITLE="Sign in to access your farm."
LOGIN_WINDOW_USERNAME_PLACEHOLDER="Username"
LOGIN_WINDOW_PASSWORD_PLACEHOLDER="Password"
LOGIN_WINDOW_KEEP_DETAILS_LABEL="Remember me"
LOGIN_WINDOW_LOGIN_BUTTON_TEXT="Login"


INVALID_CREDENTIALS_WARNING_TEXT="Invalid username or password."


# Widgets


QFLATBUTTON_DEFAULT_TEXT="Button"

QINPUT_PLACEHOLDER=INPUT_DIALOG_PLACEHOLDER
QINPUT_DEFAULT_TEXT=INPUT_DIALOG_DEFAULT



# Submit

QSUBMIT_DEFAULT_NAME="Submit Job"

SUBMIT_JOB_NAME_LABEL="Job Name"
SUBMIT_JOB_NAME_PLACEHOLDER="Enter Job Name"

SUBMIT_CPUS_LABEL="CPUs"
SUBMIT_JOB_PATH_LABEL="Job Path"
SUBMIT_JOB_PATH_PLACEHOLDER="Enter Job Path"
SUBMIT_FRAME_RANGE_LABEL="Frame Range"
SUBMIT_FRAME_START_LABEL="Frame Start"
SUBMIT_FRAME_END_LABEL="Frame End"
SUBMIT_FRAME_STEP_LABEL="Frame Step"

SUBMIT_EXTRA_COMMANDS_LABEL="Extra Commands"
SUBMIT_EXTRA_COMMANDS_PLACEHOLDER="Enter extra commands."

# DCC Jobs

BLENDER_JOB_TITLE="Submit Blender Job"
HOUDINI_JOB_TITLE="Submit Houdini Job"
MAYA_JOB_TITLE="Submit Maya Job"
NUKEX_JOB_TITLE="Submit NukeX Job"
KATANA_JOB_TITLE="Submit Katana Job"

# Renderer and output

JOB_RENDERER_LABEL="Renderer"
JOB_OUTPUT_LABEL="Output Path"
JOB_OUTPUT_PLACEHOLDER="Output Path"
JOB_OUTPUT_DEFAULT="/output/frame_####.exr"

# Custom DCC Widgets

HOUDINI_JOB_ROP_LABEL="ROP Node Path"
HOUDINI_JOB_ROP_PLACEHOLDER="Rop Node Path"
HODUINI_JOB_ROP_DEFAULT="/stage/usdrender_rop1"

MAYA_JOB_CAMERA_LABEL="Render Camera"
MAYA_JOB_CAMERA_PLACEHOLDER="Camera Name"
MAYA_JOB_CAMERA_DEFAULT="perspShape"

NUKEX_JOB_WRITE_LABEL="Write Node"
NUKEX_JOB_WRITE_PLACEHOLDER="Write Node Name"
NUKEX_JOB_WRITE_DEFAULT="Write1"

SUBMIT_BUTTON_SUBMIT_TEXT="Submit"
SUBMIT_BUTTON_CANCEL_TEXT="Cancel"

RENDERFARM_DIALOG_TITLE="Renderfarm"
RENDERFARM_SUBMITTED_LABEL="Job Submitted! {}"
RENDERFARM_ERROR_LABEL=f"Unable to submit job."


# Renderfarm Dialogs

RENDERFARM_COUNTING_FILES_LABEL="Counting files..."

RENDERFARM_PROGRESS_UPLOAD_TITLE="Upload"
RENDERFARM_PROGRESS_UPLOAD_LABEL="Uploading files..."
RENDERFARM_PROGRESS_UPLOAD_COMPLETE_TEXT="Files have been uploaded!"
RENDERFARM_PROGRESS_UPLOAD_ERROR_TEXT="Something went wrong in upload."

RENDERFARM_PROGRESS_DOWNLOAD_TITLE="Download"
RENDERFARM_PROGRESS_DOWNLOAD_LABEL="Downloading files..."
RENDERFARM_PROGRESS_DOWNLOAD_COMPLETE_TEXT="Files have been download!"
RENDERFARM_PROGRESS_DOWNLOAD_ERROR_TEXT="Something went wrong in download."

RENDERFARM_PROGRESS_DELETE_TITLE="Delete"
RENDERFARM_PROGRESS_DELETE_LABEL="Deleting files..."
RENDERFARM_PROGRESS_DELETE_COMPLETE_TEXT="Files have been deleted!"
RENDERFARM_PROGRESS_DELETE_ERROR_TEXT="Something went wrong in delete."