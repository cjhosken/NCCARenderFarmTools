import sys
import hou
import json
import traceback

if __name__ == "__main__":
    # Check if the script is being run directly
    if len(sys.argv) != 2:
        sys.exit(1)

    local_path = sys.argv[1]

    try:
        # Initialize Houdini and open the scene file
        hou.hipFile.load(local_path)
    except Exception as e:
        # Print the traceback of the exception
        print(e)
        pass
    try:
        rop_nodes_info = []

        # Iterate through all nodes in the scene
        for node in hou.node("/").allSubChildren():
            if isinstance(node, hou.RopNode):
                # Get ROP node information
                rop_info = {
                    "path": node.path(),
                    "frame_start": int(node.parm("f1").eval()),
                    "frame_end": int(node.parm("f2").eval()),
                    "frame_step": int(node.parm("f3").eval())
                }
                # Add ROP node information to the list
                rop_nodes_info.append(rop_info)

        # Generate JSON data
        json_data = {
            "NCCA_RENDERFARM": {
                "rop_nodes": rop_nodes_info,
            }
        }

        # Print JSON data
        print(json.dumps(json_data, indent=4))
    except Exception as e:
        print(e)