# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, QMetaObject, Qt
from PyQt5.QtWidgets import QInputDialog, QMessageBox
from client import *

import constants
    
# a class for the chat text box where user enter their message in
class TextBox(QtWidgets.QPlainTextEdit):
    # signal for dectecting when the enter key is pressed
    enter_pressed = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.enter_pressed.emit()
        elif event.key() == QtCore.Qt.Key_Enter:
            self.enter_pressed.emit()
        else:
            super().keyPressEvent(event)


# a class for the input diaglog for creating group chat
class CreateGroupChatDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Adding new groupchat")
        
        # Create the input fields
        self.name_label = QtWidgets.QLabel("Group name: ")
        self.name_input = QtWidgets.QLineEdit()
        self.list_label = QtWidgets.QLabel("Member list (use ';' to separate usernames): ")
        self.list_input = QtWidgets.QLineEdit()
        
        # Create the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.list_label)
        layout.addWidget(self.list_input)
        self.setLayout(layout)
        
        # Add buttons
        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

class GroupConvoButton(QtWidgets.QPushButton):
    # signals for the group convo menu
    renameTriggered = QtCore.pyqtSignal()
    addMem_Triggered = QtCore.pyqtSignal()
    remvMem_Triggered = QtCore.pyqtSignal()
    view_memList_Triggered = QtCore.pyqtSignal()
    readStatus_Triggered = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        rename = menu.addAction("Rename")
        rename.triggered.connect(self.renameTriggered)

        add_member = menu.addAction("Add member")
        add_member.triggered.connect(self.addMem_Triggered)

        remv_member = menu.addAction("Remove member")
        remv_member.triggered.connect(self.remvMem_Triggered)

        view_member_list = menu.addAction("Member list")
        view_member_list.triggered.connect(self.view_memList_Triggered)

        read_status = menu.addAction("Check read status")
        read_status.triggered.connect(self.readStatus_Triggered)

        menu.exec_(self.mapToGlobal(event.pos()))

    
class DirectConvoButton(QtWidgets.QPushButton):
    # signals for the direct convo menu
    readStatus_Triggered = QtCore.pyqtSignal()
    sendFile_Triggered = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        read_status = menu.addAction("Check read status")
        read_status.triggered.connect(self.readStatus_Triggered)

        send_file = menu.addAction("Send file")
        send_file.triggered.connect(self.sendFile_Triggered)
    
        menu.exec_(self.mapToGlobal(event.pos()))


