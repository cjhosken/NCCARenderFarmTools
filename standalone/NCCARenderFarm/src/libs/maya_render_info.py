import sys
import maya.standalone
from maya import cmds
import json

if __name__ == "__main__":
    # Check if the script is being run directly
    if len(sys.argv) != 2:
        sys.exit(1)

    local_path = sys.argv[1]

    try:
        # Initialize Maya standalone mode
        maya.standalone.initialize(name='python')
        
        # Open the Maya file
        cmds.file(local_path, open=True, force=True)
        
        # Get a list of all cameras in the scene
        all_cameras = cmds.ls(type='camera')
        
        # Filter out renderable cameras
        render_cameras = [camera for camera in all_cameras if cmds.getAttr(f"{camera}.renderable")]

        # Get the playback options
        start_frame = cmds.playbackOptions(q=True, animationStartTime=True)
        end_frame = cmds.playbackOptions(q=True, animationEndTime=True)
        step_frame = cmds.playbackOptions(q=True, by=True)

        json_data = {
            "NCCA_RENDERFARM": {
                "cameras": render_cameras,
                "start_frame": int(start_frame),
                "end_frame": int(end_frame),
                "step_frame": int(step_frame)
            }
        }

        print(json.dumps(json_data, indent=4))

    
    finally:
        # Clean up: close the scene and uninitialize Maya standalone
        cmds.file(force=True, new=True)
        maya.standalone.uninitialize()
