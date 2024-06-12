from config import *
from render_info import *
from gui.submit import *
from gui.dialogs import *

class NCCA_DCCDataThread(QThread):
    data_ready = pyqtSignal(object)

    def __init__(self, command, parent=None):
        super().__init__(parent)
        self.command = command

    def run(self):
        result = None
        self.data_ready.emit(result)

    def get_dcc_data(self, command):
        if command:
            output = subprocess.check_output(self.command, stderr=subprocess.STDOUT, universal_newlines=True).strip()
            match = re.search(r'{\s*"NCCA_RENDERFARM":\s*{.*?}\s*}', output, re.DOTALL)

            if match:
                json_data = match.group()
                return json.loads(json_data)   
        return None