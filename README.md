# NCCA RenderFarm Tools
The NCCA Renderfarm Tools allow users to interact with the NCCA Renderfarm. The shelf tools can be run from inside DCCs (Digital Content Creators). Currently, the shelf tools only support:

 - Maya
    - Maya Software Render
    - ~~Arnold (CPU)~~ (Watermarked)
    - ~~VRay (CPU)~~ (License Errors)

 - Houdini
    - Mantra
    - Karma (CPU)


## Installation
To install the shelf tools, navigate to `shelf_tools/` and run either `linux_setup.sh` or `windows_setup.sh`. The tools should then install into all Houdini and Maya distributions.

*Be aware that if you're using Houdini on windows, you'll need to run the setup script each time you install Houdini from Apps Anywhere.*

## Usage
There are 3 tools in the shelf tools. For some of the tools you will be prompted with a login page. Enter your Bournemouth University ID and password. You can also choose to save your info so you don't have to retype it each time you use the tools.

### Launch Qube!
This launches Qube, a graphical interface that lets you see jobs that have been submitted to the NCCA Renderfarm. It's recommended to launch Qube after you submit a job to see if everything is working correctly.

### Submit Job
Submitting a job will submit the current project you have open in either Houdini or Maya. 

Project Name: The name of your project that will be seen on the renderfarm.
CPU Count: How many CPUs to use for rendering. You can use all, but please be considerate of others using the renderfarm.
Project Folder: The folder that will be uploaded to the renderfarm. Make sure that all your files (including the one you have open) are located inside the project folder. You cannot submit a job without specifying a project folder.

Start, End, Step Frames: Specify what frame to start and end at. Frame stepping will render every nth frame.

#### Maya:

Active Renderer: Specify what render engine to use. "file" will use the one specified by the opened file.
Render Camera: Specify what camera to use for rendering.

Output file: The output file path. The path begins at your farm folder.

Extra Commands: Extra commands to use for controlling your renders.

#### Houdini:

Select ROP: Select the ROP node to use for rendering.


### View Farm
Launching the farm viewer will let you see your files on the NCCA Renderfarm. You can download and delete files. 

Right click on an item to action it.
Double click on images to view them. EXR files are supported.

*You can also access your files from Linux. See the videos by Jon Macey on how to do that.*

## Issues
The app can be buggy at times, so do be patient. If you feel that It's slowing down or something unusual is happening. Try restarting. If it keeps happening, report a bug either through the UI or at https://github.com/cjhosken/NCCARenderFarmTools/issues.

It's very important you report any bugs you face otherwise they likely will never get fixed. When you report a bug, try and assign a label to it. Do not create any new labels.

## Development
This project is open source, which means anyone can participate in development! I hope that this tool will be passed along by students, and maintained by them while they're at University.

If you wish to get involved with development, read [DEVEL.md](DEVEL.md)

## Contributors
This software was first developed by Christopher Hosken in the summer of 2024.

Other Contributors include:
- Jon Macey (Insipred Code)


*If you have contributed to the project, feel free to add yourself to the list of contributors.*