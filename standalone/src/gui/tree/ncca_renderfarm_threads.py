from config import *
from render_info import *
from gui.submit import *
from gui.dialogs import *

# See render_info/__init__.py as a primer
# 
# When waiting for the DCC file to read, the application process is held. 
# Moving the process into a thread allows for the user to still interact with the UI, even while loading is going.
#
# This is the part of the script that converts the print json data into real json data.
#
# If the script breaks, I recommend you print out the command in run(), and output in get_dcc_data(), that should help you debug any problems you face.

class NCCA_DCCDataThread(QThread):
    data_ready = pyqtSignal(object)

    def __init__(self, command, parent=None):
        super().__init__(parent)
        self.command = command

    def run(self):
        result = None
        if os.path.exists(self.command[0]):
            result = self.get_dcc_data(self.command)
        self.data_ready.emit(result)

    def get_dcc_data(self, command):
        if command:
            output = subprocess.check_output(self.command, stderr=subprocess.STDOUT, universal_newlines=True).strip()
            match = re.search(r'{\s*"NCCA_RENDERFARM":\s*{.*?}\s*}', output, re.DOTALL)

            if match:
                json_data = match.group()
                return json.loads(json_data)   
        return None