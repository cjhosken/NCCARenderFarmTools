# NCCA RenderFarm Tools

The NCCA RenderFarm Tools provide seamless integration with the NCCA Renderfarm, allowing users to submit and manage rendering tasks directly from their preferred Digital Content Creation (DCC) software. Currently, these tools support:

### Supported Software
- **Maya**
  - Maya Software Render
  - ~~Arnold (CPU)~~ (Watermarked)
  - ~~VRay (CPU)~~ (License Issues)

- **Houdini**
  - Mantra
  - Karma (CPU)

## Installation

To install the shelf tools:

1. Navigate to the `shelf_tools/` directory.
2. Run the appropriate setup script:
   - **Linux**: `linux_setup.sh`
   - **Windows**: `windows_setup.sh`

The tools will be installed across all Houdini and Maya distributions on your system.

> **Note:** If you're using Houdini on Windows, you must run the setup script each time you install Houdini via Apps Anywhere.

## Usage

### Overview
The NCCA RenderFarm Tools include three primary tools. For certain operations, you may be prompted to log in using your Bournemouth University ID and password. You can opt to save your credentials to avoid re-entering them each time.

### Tool Descriptions

#### 1. Launch Qube!
This tool launches the Qube! graphical interface, which allows you to monitor jobs submitted to the NCCA Renderfarm. It is recommended to launch Qube! after submitting a job to ensure everything is functioning correctly.

#### 2. Submit Job
This tool submits your current project from either Houdini or Maya to the renderfarm.

- **Project Name**: The name that will identify your project on the renderfarm.
- **CPU Count**: The number of CPUs to allocate for rendering. While you may use all available CPUs, please be considerate of others using the renderfarm.
- **Project Folder**: The directory containing all files related to your project. Ensure all necessary files, including the one currently open, are within this folder. A project folder must be specified to submit a job.
- **Frame Range**:
  - **Start Frame**: The frame to begin rendering.
  - **End Frame**: The frame to end rendering.
  - **Step Frames**: The interval at which frames will be rendered (e.g., every 2nd frame).

**Maya-Specific Options:**

- **Active Renderer**: The render engine to use. Selecting "file" will default to the renderer specified in the open file.
- **Render Camera**: The camera to be used for rendering.
- **Output File**: The output path for rendered files, relative to your farm folder.
- **Extra Commands**: Additional commands for advanced render control.

**Houdini-Specific Options:**

- **Select ROP**: The ROP node to use for rendering.

#### 3. View Farm
This tool opens the farm viewer, allowing you to manage your files on the NCCA Renderfarm. You can download, delete, or view files directly.

- **Actions**:
  - **Right-click**: Opens a context menu with available actions for the selected item.
  - **Double-click**: Views images, including support for EXR files.

> **Tip:** You can also access your files from Linux. Check out the tutorial videos by Jon Macey for more details.

## Troubleshooting

The tools may occasionally encounter bugs or performance issues. If you experience slowdowns or unexpected behavior:

1. **Restart the Tool**: This often resolves minor issues.
2. **Report Bugs**: If problems persist, please report them at [NCCA RenderFarm Tools Issues](https://github.com/cjhosken/NCCARenderFarmTools/issues).

> **Important:** Reporting bugs ensures they are addressed in future updates. When submitting a bug report, please assign an appropriate label. Avoid creating new labels.

## Development

The NCCA RenderFarm Tools is an open-source project, inviting contributions from the community. Students are encouraged to maintain and improve the tools during their time at Bournemouth University.

If you're interested in contributing, please refer to [DEVEL.md](DEVEL.md) for guidelines and instructions.

## Contributors

This project was initiated by Christopher Hosken during the summer of 2024.

**Other Contributors**:
- Jon Macey (Inspired Code)

If you've contributed to this project, feel free to add your name to the list of contributors.