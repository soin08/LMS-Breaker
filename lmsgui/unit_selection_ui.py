# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\unit_selection.ui'
#
# Created: Tue Jan 27 22:04:32 2015
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

class Ui_UnitSelection(object):
    def setupUi(self, UnitSelection):
        UnitSelection.setObjectName(_fromUtf8("UnitSelection"))
        UnitSelection.resize(492, 580)
        self.label_title = QtGui.QLabel(UnitSelection)
        self.label_title.setGeometry(QtCore.QRect(180, 10, 131, 20))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label_title.setFont(font)
        self.label_title.setObjectName(_fromUtf8("label_title"))
        self.label_desc = QtGui.QLabel(UnitSelection)
        self.label_desc.setGeometry(QtCore.QRect(190, 30, 121, 21))
        self.label_desc.setObjectName(_fromUtf8("label_desc"))
        self.label_choose = QtGui.QLabel(UnitSelection)
        self.label_choose.setGeometry(QtCore.QRect(130, 70, 241, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_choose.setFont(font)
        self.label_choose.setObjectName(_fromUtf8("label_choose"))
        self.button_solve = QtGui.QPushButton(UnitSelection)
        self.button_solve.setGeometry(QtCore.QRect(200, 530, 101, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.button_solve.setFont(font)
        self.button_solve.setObjectName(_fromUtf8("button_solve"))
        self.label_min_percent = QtGui.QLabel(UnitSelection)
        self.label_min_percent.setGeometry(QtCore.QRect(30, 350, 151, 16))
        self.label_min_percent.setObjectName(_fromUtf8("label_min_percent"))
        self.label_max_percent = QtGui.QLabel(UnitSelection)
        self.label_max_percent.setGeometry(QtCore.QRect(30, 400, 131, 16))
        self.label_max_percent.setObjectName(_fromUtf8("label_max_percent"))
        self.spinbox_min_percent = QtGui.QSpinBox(UnitSelection)
        self.spinbox_min_percent.setGeometry(QtCore.QRect(170, 350, 42, 22))
        self.spinbox_min_percent.setMinimum(0)
        self.spinbox_min_percent.setMaximum(100)
        self.spinbox_min_percent.setProperty("value", 90)
        self.spinbox_min_percent.setObjectName(_fromUtf8("spinbox_min_percent"))
        self.spinbox_max_percent = QtGui.QSpinBox(UnitSelection)
        self.spinbox_max_percent.setGeometry(QtCore.QRect(170, 400, 42, 22))
        self.spinbox_max_percent.setMinimum(0)
        self.spinbox_max_percent.setMaximum(100)
        self.spinbox_max_percent.setProperty("value", 100)
        self.spinbox_max_percent.setObjectName(_fromUtf8("spinbox_max_percent"))
        self.label_range_explained = QtGui.QLabel(UnitSelection)
        self.label_range_explained.setGeometry(QtCore.QRect(30, 450, 411, 20))
        self.label_range_explained.setObjectName(_fromUtf8("label_range_explained"))
        self.scroll_area = QtGui.QScrollArea(UnitSelection)
        self.scroll_area.setEnabled(True)
        self.scroll_area.setGeometry(QtCore.QRect(20, 100, 451, 231))
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName(_fromUtf8("scroll_area"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 449, 229))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.scroll_area.setWidget(self.scrollAreaWidgetContents)
        self.line = QtGui.QFrame(UnitSelection)
        self.line.setGeometry(QtCore.QRect(27, 480, 441, 20))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.label_status = QtGui.QLabel(UnitSelection)
        self.label_status.setGeometry(QtCore.QRect(30, 500, 47, 16))
        self.label_status.setObjectName(_fromUtf8("label_status"))
        self.label_status_msg = QtGui.QLabel(UnitSelection)
        self.label_status_msg.setGeometry(QtCore.QRect(70, 500, 361, 16))
        self.label_status_msg.setObjectName(_fromUtf8("label_status_msg"))

        self.retranslateUi(UnitSelection)
        QtCore.QMetaObject.connectSlotsByName(UnitSelection)

    def retranslateUi(self, UnitSelection):
        UnitSelection.setWindowTitle(_translate("UnitSelection", "LMS Breaker", None))
        self.label_title.setText(_translate("UnitSelection", "LMS Breaker", None))
        self.label_desc.setText(_translate("UnitSelection", "Do English in three clicks", None))
        self.label_choose.setText(_translate("UnitSelection", "Choose the tasks you would like to solve:", None))
        self.button_solve.setText(_translate("UnitSelection", "Solve!", None))
        self.label_min_percent.setText(_translate("UnitSelection", "Min percent of completion:", None))
        self.label_max_percent.setText(_translate("UnitSelection", "Max percent of completion:", None))
        self.label_range_explained.setText(_translate("UnitSelection", "A random number will be picked for each activity in each task within the given range.", None))
        self.label_status.setText(_translate("UnitSelection", "Status:", None))
        self.label_status_msg.setText(_translate("UnitSelection", "choose tasks...", None))

