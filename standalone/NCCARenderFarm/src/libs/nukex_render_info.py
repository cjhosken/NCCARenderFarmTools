import nuke
import sys

def main(nuke_script_path):
    # Your script logic here
    print("Local path:", nuke_script_path)
    # Set the path to your Nuke script
    # Read the Nuke script without opening it in the GUI
    nuke.scriptReadFile(nuke_script_path)

    # Access and manipulate the nodes using Nuke's Python API
    # For example, to print all nodes:
    for node in nuke.allNodes():
        print(node.name())

    # Generate JSON data
    json_data = {
        "NCCA_RENDERFARM": {
                "frame_start": 0,
                "frame_end": 10,
                "frame_step": 120
        }
    }

    # Print JSON data
    print(json.dumps(json_data, indent=4))

if __name__ == "__main__":
    nuke_script_path = sys.argv[1]
    main(nuke_script_path)
