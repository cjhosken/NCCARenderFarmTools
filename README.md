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







def submitSelectedIndex(self):
        """Opens a window for users to submit their project to the renderfarm"""
        index = self.currentIndex()
        if not index.isValid():
            return

        file_path = self.model().get_file_path(index)
        _, file_ext = os.path.splitext(os.path.basename(file_path))


        # Get the file name from the remote path
        file_name = os.path.basename(file_path)

        # Create a temporary directory
        temp_dir = tempfile.TemporaryDirectory(dir=os.path.join(get_user_home(), "tmp"))

        # Construct the local path for the downloaded file
        local_path = os.path.join(temp_dir.name, file_name).replace("\\", "/")

        # Download the file to the temporary directory
        self.model().renderfarm.download(file_path, local_path)

        data = None
        self.setCursor(QCursor(Qt.WaitCursor))
        if "blend" in file_ext:
            data = read_blend_rend_chunk(local_path)

            temp_dir.cleanup()

            self.job_dialog = NCCA_QSubmit_Blender(username=self.username, file_path=file_path, file_data=data)
            self.job_dialog.setGeometry(self.geometry())
            self.job_dialog.show()
        
        elif "hip" in file_ext:
            print(local_path)
            print(file_path)
            command = [LOCAL_HYTHON_PATH, os.path.join(SCRIPT_DIR, "libs", "houdini_render_info.py").replace("\\", "/"), local_path]
            print(command)
            
            # Execute the command
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True).strip()
                
            match = re.search(r'{\s*"NCCA_RENDERFARM":\s*{.*?}\s*}', output, re.DOTALL)
                
            if match:
                json_data = match.group()
                # Load JSON data
                data = json.loads(json_data)
                    
            self.job_dialog = NCCA_QSubmit_Houdini(username=self.username, file_path=file_path, file_data=data)
            self.job_dialog.setGeometry(self.geometry())
            self.job_dialog.show()

        
        elif file_ext in [".mb", ".ma"]:
            
            command = [LOCAL_MAYAPY_PATH, os.path.join(SCRIPT_DIR, "libs", "maya_render_info.py").replace("\\", "/"), local_path]
            # Execute the command
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True).strip()
            match = re.search(r'{\s*"NCCA_RENDERFARM":\s*{.*?}\s*}', output, re.DOTALL)

            if match:
                json_data = match.group()
                # Load JSON data
                data = json.loads(json_data)

            self.job_dialog = NCCA_QSubmit_Maya(username=self.username, file_path=file_path, file_data=data)
            self.job_dialog.setGeometry(self.geometry())
            self.job_dialog.show()
        else:
            self.job_dialog = NCCA_QSubmitWindow(username=self.username, file_path=file_path)
            self.job_dialog.setGeometry(self.geometry())
            self.job_dialog.show()
        
        self.setCursor(QCursor(Qt.ArrowCursor))