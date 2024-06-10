import nuke
import sys
import json
import traceback

if __name__ == "__main__":
    # Check if the script is being run directly
    if len(sys.argv) != 2:
        sys.exit(1)

    local_path = sys.argv[1]
    try:
        # Read the Nuke script without opening it in the GUI
        nuke.scriptReadFile(local_path)

        # Access and manipulate the nodes using Nuke's Python API
        write_nodes = [node for node in nuke.allNodes() if node.Class() == 'Write']

        global_start=first
        global_end=last
        

        # Extract information from write nodes
        write_nodes_info = []
        for node in write_nodes:

            write_node_info = {
                "path": node.name(),
                "frame_start": node.first if node.use_limit else global_start,
                "frame_end": node.last if node.use_limit else global_end,
            }
            write_nodes_info.append(write_node_info)

        # Generate JSON data
        json_data = {
            "NCCA_RENDERFARM": {
                "write_nodes": write_nodes_info
            }
        }

        # Print JSON data
        print(json.dumps(json_data, indent=4))
    except Exception as e:
        print(e)
