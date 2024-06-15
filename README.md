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

//TODO

### Your "Farm"

//TODO

### Projects and Jobs

//TODO

#### Preparing your Projects

//TODO

#### Submitting Projects and Jobs

// TODO

### Issues

The app can be buggy at times, so do be patient. If you feel that It's slowing down or something unusual is happening. Try restarting. If it keeps happening, report a bug either through the UI or at https://github.com/cjhosken/NCCARenderFarmTools/issues.


### Acessing the real farm

If everything has fallen apart, and you need to access your farm. You can do so in linux.

//TODO

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