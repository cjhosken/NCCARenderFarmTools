# NCCARenderFarmTools
A standalone application that interacts with the NCCA Renderfarm.

## Supported Software

The NCCA Renderfarm currently only supports:

 - ~~Maya 2023 Arnold~~ (no license)
 - ~~Maya 2023 VRay~~ (no license)
 - ~~Maya 2023 Renderman~~ (outdated)
 - Maya 2023 Software Render

<br>

 - Houdini 20.0.506 Mantra
 - Houdini 20.0.506 Karma CPU (XPU unspported)

## Installation
Before running the app, you'll need to install it. The first step is downloading the app from GitHub. 

Go to https://github.com/cjhosken/NCCARenderFarmTools, click `Code > Download ZIP`.

![Downloading](docs/images/download.png)

Choose a path to store the script, then extract it and dive inside.


NCCARenderFarm requires Qube to run. On linux, you dont need to do anything. However on Windows you need to install `Qube 7.5.2 Client Only` before running NCCARenderFarm.

### Building the Application

Run the setup script (either `windows_setup.bat`, `linux_setup.sh`). This will build the tools for you. It takes a couple minutes, so sit tight.

Once building is complete, you can then move the `NCCARenderFarmTools` folder to wherever you want. You won't need to run the setup script again.

### Storing the Application

When moving the `NCCARenderFarmTools` folder, there are recommended folders to store it in.

On Linux, storing it somewhere like `~/ncca/NCCARenderFarmTools` is a good place.

On Windows, storing it in your `H://` drive is recommended, as then you wont need to rebuild the tool for each lab machine you sign into. <br>
*Don't build the project in the H:// drive, as it takes MUCH longer. Build it in the C:// drive first and then move it acrros.*

### Running the Application

To the start the application, run either `launch.bat` (for windows) or `launch.sh` (for linux). The NCCARenderFarm application should then launch.

Be aware that this tool will only work on NCCA Lab machines, if you try and install and run it on your home machine, you will get Qube errors (and if you solve those, the renderfarm will not connect)


## Using NCCARenderFarmToools

The tool should be relatively straightforward to use.

### User Interface

The user interface is quite simple to get to grips with. When you first start the app, you'll be prompted with a sign in page. You'll need to enter your student (s#######) and your account password. You can choose to remember your account details so you need to sign in every time.

*Your details are saved and encrypted locally, so there's no need to worry about someone else gaining access to your account details.*


Once signed in, you'll see your farm file browser, and some action buttons at the top.

// TODO (Screenshot of UI)

#### Action Buttons

Plus : Upload a project to the farm and submit a job. You need to first select your project folder, and then the file you want to render from.

Cube : Open the Qube! app

Info : Get the user guide and information about the NCCA Render Farm

Bug : Report a bug

#### The Farm File Browser

You can expand folders to see items inside. right clicking on items will show you the action menu. Right clicking on the root folder will show custom actions for opening qube and refreshing the file browser.

You are also able to drag and drop files and folders into the farm.

Some shortcuts are listed below;

Delete : Delete the selected item(s)

F2 : Rename the selected item

R : Refresh the file browser

P : Upload and submit a project to the renderfarm

### Your "Farm"

Your farm is where you can upload projects and submit them for rendering. You can then download rendered frames back onto your local computer.

#### Preparing your Projects

When preparing a project, you want to make sure that everything is stored inside a root folder. 

All your file paths must be *relative* to your render file (and shouldn't go beyond your root folder).

Make sure that you have also entered the correct render settings for your project.

#### Submitting Projects and Jobs

You can either submit an entire project (by using the actions). Or, you can right click a dcc file and submit a job with it. Please make sure that all your paths are correct otherwise your renders may not be correct.

### Issues

The app can be buggy at times, so do be patient. If you feel that It's slowing down or something unusual is happening. Try restarting. If it keeps happening, report a bug either through the UI or at https://github.com/cjhosken/NCCARenderFarmTools/issues.


### Acessing the real farm

If everything has fallen apart, and you need to access your farm. You can do so in linux.

See Jon Macey's videos on accessing the farm on Linux.

#### Reporting Bugs

It's very important you report any bugs you face otherwise they likely will never get fixed. When you report a bug, try and assign a label to it. Do not create any new labels.

## Development

This project is open source, which means anyone can participate in development! I hope that this tool will be passed along by students, and maintained by them while they're at University.

If you wish to get involved with development, read [DEVEL.md](DEVEL.md)

## Contact

This software was initially developed by me, Christopher Hosken, in June 2024.

If you have any concerns or inquiries, contact me here:

[Website](https://cjhosken.github.io/)

[Email](mailto:hoskenchristopher@gmail.com)

[Linkedin](https://www.linkedin.com/in/christopher-hosken/)

[GitHub](https://github.com/cjhosken)