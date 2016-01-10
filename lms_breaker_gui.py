import sys
import threading
from lmsbreaker import Breaker, LMS_BaseError
from PyQt4.QtCore import pyqtSlot, Qt
from PyQt4.QtGui import QApplication, QCursor
from PyQt4 import QtCore, QtGui

from lmsgui import Ui_LoginWindow
from lmsgui import Ui_UnitSelection

import os.path

breaker = Breaker()

if os.path.exists("./breaker.exe"):
    breaker.set_cacert_path("cacert.pem")

class Cursor:
    @staticmethod
    def change_cursor():
         QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

    @staticmethod
    def restore_cursor():
         QApplication.restoreOverrideCursor( )


class Window:
    def show_message(self, header, message):
         QtGui.QMessageBox.about(self,  header, message)

    def show_error(self, message):
        self.show_message("Ошибка", message)

    def show_default_error(self):
        self.show_error("Произошла неизвестная ошибка.")

    def change_status(self, status):
        self.ui.label_status_msg.setText(status)


class LoginWindow(QtGui.QWidget, Window):
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__(parent)

        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        self.ui.button_login.clicked.connect(self.on_login_button_clicked)
        self.ui.line_username.textChanged.connect(self.on_login_line_changed)
        self.ui.line_password.textChanged.connect(self.on_login_line_changed)

        self.ui.line_username.returnPressed.connect(self.on_login_button_clicked)
        self.ui.line_password.returnPressed.connect(self.on_login_button_clicked)

    def is_login_info_empty(self):
        username = self.ui.line_username.text()
        password = self.ui.line_password.text()
        return not (len( password.strip(" ")) > 0 and len( username.strip(" "))) > 0

    def login(self, username, password):
        self.login_thread = LoginThread(username, password)
        self.login_thread.loginSucceeded.connect(self.on_login_succeeded)
        self.login_thread.loginFailed.connect(self.on_login_failed)
        self.login_thread.start()

    def fetch_units(self):
        self.units_thread = UnitsThread()
        self.units_thread.unitsFetched.connect(self.on_units_fetched)
        self.units_thread.unitsFailed.connect(self.on_units_failed)
        self.units_thread.start()

    def disable_ui(self):
        self.ui.line_username.setEnabled(False)
        self.ui.line_password.setEnabled(False)
        self.ui.button_login.setEnabled(False)

    def enable_ui(self):
        self.ui.line_username.setEnabled(True)
        self.ui.line_password.setEnabled(True)
        self.ui.button_login.setEnabled(True)

    def set_waiting_ui(self):
        self.disable_ui()
        Cursor.change_cursor()

    def unset_waiting_ui(self):
        self.enable_ui()
        Cursor.restore_cursor()

    @pyqtSlot(list)
    def on_units_fetched(self, units):
        Cursor.restore_cursor()
        self.hide()
        self.unit_window = UnitWindow(units)
        self.unit_window.show()

    @pyqtSlot(Exception)
    def on_units_failed(self, e):
        self.unset_waiting_ui()
        if isinstance(e, LMS_BaseError):
            self.show_error(str(e))
        else:
            self.show_default_error()

    @pyqtSlot()
    def on_login_button_clicked(self):
        if not self.is_login_info_empty():
            self.set_waiting_ui()
            self.change_status("logging in...")
            username = self.ui.line_username.text()
            password = self.ui.line_password.text()
            self.login(username, password)
        else :
            self.show_error("Введите логин / пароль")

    @pyqtSlot(str)
    def on_login_line_changed(self, string):
        if not self.is_login_info_empty():
            self.change_status("ready to login.")
        else:
            self.change_status("enter username and password.")

    @pyqtSlot()
    def on_login_succeeded(self):
        self.change_status("fetching activities...")
        self.fetch_units()

    @pyqtSlot(Exception)
    def on_login_failed(self, e):
        self.unset_waiting_ui()
        self.change_status("enter username and password.")
        if isinstance(e, LMS_BaseError):
            self.show_error(str(e))
        else:
            self.show_default_error()
        breaker.logout()


