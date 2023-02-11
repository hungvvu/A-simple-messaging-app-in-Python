# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, QMetaObject, Qt
from PyQt5.QtWidgets import QInputDialog
from client import *

    

class Ui_Dialog(object):
    def __init__(self):
        # initialize the client
        my_username, ok = QInputDialog.getText(None, "Enter your username", "Username: ")
        if ok:
            self.client = Client(IP, PORT, my_username)
            self.client.message_received.connect(self.update_chatbox) # connect the message_received signal to the handling function

            # Start client in a separate thread
            self.client_thread = QThread()
            self.client.moveToThread(self.client_thread)
            self.client_thread.start()
            QMetaObject.invokeMethod(self.client, 'run', Qt.QueuedConnection)

        # create class member variables
        self.active_convo = '' # the currently active conversation
        

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(874, 628)
        Dialog.setMinimumSize(QtCore.QSize(874, 628))
        Dialog.setMaximumSize(QtCore.QSize(874, 628))
        self.plainTextEdit = QtWidgets.QPlainTextEdit(Dialog)
        self.plainTextEdit.setGeometry(QtCore.QRect(220, 580, 601, 51))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.textBrowser = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser.setGeometry(QtCore.QRect(220, 0, 661, 581))
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 221, 631))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")

        # create button for adding new conversation
        self.pushButton_2 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_2.setObjectName("--Add Conversation--")

        self.verticalLayout.addWidget(self.pushButton_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(820, 580, 61, 51))
        self.pushButton.setObjectName("pushButton")

        # connect signals to slots
        self.pushButton.clicked.connect(self.clicked_send)
        self.pushButton_2.clicked.connect(self.add_new_convo)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", f"{self.client.my_username} - Gnirob messaging"))
        self.textBrowser.setFontPointSize(15)
        
        self.pushButton_2.setText(_translate("Dialog", "--Add Conversation--"))
        self.pushButton.setText(_translate("Dialog", ">>"))



    ## slots ##

    def clicked_send(self):
        message = self.plainTextEdit.toPlainText() # saved the inputed message
        # if the message box is not empty
        if message and self.active_convo:
            self.plainTextEdit.setPlainText("") # clear the text box

            self.textBrowser.append(f"You > {message}")
            # target_username, ok = QInputDialog.getText(None, "Send message to", "Target's username: ")
            # if ok:
            self.client.send_txt_to(self.active_convo, message)


    def update_chatbox(self, message):
        self.textBrowser.append(message)

    def add_new_convo(self):
        newConvo = QtWidgets.QPushButton(self.verticalLayoutWidget)
        target_username, ok = QInputDialog.getText(None, "Add new conversation", "Target's username: ")

        if ok:
            # create new button for the added conversation
            self.pushButton_2.setObjectName(target_username)
            self.verticalLayout.insertWidget(self.verticalLayout.indexOf(self.pushButton_2), newConvo)
            newConvo.setText(target_username)

            newConvo.clicked.connect(lambda: self.chosen_conversation(target_username)) # connect the button with the signal for choosing conversations and pass in the target username


    def chosen_conversation(self, target_username):
        self.active_convo = target_username



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
