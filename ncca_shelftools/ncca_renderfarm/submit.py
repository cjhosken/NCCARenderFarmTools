from config import *

class RenderFarmSubmitDialog(QtWidgets.QDialog):
    """"""
    def __init__(self, title="NCCA Renderfarm Submit Tool", sftp=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(600, 280)
        self.init_ui()
        self.finish_ui()
        self.sftp = sftp

    def init_ui(self):
        # Main layout for form
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.home_dir=os.environ.get("HOME")
        self.user=os.environ.get("USER")

        # row 0 project name
        label=QtWidgets.QLabel("Project Name")
        self.gridLayout.addWidget(label,0,0,1,1)
        self.project_name = QtWidgets.QLineEdit(self)
        self.project_name.setToolTip("This is the name of the project as it will appear on the Qube GUI")
        self.gridLayout.addWidget(self.project_name, 0, 1, 1, 3)

        label=QtWidgets.QLabel("CPU Count")
        self.gridLayout.addWidget(label, 0, 4, 1, 1)
        self.cpus=QtWidgets.QComboBox()
        self.cpus.addItems(str(i) for i in range(1, 8+1))
        self.cpus.setCurrentIndex(1)
        self.cpus.setToolTip("number of nodes to use, please be respectful of others and only use high numbers if farm is empty")
        self.gridLayout.addWidget(self.cpus, 0, 5, 1, 1)

        # row 1 select output drive
        self.select_project=QtWidgets.QPushButton("Project Folder")
        self.select_project.setToolTip("Select the output ROP to render, these will be either in the /shop or /stage level")
        self.select_project.clicked.connect(self.select_project_path)
        self.gridLayout.addWidget(self.select_project,1,0,1,1)
        self.project_path = QtWidgets.QLineEdit(self)
        self.project_path.setReadOnly(True)
        self.gridLayout.addWidget(self.project_path, 1, 1, 1, 5)

        # row 2
        label=QtWidgets.QLabel("Start Frame")
        self.gridLayout.addWidget(label,2,0,1,1)
        self.start_frame=QtWidgets.QSpinBox()
        self.start_frame.setToolTip("Start frame for rendering, set from ROP but can be changed here, this will override the ROP value on the farm")

        self.start_frame.valueChanged.connect(self.update_frame_range)
        self.gridLayout.addWidget(self.start_frame,2,1,1,1)
        
        label=QtWidgets.QLabel("End Frame")
        self.gridLayout.addWidget(label,2,2,1,1)
        self.end_frame=QtWidgets.QSpinBox()
        self.end_frame.valueChanged.connect(self.update_frame_range)
        self.end_frame.setToolTip("End frame for rendering, set from ROP but can be changed here, this will override the ROP value on the farm")

        self.gridLayout.addWidget(self.end_frame,2,3,1,1)

        label=QtWidgets.QLabel("By Frame")
        self.gridLayout.addWidget(label,2,4,1,1)
        self.by_frame=QtWidgets.QSpinBox()
        self.by_frame.setRange(1, self.end_frame.value() - self.start_frame.value())
        self.by_frame.setValue(1)
        self.by_frame.setToolTip("Frame Step for rendering, set from ROP but can be changed here, this will override the ROP value on the farm")

        self.gridLayout.addWidget(self.by_frame,2,5,1,1)
   
    def finish_ui(self):
        self.Cancel = QtWidgets.QPushButton("Close", self)
        self.Cancel.setToolTip("Close the submit dialog")
        self.Cancel.clicked.connect(self.close)
        self.gridLayout.addWidget(self.Cancel, 6, 0, 1, 1)

        # Screen Shot button

        self.submit = QtWidgets.QPushButton("Submit", self)
        self.submit.pressed.connect(self.submit_project)
        self.submit.setEnabled(False)
        self.submit.setToolTip("Submit job to the farm, you must select a ROP before this will activate")
        self.gridLayout.addWidget(self.submit, 6, 5, 1, 1)

    def submit_project(self, command=""):
        # Connect to the renderfarm
        username = self.username

        local_project_dir = self.project_path.text()
        remote_project_dir = os.path.join("/home", username, "farm", "projects", os.path.basename(local_project_dir))
        
        #if (self.sftp.exists(remote_project_dir)):
        #    self.sftp.rmtree(remote_project_dir)

        #self.sftp.put(remote_project_dir, local_project_dir)
        # Upload the project folder
        # Submit the job

        frame_range=f"{self.start_frame.value()}-{self.end_frame.value()}x{self.by_frame.value()}"
        render_home_dir = os.path.join("/render", username).replace("\\", "/")

        #try:
        #    sys.path.append(QUBE_PYPATH)
        #    import qb
        #except Exception as e: 
        #    hou.ui.displayMessage(title="NCCA Tool Error", severity=hou.severityType.Error, details=f"{e}", text="Uh oh! An error occurred. Please contact the NCCA team if this issue persists.")
        #    self.done(0)

        job = {}
        job['name'] = self.project_name.text()
        job['cpus'] = self.cpus.currentText()
        job['prototype']="cmdrange"
        job['cwd'] = render_home_dir
        job['env'] = {"HOME" : render_home_dir}

        package = {}
        package['shell']="/bin/bash"

        package['cmdline'] = command

        job['pacakge'] = package
            
        #job['agenda'] = qb.genframes(frame_range)

        #listOfJobsToSubmit = [job]
        #try:
        #    listOfSubmittedJobs = qb.submit(listOfJobsToSubmit)
        #    id_list = []
        #    for job in listOfSubmittedJobs:
        #        id_list.append(job['id'])
        #    hou.ui.displayMessage(itle="NCCA Tool", text=f"{self.project_name.text()} has been successfully added to the NCCA Renderfarm! \nID: {id_list}",buttons=("Ok",))
        #except Exception as e:
        #    hou.ui.displayMessage(title="NCCA Tool Error", severity=hou.severityType.Error, details=f"{e}", text="Uh oh! An error occurred. Please contact the NCCA team if this issue persists.")
                 
        self.done(0)

    def select_project_path(self):
        pass

    def update_frame_range(self):
        self.by_frame.setRange(1, self.end_frame.value() - self.start_frame.value())
        self.by_frame.setValue(min(max(1, self.by_frame.value()), self.end_frame.value() - self.start_frame.value()))

    def check_for_submit(self):
        self.submit.setEnabled(True)

