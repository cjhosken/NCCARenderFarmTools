from config import *

from gui.ncca_qflatbutton import NCCA_QFlatButton
from gui.ncca_qmainwindow import NCCA_QMainWindow
from gui.ncca_qmessagebox import NCCA_QMessageBox
from gui.ncca_qcombobox import NCCA_QComboBox
from gui.ncca_qinput import NCCA_QInput

class NCCA_QSubmitWindow(NCCA_QMainWindow):
    """Interface for the user to submit renderfarm jobs"""

    def __init__(self, file_path="", name="Submit Job", username="", parent=None):
        """Initializes the window UI"""
        self.file_path = file_path
        self.job_id = 0
        self.name = name
        self.username = username
        super().__init__(self.name, size=SUBMIT_WINDOW_SIZE)

    def initUI(self):
        super().initUI()
        """Initializes the UI"""
        self.main_layout.setAlignment(Qt.AlignCenter)

        # Title
        self.title=QLabel(self.name)
        self.title.setContentsMargins(25, 0, 0, 0)
        self.title.setFont(TITLE_FONT)
        self.title.setStyleSheet(f"color: {APP_FOREGROUND_COLOR};")
        self.nav_and_title_layout.addWidget(self.title, alignment=Qt.AlignLeft)
        self.nav_and_title_layout.addStretch()

        self.job_row_layout = QHBoxLayout()
        self.job_row_widget = QWidget()

        self.job_name_label = QLabel("Job Name")
        self.job_row_layout.addWidget(self.job_name_label)
        self.job_name = NCCA_QInput(placeholder="Job Name", text=f"{self.username}_{os.path.basename(self.file_path)}")
        self.job_row_layout.addWidget(self.job_name)

        self.cpu_label = QLabel("CPUs")
        self.job_row_layout.addWidget(self.cpu_label)
        self.num_cpus = NCCA_QComboBox()
        self.num_cpus.addItems([str(i) for i in range(1, FARM_CPUS)])
        self.num_cpus.setCurrentText(str(DEFAULT_CPU_USAGE))
        self.job_row_layout.addWidget(self.num_cpus)

        self.job_row_widget.setLayout(self.job_row_layout)
        self.main_layout.addWidget(self.job_row_widget)
        
        self.frame_row_layout = QHBoxLayout()
        self.frame_row_widget = QWidget()

        self.frame_label = QLabel("Frame Range")
        self.frame_row_layout.addWidget(self.frame_label)

        self.frame_start = NCCA_QInput(placeholder="Frame Start", text="1")
        self.frame_start.setValidator(QIntValidator())
        self.frame_row_layout.addWidget(self.frame_start)

        self.frame_end = NCCA_QInput(placeholder="Frame End", text="125")
        self.frame_end.setValidator(QIntValidator())
        self.frame_row_layout.addWidget(self.frame_end)

        self.frame_step = NCCA_QInput(placeholder="Frame Step", text="1")
        self.frame_step.setValidator(QIntValidator())
        self.frame_row_layout.addWidget(self.frame_step)

        self.frame_row_widget.setLayout(self.frame_row_layout)

        self.main_layout.addWidget(self.frame_row_widget)

    def endUI(self):
        """Same purpose as endUI, however another level deeper"""
        self.button_box = QDialogButtonBox(Qt.Horizontal)
        

        # Submit button
        submit_button = NCCA_QFlatButton("Submit")
        submit_button.setFixedSize(QSize(125, 35))
        submit_button.clicked.connect(self.submit_job)
        self.button_box.addButton(submit_button, QDialogButtonBox.YesRole)

        # Cancel button
        cancel_button = NCCA_QFlatButton("Cancel")
        cancel_button.setFixedSize(QSize(125, 35))
        cancel_button.clicked.connect(self.close)
        self.button_box.addButton(cancel_button, QDialogButtonBox.NoRole)


        self.main_layout.addWidget(self.button_box, alignment=Qt.AlignCenter)

        super().endUI()

    def submit_job(self):
        """ Submits the job to the renderfarm"""
        self.close()
        NCCA_QMessageBox.info(
            self,
            "NCCA Renderfarm",
            f"Job Submitted!\nID: {self.job_id}"
        )