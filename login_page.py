from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
from admin_page import Admin_Page_UI
from create_new_user import CreatingNewUser
from user_page_v2 import User_Page
import sys
import sqlite3      
import datetime
from Methods_Dealer import check_rates_existant, check_TDtable_existant
from getmac import get_mac_address as Mac
import ctypes

ValidUsers = ['e0:2a:82:df:74:41']

MainUI , _ = loadUiType("styles/login_page.ui")

conn = sqlite3.connect("styles/admin.db")
c = conn.cursor()

conn2 = sqlite3.connect('styles/yields.db')
c2 = conn2.cursor()


class Login_Page(QDialog, MainUI):
    def __init__(self, parent = None):
        super(Login_Page, self).__init__(parent)
        QDialog.__init__(self)
        self.setupUi(self)
        self.widget_changes()
        self.buttons_clicked()

    def widget_changes(self):
        pass

    def buttons_clicked(self):
        self.pushButton_2.clicked.connect(self.open_regestration)
        self.pushButton.clicked.connect(self.check)        
        self.pushButton.setShortcut("Return")

    def check(self):
        admin_exe = c.execute("SELECT User_Name, Password FROM users").fetchone()
        users_exe  = c.execute("SELECT User_Name, Password FROM users").fetchall()
        users_name_exe =[i[0] for i in  c.execute("SELECT User_Name FROM users").fetchall()]
        if (self.lineEdit.text() , self.lineEdit_2.text()) in users_exe:
            if (self.lineEdit.text(), self.lineEdit_2.text()) == admin_exe:
                self.open_admin_page()

            else:
                check_TDtable_existant()
                check_rates_existant(self.lineEdit.text())
                self.open_user_page()

        else:
            if self.lineEdit.text() in users_name_exe:
                msg = QMessageBox.information(self, 'Informative Message', 'Uncorrect Password.', QMessageBox.Ok)
            else:
                msg = QMessageBox.information(self, 'Informative Message', 'Sorry, This user can\'t be found.', QMessageBox.Yes)        
  




    def open_regestration(self):
        self.ui = CreatingNewUser()
        self.ui.show()

        

    
    def open_admin_page(self):
        self.ui = Admin_Page_UI(self.lineEdit.text())
        self.ui.show()
        self.lineEdit.setText("")
        self.lineEdit_2.setText("")
    

    def open_user_page(self):
        self.ui = User_Page(self.lineEdit.text())
        self.ui.show()
        self.lineEdit.setText("")
        self.lineEdit_2.setText("")
        






def main():
    app = QApplication(sys.argv)
    login = Login_Page()
    login.show()
    app.exec_()

if __name__ == "__main__":
    # if Mac() in ValidUsers:
    main()
    # else :
    #     ctypes.windll.user32.MessageBoxW(0,
    #     """\n
    #     You can't use the applicatopn because you haven't bought it from the legal developer :(\n
    #     To buy the application please, contact "Ahmed Hawater" ON : \n
    #     1 - hawatercoding@gmail.com
    #     2 - +20 1207151977.
    #     """, "Unvalid User !", 16)
        

    # shutil.move(os.path.join(r"C:\Users\osama.pc\

    # thing = Popen(["locker.bat"], stdin = PIPE, stdout = PIPE, shell = True)
    # thing.communicate(input="y".encode())