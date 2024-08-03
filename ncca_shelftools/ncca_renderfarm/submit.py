# RenderFarmSubmitDialog is the parent class that other submitters extend from.

from PySide2.QtWidgets import QMainWindow, QWidget, QMessageBox
import sys

from config import *
from utils import *

class RenderFarmSubmitDialog(QMainWindow):
    """"""
    def __init__(self, title=NCCA_SUBMIT_DIALOG_TITLE, info=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(600, 280)
        self.init_ui()
        self.finish_ui()

        self.sftp = info["sftp"]
        self.username = info["username"]

    def init_ui(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        # Main layout for form
        self.gridLayout = QtWidgets.QGridLayout(self.central_widget)
        self.home_dir=os.environ.get("HOME")
        self.user=os.environ.get("USER")

        # row 0 project name
        label=QtWidgets.QLabel(NCCA_SUBMIT_PROJECTNAME_LABEL)
        self.gridLayout.addWidget(label,0,0,1,1)
        self.project_name = QtWidgets.QLineEdit(self)
        self.project_name.setToolTip(NCCA_SUBMIT_PROJECTNAME_TOOLTIP)
        self.gridLayout.addWidget(self.project_name, 0, 1, 1, 3)

        label=QtWidgets.QLabel(NCCA_SUBMIT_CPUCOUNT_LABEL)
        self.gridLayout.addWidget(label, 0, 4, 1, 1)
        self.cpus=QtWidgets.QComboBox()
        self.cpus.addItems(str(i) for i in range(1, MAX_CPUS+1))
        self.cpus.setCurrentText(str(DEFAULT_CPU_USAGE))
        self.cpus.setToolTip(NCCA_SUBMIT_CPUCOUNT_TOOLTIP)
        self.gridLayout.addWidget(self.cpus, 0, 5, 1, 1)

        # row 1 select output drive
        self.select_project=QtWidgets.QPushButton(NCCA_SUBMIT_PROJECTFOLDER_LABEL)
        self.select_project.setToolTip(NCCA_SUBMIT_PROJECTFOLDER_TOOLTIP)
        self.select_project.clicked.connect(self.select_project_path)
        self.gridLayout.addWidget(self.select_project,1,0,1,1)
        self.project_path = QtWidgets.QLineEdit(self)
        self.project_path.setReadOnly(True)
        self.gridLayout.addWidget(self.project_path, 1, 1, 1, 5)

        # row 2
        label=QtWidgets.QLabel(NCCA_SUBMIT_STARTFRAME_LABEL)
        self.gridLayout.addWidget(label,2,0,1,1)
        self.start_frame=QtWidgets.QSpinBox()
        self.start_frame.setMinimum(-1000000)
        self.start_frame.setToolTip(NCCA_SUBMIT_STARTFRAME_TOOLTIP)

        self.start_frame.valueChanged.connect(self.update_frame_range)
        self.gridLayout.addWidget(self.start_frame,2,1,1,1)
        
        label=QtWidgets.QLabel(NCCA_SUBMIT_ENDFRAME_LABEL)
        self.gridLayout.addWidget(label,2,2,1,1)
        self.end_frame=QtWidgets.QSpinBox()
        self.end_frame.setMaximum(1000000)
        self.end_frame.valueChanged.connect(self.update_frame_range)
        self.end_frame.setToolTip(NCCA_SUBMIT_ENDFRAME_TOOLTIP)

        self.gridLayout.addWidget(self.end_frame,2,3,1,1)

        label=QtWidgets.QLabel(NCCA_SUBMIT_BYFRAME_LABEL)
        self.gridLayout.addWidget(label,2,4,1,1)
        self.by_frame=QtWidgets.QSpinBox()
        self.by_frame.setRange(1, self.end_frame.value() - self.start_frame.value())
        self.by_frame.setValue(1)
        self.by_frame.setToolTip(NCCA_SUBMIT_BYFRAME_TOOLTIP)

        self.gridLayout.addWidget(self.by_frame,2,5,1,1)
   
    def finish_ui(self):
        self.Cancel = QtWidgets.QPushButton(NCCA_SUBMIT_CLOSE_LABEL, self)
        self.Cancel.setToolTip(NCCA_SUBMIT_CLOSE_TOOLTIP)
        self.Cancel.clicked.connect(self.close)
        self.gridLayout.addWidget(self.Cancel, 6, 0, 1, 1)

        # Screen Shot button

        self.submit = QtWidgets.QPushButton(NCCA_SUBMIT_SUBMIT_LABEL, self)
        self.submit.pressed.connect(self.submit_project)
        self.submit.setEnabled(False)
        self.submit.setToolTip(NCCA_SUBMIT_SUBMIT_TOOLTIP)
        self.gridLayout.addWidget(self.submit, 6, 5, 1, 1)

    def submit_project(self, command=""):
        # Connect to the renderfarm

        local_project_dir = self.project_path.text()
        remote_project_dir = os.path.join("/home", self.username, "farm", "projects", os.path.basename(local_project_dir)).replace("\\", "/")
        
        if (sftp_exists(self.sftp, remote_project_dir)):
            if self.confirm_override(remote_project_dir):
                sftp_delete(self.sftp, remote_project_dir)
            else:
                return
        
        sftp_upload(remote_project_dir, local_project_dir)
        # Submit the job

        frame_range=f"{self.start_frame.value()}-{self.end_frame.value()}x{self.by_frame.value()}"
        render_home_dir = os.path.join("/render", self.username).replace("\\", "/")

        try:
            sys.path.append(QUBE_PYPATH.get(OPERATING_SYSTEM))
            import qb
        except Exception as e: 
            QtWidgets.QMessageBox.warning(None, NCCA_ERROR.get("title"), NCCA_ERROR.get("message").format(e))
            self.close()
            return

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
            
        job['agenda'] = qb.genframes(frame_range)

        listOfJobsToSubmit = [job]
        try:
            listOfSubmittedJobs = qb.submit(listOfJobsToSubmit)
            id_list = []
            for job in listOfSubmittedJobs:
                id_list.append(job['id'])
            QtWidgets.QMessageBox.warning(None, NCCA_SUBMIT_MESSAGE.get("title"), NCCA_SUBMIT_MESSAGE.get("message").format(self.project_name.text(), id_list))
        except Exception as e:
            QtWidgets.QMessageBox.warning(None, NCCA_ERROR.get("title"), NCCA_ERROR.get("message").format(e))
        
        self.close()

    def confirm_override(self, file_path):
        reply = QMessageBox.question(None, OVERRIDE_DIALOG.get("title"), 
            OVERRIDE_DIALOG.get("message").format(file_path), 
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return reply == QMessageBox.Yes

    def select_project_path(self):
        pass

    def update_frame_range(self):
        self.by_frame.setRange(1, self.end_frame.value() - self.start_frame.value())
        self.by_frame.setValue(min(max(1, self.by_frame.value()), self.end_frame.value() - self.start_frame.value()))

    def check_for_submit(self):
        self.submit.setEnabled(True)