class UnitWindow(QtGui.QWidget, Window):
    def __init__(self, units, parent=None):
        super(UnitWindow, self).__init__(parent)
        self.units = units
        self.ui = Ui_UnitSelection()
        self.ui.setupUi(self)

        self.ui.button_solve.clicked.connect(self.on_solve_button_clicked)

        w = QtGui.QWidget(self)
        self.ui.vbox = QtGui.QVBoxLayout(w)
        for index, value in enumerate(units):
            c = QtGui.QCheckBox(value['unit_title'])
            c.setObjectName("unit_" + str(index))
            self.ui.vbox.addWidget(c)
        self.ui.scroll_area.setWidget(w)

    def disable_ui(self):
        self.ui.scroll_area.setEnabled(False)
        self.ui.spinbox_max_percent.setEnabled(False)
        self.ui.spinbox_min_percent.setEnabled(False)
        self.ui.button_solve.setEnabled(False)

    def enable_ui(self):
        self.ui.scroll_area.setEnabled(True)
        self.ui.spinbox_max_percent.setEnabled(True)
        self.ui.spinbox_min_percent.setEnabled(True)
        self.ui.button_solve.setEnabled(True)

    def set_waiting_ui(self):
        self.disable_ui()
        Cursor.change_cursor()

    def unset_waiting_ui(self):
        self.enable_ui()
        Cursor.restore_cursor()

    def start_attempt(self, units_chosen, percent_min, percent_max):
        self.attempt_thread = AttemptThread(self.units, units_chosen, percent_min, percent_max)
        self.attempt_thread.attemptSucceeded.connect(self.on_attempt_succeeded)
        self.attempt_thread.attemptFailed.connect(self.on_attempt_failed)
        self.attempt_thread.start()

    @pyqtSlot()
    def on_attempt_succeeded(self):
        self.unset_waiting_ui()
        self.show_message("Успех", "Выбранные юниты были успешно решены! До новых встреч!")
        self.hide()
        QApplication.quit()

    @pyqtSlot(Exception)
    def on_attempt_failed(self, e):
        self.unset_waiting_ui()
        if isinstance(e, LMS_BaseError):
            self.show_error(str(e))
        else:
            self.show_default_error()

    def on_solve_button_clicked(self):
        sel_units = self.get_selected_units()
        if sel_units:
            self.set_waiting_ui()
            self.change_status("solving selected tasks...")
            percent_min = self.ui.spinbox_min_percent.value()
            percent_max = self.ui.spinbox_max_percent.value()
            self.start_attempt(sel_units, percent_min, percent_max)
        else:
            self.show_error("Выберите юниты")

    def get_selected_units(self):
        units_chosen = []
        for i in range(self.ui.vbox.count()):
            c = self.ui.vbox.itemAt(i).widget()
            if c.isChecked():
                units_chosen.append( self.units[i])
        return units_chosen

    def closeEvent(self, event):
        pass

class LoginThread(QtCore.QThread):
    loginSucceeded = QtCore.pyqtSignal()
    loginFailed = QtCore.pyqtSignal(Exception)

    def __init__(self, username, password):
        QtCore.QThread.__init__(self)
        self.username = username
        self.password = password

    def run(self):
        try:
            breaker.login(self.username, self.password)
            self.loginSucceeded.emit()
        except Exception as e:
            self.loginFailed.emit(e)


class UnitsThread(QtCore.QThread):
    unitsFetched = QtCore.pyqtSignal(list)
    unitsFailed = QtCore.pyqtSignal(Exception)

    def __init__(self):
        QtCore.QThread.__init__(self)

    def run(self):
        try:
            units = breaker.get_units()
            self.unitsFetched.emit(units)
        except Exception as e:
            self.unitsFailed.emit(e)


class AttemptThread(QtCore.QThread):
    attemptSucceeded = QtCore.pyqtSignal()
    attemptFailed = QtCore.pyqtSignal(Exception)

    def __init__(self, units_aval, units_chosen, percent_min, percent_max):
        QtCore.QThread.__init__(self)
        self.units_aval = units_aval
        self.units_chosen = units_chosen
        self.percent_min = percent_min
        self.percent_max = percent_max

    def run(self):
        try:
            breaker.attempt(self.units_aval, self.units_chosen, self.percent_min, self.percent_max)
            self.attemptSucceeded.emit()
        except Exception as e:
            self.attemptFailed.emit(e)


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        myapp = LoginWindow()
        myapp.show()
        sys.exit(app.exec_())
    except SystemExit:
        breaker.logout()
