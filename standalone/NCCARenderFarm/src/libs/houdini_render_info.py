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
        pass
    try:
        rop_nodes = []

        # Iterate through all nodes in the scene
        for node in hou.node("/").allSubChildren():
            print(f"{node}: {node.type().category()}")
            if isinstance(node, hou.RopNode):
                # Add the name of the ROP node to the list
                rop_nodes.append(node.path())

        # Generate JSON data
        json_data = {
            "NCCA_RENDERFARM": {
                "rop_nodes": rop_nodes,
            }
        }

        # Print JSON data
        print(json.dumps(json_data, indent=4))

    except Exception as e:
        # Print the traceback of the exception
        print(e)
