# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\login_window.ui'
#
# Created: Sun Jan 25 13:15:59 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_LoginWindow(object):
    def setupUi(self, LoginWindow):
        LoginWindow.setObjectName(_fromUtf8("LoginWindow"))
        LoginWindow.setEnabled(True)
        LoginWindow.resize(241, 250)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(LoginWindow.sizePolicy().hasHeightForWidth())
        LoginWindow.setSizePolicy(sizePolicy)
        LoginWindow.setMaximumSize(QtCore.QSize(241, 250))
        LoginWindow.setBaseSize(QtCore.QSize(241, 250))
        self.label_title = QtGui.QLabel(LoginWindow)
        self.label_title.setGeometry(QtCore.QRect(50, 10, 131, 20))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label_title.setFont(font)
        self.label_title.setObjectName(_fromUtf8("label_title"))
        self.label_desc = QtGui.QLabel(LoginWindow)
        self.label_desc.setGeometry(QtCore.QRect(60, 30, 161, 21))
        self.label_desc.setObjectName(_fromUtf8("label_desc"))
        self.login_box = QtGui.QGroupBox(LoginWindow)
        self.login_box.setGeometry(QtCore.QRect(10, 60, 221, 151))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.login_box.setFont(font)
        self.login_box.setObjectName(_fromUtf8("login_box"))
        self.line_username = QtGui.QLineEdit(self.login_box)
        self.line_username.setGeometry(QtCore.QRect(90, 40, 113, 20))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.line_username.setFont(font)
        self.line_username.setInputMethodHints(QtCore.Qt.ImhHiddenText)
        self.line_username.setText(_fromUtf8(""))
        self.line_username.setObjectName(_fromUtf8("line_username"))
        self.line_password = QtGui.QLineEdit(self.login_box)
        self.line_password.setGeometry(QtCore.QRect(90, 70, 113, 20))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.line_password.setFont(font)
        #self.line_password.setInputMethodHints(QtCore.Qt.ImhHiddenText|QtCore.Qt.ImhNoAutoUppercase|QtCore.Qt.ImhNoPredictiveText|QtCore.Qt.ImhSensitiveData)
        self.line_password.setInputMask(_fromUtf8(""))
        self.line_password.setText(_fromUtf8(""))
        self.line_password.setEchoMode(QtGui.QLineEdit.Password)
        #self.line_password.setClearButtonEnabled(False)
        self.line_password.setObjectName(_fromUtf8("line_password"))
        self.label_login = QtGui.QLabel(self.login_box)
        self.label_login.setGeometry(QtCore.QRect(20, 40, 61, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_login.setFont(font)
        self.label_login.setObjectName(_fromUtf8("label_login"))
        self.label_password = QtGui.QLabel(self.login_box)
        self.label_password.setGeometry(QtCore.QRect(20, 70, 71, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_password.setFont(font)
        self.label_password.setObjectName(_fromUtf8("label_password"))
        self.button_login = QtGui.QPushButton(self.login_box)
        self.button_login.setGeometry(QtCore.QRect(20, 110, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.button_login.setFont(font)
        self.button_login.setObjectName(_fromUtf8("button_login"))
        self.label_status = QtGui.QLabel(LoginWindow)
        self.label_status.setGeometry(QtCore.QRect(10, 220, 41, 16))
        self.label_status.setObjectName(_fromUtf8("label_status"))
        self.label_status_msg = QtGui.QLabel(LoginWindow)
        self.label_status_msg.setGeometry(QtCore.QRect(50, 220, 151, 16))
        self.label_status_msg.setObjectName(_fromUtf8("label_status_msg"))

        self.retranslateUi(LoginWindow)
        QtCore.QMetaObject.connectSlotsByName(LoginWindow)

    def retranslateUi(self, LoginWindow):
        LoginWindow.setWindowTitle(_translate("LoginWindow", "LMS Breaker", None))
        self.label_title.setText(_translate("LoginWindow", "LMS Breaker", None))
        self.label_desc.setText(_translate("LoginWindow", "Do English in three clicks", None))
        self.login_box.setTitle(_translate("LoginWindow", "Login to Cambridge LMS", None))
        self.label_login.setText(_translate("LoginWindow", "username:", None))
        self.label_password.setText(_translate("LoginWindow", "password:", None))
        self.button_login.setText(_translate("LoginWindow", "Login", None))
        self.label_status.setText(_translate("LoginWindow", "Status:", None))
        self.label_status_msg.setText(_translate("LoginWindow", "enter username and password.", None))

