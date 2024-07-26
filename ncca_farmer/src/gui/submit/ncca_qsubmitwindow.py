from config import *
from gui.widgets import *
from gui.dialogs import *
from gui.ncca_qmainwindow import NCCA_QMainWindow

# All DCC job submissions derive from the NCCA_QSubmitWindow
# If you plan on writing your own job submitters, make it a child of this class.
# also look at the guide in gui/submit/__init__.py to write your own submitwindow class



class NCCA_QSubmitWindow(NCCA_QMainWindow):
    """Interface for the user to submit renderfarm jobs"""

    def __init__(self, renderfarm=None, file_path="", folder_path=None, name=QSUBMIT_DEFAULT_NAME, username="", parent=None):
        """Initializes the window UI"""
        self.file_path = file_path
        
        self.folder_path = "/"
        if folder_path is not None:
            self.folder_path = folder_path

        self.name = name
        self.username = username
        self.renderfarm = renderfarm

        super().__init__(self.name, size=SUBMIT_WINDOW_SIZE)


        # if the user sets their job_path.text() to /, expand it to /home/username/farm.
        if (self.job_path.text() == "/"):
            self.job_path.setText(os.path.dirname(file_path).replace(join_path(RENDERFARM_ROOT, username, RENDERFARM_FARM_DIR), ""))

    def init_ui(self):
        """Initializes the UI"""
        super().init_ui()
        self.setupJobInputs()

    def setupJobInputs(self):
        """Set up job input fields."""
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        self.title = QLabel(self.name)
        self.title.setContentsMargins(MARGIN_DEFAULT, 0, 0, 0)
        self.title.setFont(TITLE_FONT)
        self.title.setStyleSheet(f"color: {APP_FOREGROUND_COLOR};")
        self.nav_and_title_layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignLeft)
        self.nav_and_title_layout.addStretch()

        self.setupJobNameInput()
        self.setupJobPathInput()
        self.setupFrameRangeInput()

    def setupJobNameInput(self):
        """Set up job name input."""
        self.job_row_layout = QHBoxLayout()
        self.job_row_widget = QWidget()

        self.job_name_label = QLabel(SUBMIT_JOB_NAME_LABEL)
        self.job_row_layout.addWidget(self.job_name_label)
        self.job_name = NCCA_QInput(placeholder=SUBMIT_JOB_NAME_PLACEHOLDER, text=f"{self.username}_{os.path.basename(self.file_path)}")
        self.job_name.setToolTip(SUBMIT_JOB_NAME_TOOLTIP)
        self.job_row_layout.addWidget(self.job_name)

        self.cpu_label = QLabel(SUBMIT_CPUS_LABEL)
        self.job_row_layout.addWidget(self.cpu_label)
        self.num_cpus = NCCA_QComboBox()
        self.num_cpus.setToolTip(SUBMIT_CPUS_TOOLTIP)
        self.num_cpus.addItems([str(i) for i in range(1, FARM_CPUS+1)])
        self.num_cpus.setCurrentText(str(DEFAULT_CPU_USAGE))
        self.job_row_layout.addWidget(self.num_cpus)

        self.job_row_widget.setLayout(self.job_row_layout)
        self.main_layout.addWidget(self.job_row_widget)

    def setupJobPathInput(self):
        """Set up job path input."""
        self.job_path_row_layout = QHBoxLayout()
        self.job_path_row_widget = QWidget()

        self.job_path_label = QLabel(SUBMIT_JOB_PATH_LABEL)
        self.job_path_row_layout.addWidget(self.job_path_label)
        self.job_path = NCCA_QInput(placeholder=SUBMIT_JOB_PATH_PLACEHOLDER)
        self.job_path.setToolTip(SUBMIT_JOB_PATH_TOOLTIP)
        self.job_path.setText("/" + os.path.basename(self.folder_path))
        self.job_path_row_layout.addWidget(self.job_path)

        self.job_path_row_widget.setLayout(self.job_path_row_layout)
        self.main_layout.addWidget(self.job_path_row_widget)

    def setupFrameRangeInput(self):
        """Set up frame range input."""
        self.frame_row_layout = QHBoxLayout()
        self.frame_row_widget = QWidget()

        self.frame_label = QLabel(SUBMIT_FRAME_RANGE_LABEL)
        self.frame_row_layout.addWidget(self.frame_label)

        self.frame_start = NCCA_QInput(placeholder=SUBMIT_FRAME_START_LABEL, text=str(SUBMIT_FRAME_START_DEFAULT))
        self.frame_start.setValidator(QIntValidator())
        self.frame_start.setToolTip(SUBMIT_FRAME_START_TOOLTIP)
        self.frame_row_layout.addWidget(self.frame_start)

        self.frame_end = NCCA_QInput(placeholder=SUBMIT_FRAME_END_LABEL, text=str(SUBMIT_FRAME_END_DEFAULT))
        self.frame_end.setValidator(QIntValidator())
        self.frame_end.setToolTip(SUBMIT_FRAME_END_TOOLTIP)
        self.frame_row_layout.addWidget(self.frame_end)

        self.frame_step = NCCA_QInput(placeholder=SUBMIT_FRAME_STEP_LABEL, text=str(SUBMIT_FRAME_STEP_DEFAULT))
        self.frame_step.setValidator(QIntValidator())
        self.frame_step.setToolTip(SUBMIT_FRAME_STEP_TOOLTIP)
        self.frame_row_layout.addWidget(self.frame_step)

        self.frame_row_widget.setLayout(self.frame_row_layout)
        self.main_layout.addWidget(self.frame_row_widget)

    def end_ui(self):
        """Finalize UI elements."""
        self.setupCommandInput()
        self.setupButtons()
        super().end_ui()

    def setupCommandInput(self):
        """Set up extra command input."""
        self.command_row_layout = QHBoxLayout()
        self.command_row_widget = QWidget()

        self.command_label = QLabel(SUBMIT_EXTRA_COMMANDS_LABEL)
        self.command_row_layout.addWidget(self.command_label)
        self.command = NCCA_QInput(placeholder=SUBMIT_EXTRA_COMMANDS_PLACEHOLDER)
        self.command.setToolTip(SUBMIT_EXTRA_COMMANDS_TOOLTIP)
        self.command_row_layout.addWidget(self.command)

        self.command_row_widget.setLayout(self.command_row_layout)
        self.main_layout.addWidget(self.command_row_widget)

    def setupButtons(self):
        """Set up submit and cancel buttons."""
        self.button_box = QDialogButtonBox(Qt.Orientation.Horizontal)

        # Submit button
        submit_button = NCCA_QFlatButton(SUBMIT_BUTTON_SUBMIT_TEXT)
        submit_button.setFixedSize(QDIALOG_BUTTON_DEFAULT_SIZE)
        submit_button.clicked.connect(self.prepare_job)
        self.button_box.addButton(submit_button, QDialogButtonBox.ButtonRole.AcceptRole)

        # Cancel button
        cancel_button = NCCA_QFlatButton(SUBMIT_BUTTON_CANCEL_TEXT)
        cancel_button.setFixedSize(QDIALOG_BUTTON_DEFAULT_SIZE)
        cancel_button.clicked.connect(self.close)
        self.button_box.addButton(cancel_button, QDialogButtonBox.ButtonRole.AcceptRole)

        self.main_layout.addWidget(self.button_box, alignment=Qt.AlignmentFlag.AlignCenter)

    def prepare_job(self):
        """Prepare job for submission."""

        # This code is very messy, if someone wants to try and clean it up, be my guest.
        # its main intent is to convert the RENDERFARM_ROOT paths into RENDERFARM_RENDER_ROOT paths. see config/farm.py for more info.

        self.render_path = self.file_path.replace(join_path(RENDERFARM_ROOT, self.username),
                                                    join_path(RENDERFARM_RENDER_ROOT, self.username))

        remote_job_path = join_path(RENDERFARM_ROOT, self.username, RENDERFARM_FARM_DIR, self.job_path.text())

        if self.renderfarm.exists(remote_job_path):
            response = NCCA_QMessageBox.override(
                self,
                PATH_EXISTING_TITLE,
                PATH_EXISTING_OVERRIDE_LABEL.format(remote_job_path)
            )

            if response == QDialogButtonBox.ButtonLayout.YesRole:
                self.renderfarm.delete(remote_job_path)
                self.renderfarm.upload_folder(self.folder_path, remote_job_path, None)
            elif response == QDialogButtonBox.ButtonLayout.NoRole: 
                remote_render_path = join_path(RENDERFARM_RENDER_ROOT, self.username, RENDERFARM_FARM_DIR,
                                                self.job_path.text())

                common_prefix = os.path.commonprefix([self.folder_path, self.file_path])
                render_file_path = self.file_path[len(common_prefix) + 1:]

                self.render_path = join_path(remote_render_path, render_file_path)
            
            else:
                # not entirely sure this quits the process properly, it may continue to submit a job. This may need fixing.
                self.render_path = None

    def build_job(self):
        """prepare a job for the renderfarm
        
        This is where the job is prepared for qube. 
        It's fairly simple, but if you wish tofurther develop this, look at the Qube documentation.
        """

        job = {}

        # name is name of the job on the renderfarm
        job['name'] = self.job_name.text()

        # cpus is the max-number of cpus that can render at the same time
        job['cpus'] = self.num_cpus.currentText()

        # package is the main linux shell script that is sent to qube
        package={}
        package['shell']="/bin/bash" # set the shell for qube
        job['package'] = package 
        job['prototype'] = "cmdrange" # the type of qube project
        job['cwd'] = join_path(RENDERFARM_RENDER_ROOT, self.username) # cwd (Current Working Directory) is the starting directory for the shell script. It's been set to /render/user
        job['env'] = {"HOME": join_path(RENDERFARM_RENDER_ROOT, self.username)} # HOME environment variable. It's not put in renderfarm/payload/souce.sh as it requires the username.

        return job

    def submit_job(self, job):
        """Submit the job to the renderfarm.
        This takes in a job, and adds a couple extra (more dcc specific) settings.
        """

        # This where renderfarm/payload/source.sh is sourced. As it's copied over through the payload during login, it can be found at /render/user/.ncca/source.sh
        shell_script_path=join_path(RENDERFARM_RENDER_ROOT, self.username, NCCA_PACKAGE_DIR, "source.sh")
        sed_command = f"sed -i 's/\r//' {shell_script_path};" # Due to developing the shell script on windows, sometimes characters are misread. This makes sure that the script can be run in shell.

        source_command = f"{sed_command} source {shell_script_path};" # This runs the character fix, then the environment sourcing.

        # job['package']['cmidline'] is the main command for rendering. It's set in the DCC submit classes and than passed through.
        # source_command is prepended to it so that the environment variables are setup before the script starts.
        job['package']['cmdline'] = f"{source_command} {job['package']['cmdline']}" 

        # The render frame range. Qube requires it to be in the string format "start-endxstep", (eg: "1-100x1") 
        frame_range = f"{int(self.frame_start.text())}-{int(self.frame_end.text())}x{int(self.frame_step.text())}"
        # all the frame jobs are then generated.
        job['agenda'] = qb.genframes(frame_range)


        # The job is then sent to the renderfarm.
        listOfJobsToSubmit = [job]
        try:
            listOfSubmittedJobs = qb.submit(listOfJobsToSubmit)
            id_list = []
            for job in listOfSubmittedJobs:
                id_list.append(job['id'])

            self.close()
            NCCA_QMessageBox.info(
                self,
                RENDERFARM_DIALOG_TITLE,
                RENDERFARM_SUBMITTED_LABEL.format(id_list)
            )
        except Exception as e:
            traceback_info = traceback.format_exc()
            self.close()
            NCCA_QMessageBox.warning(
                self,
                RENDERFARM_DIALOG_TITLE,
                RENDERFARM_ERROR_LABEL + "\n\n" + f"{str(e)}\n\nTraceback:\n{traceback_info}"
            )
            