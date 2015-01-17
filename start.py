import sys
from PyQt4 import QtCore, QtGui

from login_window_ui import Ui_LoginWindow


class LoginWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = LoginWindow()
    myapp.show()
    sys.exit(app.exec_())

