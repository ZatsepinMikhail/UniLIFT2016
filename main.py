import Lift

import time, sys
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':

    app = QApplication([])
    lift = Lift.Lift()
    sys.exit(app.exec_())
