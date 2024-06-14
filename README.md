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


NCCARenderFarm requires qube to run. On linux, you dont need to do anything. However on windows you need to install `Qube 7.5.2 Client Only` before running NCCARenderFarm.

<br>

### Building the Application

Run the setup script (either `windows_setup.bat`, `linux_setup.sh`). This will build the tools for you. It takes a couple minutes, so sit tight.

One the script is a complete, you'll see a `launch` executable appear. Running that should run the NCCRenderFarm.

<br>

Once complete, you wont need to run the setup file again. You can also move the NCCARenderFarmTools folder wherever you like.

On linux, storing it somewhere like `home/s5605094/ncca/NCCARenderFarmTools` is a good place.

On windows, storing it in your `H://` drive is recommended, as then you wont need to rebuilt it for each lab machine you sign into. 
*Dont setup the project in the H:// drive, as it takes MUCH longer.*


## Contact

This software was developed by me, Christopher Hosken.

[Email]()

[Linkedin]()

[GitHub](https://github.com/cjhosken)

[Artstation]()