class Ui_Dialog(object):
    def __init__(self):
        # initialize the client
        my_username, ok = QInputDialog.getText(None, "Enter your username", "Username: ")
        if ok:
            self.client = Client(constants.IP, constants.PORT, my_username)
            self.client.text_message_received.connect(self.update_chatbox) # connect the text_ceived signal to the handling function
            self.client.rename_task_received.connect(self.update_convo_name) # handle the task required by the client
            self.client.file_message_received.connect(self.file_received)

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
        self.TextBox = TextBox(Dialog)
        self.TextBox.setGeometry(QtCore.QRect(220, 580, 601, 51))
        self.TextBox.setObjectName("TextBox")
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
        self.pushButton_2.setObjectName("--New Conversation--")

        self.verticalLayout.addWidget(self.pushButton_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(820, 580, 61, 51))
        self.pushButton.setObjectName("pushButton")

        # connect signals to slots
        self.pushButton.clicked.connect(self.clicked_send)
        self.pushButton_2.clicked.connect(self.show_new_convo_menu)
        self.TextBox.enter_pressed.connect(self.clicked_send)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", f"{self.client.my_username} - Gnirob messaging"))
        self.textBrowser.setFontPointSize(15)
        
        self.pushButton_2.setText(_translate("Dialog", "--New Conversation--"))
        self.pushButton.setText(_translate("Dialog", ">>"))

    def closeEvent(self, event):
        self.client.close()
        event.accept()

    ## slots ##

    def clicked_send(self):
        message = self.TextBox.toPlainText() # saved the inputed message
        # if the message box is not empty
        if message and self.active_convo:
            self.TextBox.setPlainText("") # clear the text box

            # make a timestamp from the current time
            timestamp = datetime.datetime.now().strftime("%H:%M")

            self.textBrowser.append(f"[{timestamp}, You --> {self.active_convo}] > {message}")
            # target_username, ok = QInputDialog.getText(None, "Send message to", "Target's username: ")
            # if ok:
            self.client.send_txt_to(self.active_convo, message)


    def update_chatbox(self, message):
        self.textBrowser.append(message)

    # update the specified convo name
    def update_convo_name(self, old_name, new_name):
        button = None
        # find the button for the conversation with the given name
        for widget in self.verticalLayoutWidget.findChildren(QtWidgets.QPushButton):
            if widget.text() == old_name:
                button = widget
                break
        
        if button is not None:
            # if the old_name was the active convo, update that to the new name
            if old_name == self.active_convo:
                self.active_convo = new_name

            button.setText(new_name)

    def file_received(self, file_size):
        # create a message box
        message_box = QMessageBox(self.verticalLayoutWidget)
        message_box.setWindowTitle("File Receive")
        message_box.setText("Would you like to receive the file?")

        # add buttons
        yes_button = message_box.addButton(QMessageBox.Yes)
        no_button = message_box.addButton(QMessageBox.No)

        # show the message box
        message_box.exec_()

        recv_status = False
        # check which button was clicked
        if message_box.clickedButton() == yes_button:
            # handle "yes"
            recv_status = self.client.recv_file(True, '/received/test_receive.txt', file_size)
        elif message_box.clickedButton() == no_button:
            # handle "no"
            recv_status = self.client.recv_file(False)

        if recv_status:
            # continue the client's execution
            self.client.halt = False
        else:
            self.update_chatbox('[ERROR] Fail to receive file')


    def show_new_convo_menu(self):
        menu = QtWidgets.QMenu(self.pushButton_2)
        
        action1 = menu.addAction("Direct message")
        action2 = menu.addAction("Group message")
        
        action1.triggered.connect(self.add_new_convo)
        action2.triggered.connect(self.add_new_group_convo)
        
        menu.exec_(QtGui.QCursor.pos())

    # for adding new direct messages conversations
    def add_new_convo(self):
        newConvo = DirectConvoButton(self.verticalLayoutWidget)
        target_username, ok = QInputDialog.getText(None, "Adding new conversation", "Target's username: ")

        if ok:
            # create new button for the added conversation
            # self.pushButton_2.setObjectName(target_username)
            self.verticalLayout.insertWidget(self.verticalLayout.indexOf(self.pushButton_2), newConvo)
            newConvo.setText(target_username)

            newConvo.clicked.connect(lambda: self.chosen_conversation(newConvo)) # connect the button with the signal for choosing conversations and pass in the target username
            newConvo.readStatus_Triggered.connect(lambda: self.check_readStatus(newConvo))
            newConvo.sendFile_Triggered.connect(lambda: self.send_file(newConvo)) #$here
            # rename the convo on the client side
            self.client.add_convo(target_username, {target_username})
    
    def add_new_group_convo(self):
        createGroupDialog = CreateGroupChatDialog()
        result = createGroupDialog.exec_()

        if result == QtWidgets.QDialog.Accepted:
            group_name = createGroupDialog.name_input.text()
            member_list_raw = createGroupDialog.list_input.text()

            try:
                member_set = set(member_list_raw.split(';')) # parse the usernames

                if group_name and len(member_set) != 0:
                    # create new button for the added conversation
                    newConvo = GroupConvoButton(self.verticalLayoutWidget)
                    self.verticalLayout.insertWidget(self.verticalLayout.indexOf(self.pushButton_2), newConvo)
                    newConvo.setText(group_name)

                    newConvo.clicked.connect(lambda: self.chosen_conversation(newConvo)) # connect the button with the signal for choosing conversations and pass in the target username
                    newConvo.renameTriggered.connect(lambda: self.rename_convo(newConvo))
                    newConvo.addMem_Triggered.connect(lambda: self.add_new_member(newConvo))
                    newConvo.remvMem_Triggered.connect(lambda: self.remv_member(newConvo))
                    newConvo.view_memList_Triggered.connect(lambda: self.view_member_list(newConvo))
                    newConvo.readStatus_Triggered.connect(lambda: self.check_readStatus(newConvo))

                    # save the new conversation on the client side
                    self.client.add_convo(group_name, member_set)
            
            except ValueError as e:
                QtWidgets.QMessageBox.warning(None, 'Error', str(e))

    def rename_convo(self, convo):
        # ask user for new name
        new_name, ok = QInputDialog.getText(None, "Renaming group", "New name: ")

        if ok:
            old_name = convo.text()
            convo.setText(new_name)

            # tell the client to rename the conversation
            self.client.rename_convo(old_name, new_name)

            # if the conversation was the active convo before the name change, make the new name the active convo
            if old_name == self.active_convo:
                self.active_convo = new_name

    def add_new_member(self, convo):
        # ask user for member name
        member_uname, ok = QInputDialog.getText(None, "Adding new member", "Member's username: ")

        if ok:
            # tell the client to add new member
            self.client.add_new_member(convo.text(), member_uname)

    def remv_member(self, convo):
        # ask user for member name
        member_uname, ok = QInputDialog.getText(None, "Removing member", "Member's username: ")

        if ok:
            # tell the client to add new member
            self.client.remv_member(convo.text(), member_uname)

    def view_member_list(self, convo):
        # tell the client about the view request
        self.client.view_member_list(convo.text())

    def check_readStatus(self, convo):
        # tell the client about the check read status request
        self.client.check_readStatus(convo.text())

    def send_file(self, convo):
        # ask user for file name
        file_dir, ok = QInputDialog.getText(None, "Sending file", "File directory: ")

        if ok:
            # tell the client to send the file
            self.client.send_file_to(convo.text(), file_dir)

    def chosen_conversation(self, button):
        self.clear_layout_color()
        button.setStyleSheet("background-color: DarkOliveGreen")
        self.active_convo = button.text()
    
    # for clearing all color of the widgets in the layout
    def clear_layout_color(self):
        for i in range(self.verticalLayout.count()):
            currWid = self.verticalLayout.itemAt(i).widget()
            if currWid:
                currWid.setStyleSheet("")



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
