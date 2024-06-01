# NCCARenderFarmTools
My attempt at improving the NCCA renderfarm. Ideally, once the standalone tool is finished, the in-app tools can be deprecated.

For Linux, run `./standalone/NCCARenderFarm/launch.sh` to run the standalone application.

For Windows run `. "./standalone/NCCARenderFarm/launch.ps1"` to run the standalone application.

## TODOs
1. Cleanup and document the code for Jon Macey
2. Check for bugs with editing files
3. Fix Drag/Drop
4. Add job submissions
5. Fix the renderfarm server
6. Polish the code and check for bugs
7. First release
8. Implement into the machines
9. Public Announcements


## Known Limitations
At the current moment, Qt (and c++) is not behaving correctly on the RedHat machines in the NCCA lab. 
There seems to be a problem with cstdio and stdio in the gcc-toolset. 
I'll include the error messages below when I have time.


This is the error that appears when running launch.sh

```
qt.qpa.plugin: From 6.5.0, xcb-cursor0 or libxcb-cursor0 is needed to load the Qt xcb platform plugin.
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

Available platform plugins are: eglfs, linuxfb, minimal, minimalegl, offscreen, vkkhrdisplay, vnc, wayland-egl, wayland, xcb.
```

The quick fix for this should be `sudo yum install xcb-cursor0`




Another issue that occurs (which has been happened for most of the year), is 

/opt/rh/gcc-toolset-12/root/usr/include/c++/12/cstdlib:75:15: fatal error: stdlib.h: No such file or directory
   75 | #include_next <stdlib.h>