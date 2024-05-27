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
I'll include the error message below when I have time.
