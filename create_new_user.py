from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
import sys
import datetime
import sqlite3
import os

conn = sqlite3.connect('styles/admin.db')
c = conn.cursor()


MainUI, _ = loadUiType('styles/CreateNewUser_page.ui')

class CreatingNewUser(QWidget, MainUI):
    def __init__(self, parent = None):
        super(CreatingNewUser, self).__init__(parent)
        QWidget.__init__(self)
        self.setupUi(self)
        self.clicked_buttons()
        

    def clicked_buttons(self):
        self.Submit_button.clicked.connect(self.add_new_user)
        self.Submit_button.setShortcut('Return')

    def show_pop(self, title, message):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def add_new_user(self):
        today_datetime = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S")
        LineEdits = [self.User_name_input.text(), self.Password_input.text(), self.Email_input.text(), self.Phone_number_input.text(),
        self.Admin_password_input.text(), self.National_ID_input.text()]
        if all([i !="" for i in LineEdits[0:3]]) and self.Admin_password_input.text() !="" and len(self.Phone_number_input.text()) != 11 :
            self.show_pop("Uncorrect Data", "Phone Number isn't 11 numebers  Please, Re-enter your Phone Numebr.")

        elif all([i !="" for i in LineEdits[0:4]]) and self.Admin_password_input.text() !="" and len(self.National_ID_input.text()) != 14 :
            self.show_pop("Uncorrect Data", "National ID isn't 14 numebers  Please, Re-enter your National ID.")

        elif any([i =="" for i in LineEdits]):
            self.show_pop("Uncorrect Data", "Make sure you entered all of the required data ! ")

        else :
            admin_code = c.execute("SELECT Password FROM Users").fetchone()
            if admin_code == None:
                try:
                    c.execute("""
                    INSERT INTO Users VALUES ('{}', '{}', '{}', '{}','{}', '{}')
                    """.format(self.User_name_input.text(), self.Password_input.text(), self.Email_input.text(), self.Phone_number_input.text(), self.National_ID_input.text(), today_datetime))
                    conn.commit()
                    self.show_pop("Congrats", "New user has been created successfuly.")
                    with open('{}/users_notes/{}.txt'.format(os.getcwd().replace("\\", '/') ,self.User_name_input.text()), 'w') as f:
                        f.write('')
                    self.User_name_input.setText("") 
                    self.Password_input.setText("") 
                    self.Email_input.setText("") 
                    self.Phone_number_input.setText("")
                    self.Admin_password_input.setText("")
                    self.National_ID_input.setText("")  
                except sqlite3.IntegrityError:
                    self.show_pop("Common data have been entered", "Your User_Name, Email, National ID or Phone_Number have been entered before by another user.")
            else :
                if self.Admin_password_input.text() == admin_code[0]:
                    try:
                        c.execute("""
                        INSERT INTO Users VALUES ('{}', '{}', '{}', '{}', '{}', '{}')
                        """.format(self.User_name_input.text(), self.Password_input.text(), self.Email_input.text(), self.Phone_number_input.text(), self.National_ID_input.text(), today_datetime))
                        conn.commit()
                        with open('{}/users_notes/{}.txt'.format(os.getcwd().replace("\\", '/') ,self.User_name_input.text()), 'w') as f:
                            f.write('')
                        self.show_pop("Congrats", "New user has been created successfuly.")
                        self.User_name_input.setText("") 
                        self.Password_input.setText("") 
                        self.Email_input.setText("") 
                        self.Phone_number_input.setText("")
                        self.Admin_password_input.setText("")
                        self.National_ID_input.setText("") 
                    except sqlite3.IntegrityError:
                        self.show_pop("Common data have been entered", "Your User_Name, Email, or Phone_Number have been entered before by another user.")
                else:
                    self.show_pop("Uncorrect Data", "Admin password isn't correct.")


def main():
    app = QApplication(sys.argv)
    window = CreatingNewUser()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()