# NCCARenderFarmTools
My attempt at improving the NCCA renderfarm. Ideally, once the standalone tool is finished, the in-app tools can be deprecated.

Run `./launch.sh` to run the NCCA Renderfarm Tool.

## Current TODOs
1. Fix QB_FRAME error
2. Fix tabbed active buttons
3. Fix menu UI
4. Fix dialog sizes
6. progress_bar loading for counting files
7. Fix the Renderfarm server
8. Code Refactoring and Cleanup
9. Documentation

## TODOs
1. VFX Reference Platform (update Qube)
2. Polish the code and check for bugs (reduce hanging)
3. First release
4. Implement into the machines
5. Public Announcements

## Bugs

- When deleting large folders, the application takes a while to count the number of files. If a user spam clicks during this process, the application crashes. This is true for any time the program is loading something (or running a process)

- Blender, Nuke, Katana projects don't render on the farm as the software isnt installed on there.

- Katana not fully implemented due to it not being supported on the NCCA machines.

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
``````
/opt/rh/gcc-toolset-12/root/usr/include/c++/12/cstdlib:75:15: fatal error: stdlib.h: No such file or directory
   75 | #include_next <stdlib.h>
``````

# Renderfarm Errors


This is for arnold
```
00:00:00   557MB WARNING |  unable to load dynamic library /opt/autodesk/arnold/maya2023/procedurals/xgenSpline_procedural.so: libAdskSeExpr.so: cannot open shared object file: No such file or directory
00:00:00   558MB WARNING |  unable to load dynamic library /opt/autodesk/arnold/maya2023/procedurals/xgen_procedural.so: libAdskSeExpr.so: cannot open shared object file: No such file or directory
```

Alongside this, arnold needs licenses.
```
Warning: 00:00:11   691MB         |         ARNOLD_LICENSE_ORDER   = (not set)
Warning: 00:00:11   691MB         |         ARNOLD_LICENSE_MANAGER = (not set)
Warning: 00:00:11   691MB         |  [rlm]  solidangle_LICENSE     = (not set)
Warning: 00:00:11   691MB         |  [rlm]  RLM_LICENSE            = (not set)
Warning: 00:00:11   691MB         |  [clm]  ADSKFLEX_LICENSE_FILE  = (not set)
Warning: 00:00:11   691MB         |  [clm]  LM_LICENSE_FILE        = (not set)
```

This is for VRay
```
RuntimeError: Unable to dynamically load : /opt/software/ChaosGroup/V-Ray/Maya2023-x64/maya_vray/plug-ins/vrayformaya.so
libQt5DBus.so.5: cannot open shared object file: No such file or directory
libQt5DBus.so.5: cannot open shared object file: No such file or directory (vrayformaya)
```



RenderMan works (sort of). It just needs a system update
```
[rfm]     INFO:  <module>: Loading RenderMan for Maya -----------------------------------
[rfm]     INFO:  setup_environment: 24.1 @ 2180697 - linuxRHEL7_x86-64_gcc63icc190_external_release built on Wed 28 Jul 2021 @ 21:04:31
Error: file: /tmp/ASTMPVlbWhf.mel line 7: RuntimeError: file /opt/software/pixar/RenderManForMaya-24.1/plug-ins/RenderMan_for_Maya.py line 669: RenderMan for Maya 24.1 is only compatible with Maya 2019 - 2022 ! You are using version 2023
Warning: file: /tmp/ASTMPVlbWhf.mel line 7: Failed to run file: /opt/software/pixar/RenderManForMaya-24.1/plug-ins/RenderMan_for_Maya.py
Error: file: /tmp/ASTMPVlbWhf.mel line 7:  (RenderMan_for_Maya)
Warning: file: /opt/autodesk/maya2023/scripts/others/supportRenderers.mel line 169: The 'showLineNumbers' flag is obsolete and will be removed in the next version of Maya. Use the Script Editor checkbox to turn on line number display instead.
Error: file: /opt/autodesk/maya2023/scripts/others/supportRenderers.mel line 169: Renderer "renderman" is not valid
Error: file: /tmp/ASTMPVlbWhf.mel line 34: Scene /render/s5605094/farm/maya/maya_test.ma failed to render.
```


While not required, It would be nice to have the tool be in line with the [VFX Reference Platform](https://vfxplatform.com/).

To do so, this would involve updating Qube so that its compatible with Python 3.11 (At the moment, we're stuck on 3.8)