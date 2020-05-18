from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
from datetime import date, datetime, timedelta, time
import collections
import sqlite3
from playsound import playsound
import concurrent.futures
import os
import smtplib
from email.message import EmailMessage
import csv
from Methods_Dealer import check_TDtable_existant, check_rates_existant


conn = sqlite3.connect("styles/admin.db")
cursor = conn.cursor()

conn2 = sqlite3.connect('styles/yields.db')
cursor2 = conn2.cursor()

MainUI, _ = loadUiType('styles/user_page.ui')

class User_Page(QTabWidget, MainUI):

    def __init__(self, global_user_name,  parent = None):
        self.global_user_name = global_user_name
        super(User_Page, self).__init__(parent)
        QTabWidget.__init__(self)
        self.setupUi(self)
        # print(self.global_user_name)
        self.widget_changes()
        self.clicked_buttons()
        self.groupboxes = [self.groupBox, self.groupBox_2, self.groupBox_3, self.groupBox_4]
        self.rename_groupBoxes()

    def demo(self):
        dem = QMessageBox()
        # dem.setEchoMode


    def Today_Inventory(self):
        try : 
            NotSeprated_Foods = []
            Level = []

            x = [i[0] for i in cursor2.execute(f'SELECT "Food" FROM "{date.today()}" WHERE "User Name" = "{self.global_user_name}" ').fetchall()]
            Level.extend([i.split(" / ") for i in x])
            for i in Level:
                NotSeprated_Foods.extend(i)


            Food_Inventory = []
            Food_Names = [i[0] for i in cursor.execute('SELECT Name FROM Foods ').fetchall()]

            for i in Food_Names:
                Level_0 =  list( filter(lambda x : x.split(":")[0] == i, NotSeprated_Foods) ) 

                OneItem_summ = [int(x.split(':')[1]) for x in Level_0]
                Food_Inventory.append(f'{i} : {sum(OneItem_summ)}')

            Food_Inventory = [i for i in Food_Inventory if i[-1] != "0"]

            cursor2.execute('UPDATE users_rates SET food = "{}" WHERE date = "{}" AND user_name = "{}" '.format(' / '.join(Food_Inventory), date.today(), self.global_user_name))
            conn2.commit()

            self.listWidget_19.addItems([i for i in Food_Inventory if i[-1] != "0"])
        except sqlite3.OperationalError:
            pass

# Sending Emails Methods   
    def EmailOperationStyling(self):
        self.lineEdit_19.clear()
        self.lineEdit_19.setEchoMode(QLineEdit.Password)
        self.lineEdit_19.setStyleSheet("border : 2px solid black")

    def sending(self):
        user_password = cursor.execute(f'SELECT Password FROM Users WHERE User_Name = "{self.global_user_name}" ').fetchone()[0]
        if self.lineEdit_19.text() == user_password:
            try:
                self.SENDING_mechanics()
                self.lineEdit_19.clear()
                msg  = QMessageBox.information(self.tab, "Informative Message", "Email has been sent Successfully", QMessageBox.Ok)
            except smtplib.socket.gaierror:
                os.remove('TodayYields.csv')
                self.lineEdit_19.clear()                
                msg2 = QMessageBox.warning(self.tab, "Connection Failed", "There is no internet connection", QMessageBox.Ok)
        else :
            self.lineEdit_19.setEchoMode(QLineEdit.Normal)
            self.lineEdit_19.setStyleSheet("color : red; border : 2px solid black") 
            self.lineEdit_19.setText("Uncorrect Password")
            QTimer.singleShot(500,self.EmailOperationStyling)


    def SENDING_mechanics(self):
        exe = cursor2.execute(f'SELECT * FROM "{date.today()}" ').fetchall()
        exe_columns_names = cursor2.execute(f'PRAGMA table_info("{date.today()}")').fetchall()
        columns_names = [name[1] for name in exe_columns_names]
        TotalYields = sum([i[-1] for i in exe ])
        AdminEmail = cursor.execute("SELECT Email FROM Users ").fetchone()[0]

        with open('TodayYields.csv', 'w', newline='') as csv_file:
            csv.writer(csv_file).writerow(columns_names)
            csv.writer(csv_file).writerow(["" for i in range(10)])
            csv.writer(csv_file).writerows(exe)

        My_Address = 'ahmedhawater3@gmail.com'
        Password = 'hema12345'

        msg = EmailMessage()
        msg['Subject'] = f'Your yields for {date.today()}'
        msg['From'] = My_Address
        msg['To'] = AdminEmail
        msg.add_alternative(f"""
            <!DOCTYPE html>
            <html>
                <body>
                    <h3>Sent at {datetime.now().time().strftime("%I:%M:%S %p")}</h3>
                    <h2>Total yields for today until now is {TotalYields} EG</h1>

                </body>
            </html>
        """, subtype = 'html')

        with open('TodayYields.csv', 'rb', ) as f:
            file_data = f.read() 
            file_name = f.name

        msg.add_attachment(file_data, maintype = 'application', subtype = 'octet-stram', filename = file_name )

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(user = My_Address, password= Password)
            smtp.send_message(msg)

        os.remove('TodayYields.csv')
  

# Notes Methods
    def notes_show(self):
        with open('{}/users_notes/{}.txt'.format(os.getcwd().replace("\\", '/'), self.global_user_name), 'r', encoding = "utf-8") as f:
            content = f.read()
        self.plainTextEdit.setPlainText(content)      

    
    def notes_save(self):
        content = self.plainTextEdit.toPlainText()
        with open('{}/users_notes/{}.txt'.format(os.getcwd().replace("\\", '/') ,self.global_user_name), 'w', encoding = "utf-8") as f2:
            f2.write(content)

# Others Methods
    def clock(self):
        self.label_21.setText(datetime.now().time().strftime('%I:%M:%S'))
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(lambda : self.label_21.setText(datetime.now().time().strftime('%I:%M:%S')) )
        self.clock_timer.start(1000)

    def show_targrt(self):
        try:
            Nclients = str(cursor2.execute(f'SELECT clients_numbers FROM users_rates WHERE user_name = "{self.global_user_name}" AND date = "{date.today()}" ').fetchone()[0])
            self.label_22.setText(Nclients.zfill(3))
        except TypeError:
            check_rates_existant(self.global_user_name)
            self.show_targrt()

    def blabla(self):
        try:
            TotalMoney = cursor2.execute(f'SELECT total FROM users_rates WHERE user_name = "{self.global_user_name}" AND date = "{date.today()}" ').fetchone()[0]
            self.label_23.setText(f"{TotalMoney}")
        except TypeError:
            pass
        
    def widget_changes(self):
        self.label_19.setText(f'Welcome {self.global_user_name}')
        self.blabla()
        self.show_targrt()
        self.clock()
        self.notes_show()
        self.Today_Inventory()
        
        self.Mcounter = 0
        self.is_open = False
        self.products_prices_list = []
        self.products_list = []
        self.single_radioBttn.setChecked(True)
        self.pause_bttn.setDisabled(True)
        self.timer = QTimer()
        self.show_foods(self.comboBox)

        self.Mcounter2 = 0
        self.is_open2 = False
        self.products_prices_list_2 = []
        self.products_list_2 = []
        self.single_radioBttn_2.setChecked(True)
        self.pause_bttn_2.setDisabled(True)
        self.timer_2 = QTimer()
        self.show_foods(self.comboBox_2)

        self.Mcounter3 = 0
        self.is_open3 = False
        self.products_prices_list_3 = []
        self.products_list_3 = []
        self.single_radioBttn_3.setChecked(True)
        self.pause_bttn_3.setDisabled(True)
        self.timer_3 = QTimer()
        self.show_foods(self.comboBox_3)

        self.Mcounter4 = 0
        self.is_open4 = False
        self.products_prices_list_4 = []
        self.products_list_4 = []
        self.single_radioBttn_4.setChecked(True)
        self.pause_bttn_4.setDisabled(True)
        self.timer_4 = QTimer()
        self.show_foods(self.comboBox_4)

    def device_counter(self, special):
        if special == 1 :
            self.Mcounter = self.Mcounter + 1
        elif special == 0 :
            self.Mcounter = 0
    def device_open(self, special):
        if special == 1 :
            self.is_open = True
        elif special == 0 :
            self.is_open = False
    # ------------------------------
    def device2_counter(self, special):
        if special == 1 :
            self.Mcounter2 = self.Mcounter2 + 1
        elif special == 0 :
            self.Mcounter2 = 0
    def device2_open(self, special):
        if special == 1 :
            self.is_open2 = True
        elif special == 0 :
            self.is_open2 = False
    # -------------------------------
    def device3_counter(self, special):
        if special == 1 :
            self.Mcounter3 = self.Mcounter3 + 1
        elif special == 0 :
            self.Mcounter3 = 0
    def device3_open(self, special):
        if special == 1 :
            self.is_open3 = True
        elif special == 0 :
            self.is_open3 = False
    # -------------------------------
    def device4_counter(self, special):
        if special == 1 :
            self.Mcounter4 = self.Mcounter4 + 1
        elif special == 0 :
            self.Mcounter4 = 0
    def device4_open(self, special):
        if special == 1 :
            self.is_open4 = True
        elif special == 0 :
            self.is_open4 = False




    def clicked_buttons(self):
        self.pushButton.clicked.connect(self.notes_save)
        self.pushButton_2.clicked.connect(self.sending)

        #   #

        """
                    Change the "Super Dober number" for each device EXCEPT (self.multi2.radioButton)   

           << Super Dober number : is the unique number for each [method, attr ,label, button, lineEdit, etc] >>

    explaination : using setters methods to change the value of the counter and the is_open attrs.

    more explaination : replacing  // Mcounter +=1 & Mcounter = 0 // with the setter method "device_counter"
                                   // is_open = False & is_open = True // with the setter method "device_open" 

    more more explaination : i did this cause i coould  not change the counter & is_open vlaue by passing it as an argument in the main methods
    of the program and cause i could not use {- + =} operators to modify the counter value , and i had to write 175 lines of code for every device.
    so i came out with the idea of using setters. its a little bit complicated but i will make it clear for you now :

        i had put functions parameters in the main program methods, and these functions are going to be called using lambda
        and these function "setters" are going to do all the work for me .

        I had made 2 setters functions for each device starting from the line " 166 ".
        
        """
        # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ 1 st $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        self.add_bttn.clicked.connect(lambda : self.add(self.spinBox, self.listWidget, self.comboBox, self.products_list))

        self.delete_bttn.clicked.connect(lambda : self.delete_list_item(self.listWidget, self.products_list))

        self.start_time_bttn.clicked.connect(lambda : self.timer_execution(self.timeEdit, self.timer,
            [self.start_time_bttn, self.start_open_time_bttn, self.pause_bttn], 
            lambda : self.timer_timeEdit_mechanics(self.timeEdit, self.timer, self.label,
                [self.start_time_bttn, self.start_open_time_bttn, self.pause_bttn], lambda : self.device_counter(1))))

        self.pause_bttn.clicked.connect(lambda : self.pause_time( self.timer, 
            [self.start_time_bttn, self.start_open_time_bttn, self.pause_bttn], self.is_open ))

                                # - - - - - - - - - -  - - - - - - - - - - - - - - -  #
        self.submit_bttn.clicked.connect(lambda : self.submit(self.Mcounter ,self.timer, self.timeEdit, self.groupBox,
            [self.single_radioBttn, self.multi1_radioBttn, self.multi2_radioBttn], self.lineEdit, self.listWidget, 
            self.products_list, self.products_prices_list, self.label, [self.start_time_bttn, self.start_open_time_bttn],
            lambda : self.device_counter(0), lambda : self.device_open(0),

            lambda : self.submit(self.Mcounter ,self.timer, self.timeEdit, self.groupBox,
            [self.single_radioBttn, self.multi1_radioBttn, self.multi2_radioBttn], self.lineEdit, self.listWidget, 
            self.products_list, self.products_prices_list, self.label, [self.start_time_bttn, self.start_open_time_bttn],
            lambda : self.device_counter(0), lambda : self.device_open(0) )))
                                # - - - - - - - - - -  - - - - - - - - - - - - - - -  #

        self.start_open_time_bttn.clicked.connect(lambda : self.open_time_execution(self.timer, self.timeEdit, 
            [self.start_time_bttn, self.start_open_time_bttn, self.pause_bttn], 
                lambda : self.open_time_mechanics(self.timeEdit, lambda : self.device_counter(1) ),
                lambda : self.device_open(1) ) )
        # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

        # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ 2 nd $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        self.add_bttn_2.clicked.connect(lambda : self.add(self.spinBox_2, self.listWidget_2, self.comboBox_2, self.products_list_2))

        self.delete_bttn_2.clicked.connect(lambda : self.delete_list_item(self.listWidget_2, self.products_list_2))

        self.start_time_bttn_2.clicked.connect(lambda : self.timer_execution(self.timeEdit_2, self.timer_2,
            [self.start_time_bttn_2, self.start_open_time_bttn_2, self.pause_bttn_2], 
            lambda : self.timer_timeEdit_mechanics(self.timeEdit_2, self.timer_2, self.label_2,
                [self.start_time_bttn_2, self.start_open_time_bttn_2, self.pause_bttn_2], lambda : self.device2_counter(1) )))

        self.pause_bttn_2.clicked.connect(lambda : self.pause_time( self.timer_2, 
            [self.start_time_bttn_2, self.start_open_time_bttn_2, self.pause_bttn_2], self.is_open2))

                                # - - - - - - - - - -  - - - - - - - - - - - - - - -  #
        self.submit_bttn_2.clicked.connect(lambda : self.submit(self.Mcounter2 ,self.timer_2, self.timeEdit_2, self.groupBox_2,
            [self.single_radioBttn_2, self.multi1_radioBttn_2, self.multi2_radioBttn_2], self.lineEdit_2, self.listWidget_2, 
            self.products_list_2, self.products_prices_list_2, self.label_2, [self.start_time_bttn_2, self.start_open_time_bttn_2],
            lambda : self.device2_counter(0), lambda : self.device2_open(0),

            lambda : self.submit(self.Mcounter2 ,self.timer_2, self.timeEdit_2, self.groupBox_2,
            [self.single_radioBttn_2, self.multi1_radioBttn_2, self.multi2_radioBttn_2], self.lineEdit_2, self.listWidget_2, 
            self.products_list_2, self.products_prices_list_2, self.label_2, [self.start_time_bttn_2, self.start_open_time_bttn_2],
            lambda : self.device2_counter(0), lambda : self.device2_open(0) )))
                                # - - - - - - - - - -  - - - - - - - - - - - - - - -  #

        self.start_open_time_bttn_2.clicked.connect(lambda : self.open_time_execution(self.timer_2, self.timeEdit_2, 
            [self.start_time_bttn_2, self.start_open_time_bttn_2, self.pause_bttn_2], 
                lambda : self.open_time_mechanics(self.timeEdit_2, lambda : self.device2_counter(1) ),
                lambda : self.device2_open(1) ) ) 
        # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

        # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ 3 rd $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        self.add_bttn_3.clicked.connect(lambda : self.add(self.spinBox_3, self.listWidget_3, self.comboBox_3, self.products_list_3))

        self.delete_bttn_3.clicked.connect(lambda : self.delete_list_item(self.listWidget_3, self.products_list_3))

        self.start_time_bttn_3.clicked.connect(lambda : self.timer_execution(self.timeEdit_3, self.timer_3,
            [self.start_time_bttn_3, self.start_open_time_bttn_3, self.pause_bttn_3], 
            lambda : self.timer_timeEdit_mechanics(self.timeEdit_3, self.timer_3, self.label_3,
                [self.start_time_bttn_3, self.start_open_time_bttn_3, self.pause_bttn_3], lambda : self.device3_counter(1) )))

        self.pause_bttn_3.clicked.connect(lambda : self.pause_time( self.timer_3, 
            [self.start_time_bttn_3, self.start_open_time_bttn_3, self.pause_bttn_3], self.is_open3 ))

                                # - - - - - - - - - -  - - - - - - - - - - - - - - -  #
        self.submit_bttn_3.clicked.connect(lambda : self.submit(self.Mcounter3 ,self.timer_3, self.timeEdit_3, self.groupBox_3,
            [self.single_radioBttn_3, self.multi1_radioBttn_3, self.multi2_radioBttn_3], self.lineEdit_3, self.listWidget_3, 
            self.products_list_3, self.products_prices_list_3, self.label_3, [self.start_time_bttn_3, self.start_open_time_bttn_3],
            lambda : self.device3_counter(0), lambda : self.device3_open(0),

            lambda : self.submit(self.Mcounter3 ,self.timer_3, self.timeEdit_3, self.groupBox_3,
            [self.single_radioBttn_3, self.multi1_radioBttn_3, self.multi2_radioBttn_3], self.lineEdit_3, self.listWidget_3, 
            self.products_list_3, self.products_prices_list_3, self.label_3, [self.start_time_bttn_3, self.start_open_time_bttn_3],
            lambda : self.device3_counter(0), lambda : self.device3_open(0)  ))) 
                                # - - - - - - - - - -  - - - - - - - - - - - - - - -  #

        self.start_open_time_bttn_3.clicked.connect(lambda : self.open_time_execution(self.timer_3, self.timeEdit_3, 
            [self.start_time_bttn_3, self.start_open_time_bttn_3, self.pause_bttn_3], 
                lambda : self.open_time_mechanics(self.timeEdit_3, lambda : self.device3_counter(1) ),
                lambda : self.device3_open(1) ) ) 
        # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

        # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ 4 nd $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        self.add_bttn_4.clicked.connect(lambda : self.add(self.spinBox_4, self.listWidget_4, self.comboBox_4, self.products_list_4))

        self.delete_bttn_4.clicked.connect(lambda : self.delete_list_item(self.listWidget_4, self.products_list_4))

        self.start_time_bttn_4.clicked.connect(lambda : self.timer_execution(self.timeEdit_4, self.timer_4,
            [self.start_time_bttn_4, self.start_open_time_bttn_4, self.pause_bttn_4], 
            lambda : self.timer_timeEdit_mechanics(self.timeEdit_4, self.timer_4, self.label_4,
                [self.start_time_bttn_4, self.start_open_time_bttn_4, self.pause_bttn_4], lambda : self.device4_counter(1) )))

        self.pause_bttn_4.clicked.connect(lambda : self.pause_time( self.timer_4, 
            [self.start_time_bttn_4, self.start_open_time_bttn_4, self.pause_bttn_4], self.is_open4))

                                # - - - - - - - - - -  - - - - - - - - - - - - - - -  #
        self.submit_bttn_4.clicked.connect(lambda : self.submit(self.Mcounter4 ,self.timer_4, self.timeEdit_4, self.groupBox_4,
            [self.single_radioBttn_4, self.multi1_radioBttn_4, self.multi2_radioBttn_4], self.lineEdit_4, self.listWidget_4,  
            self.products_list_4, self.products_prices_list_4, self.label_4, [self.start_time_bttn_4, self.start_open_time_bttn_4],
            lambda : self.device4_counter(0), lambda : self.device4_open(0),

            lambda : self.submit(self.Mcounter4 ,self.timer_4, self.timeEdit_4, self.groupBox_4,
            [self.single_radioBttn_4, self.multi1_radioBttn_4, self.multi2_radioBttn_4], self.lineEdit_4, self.listWidget_4, 
            self.products_list_4, self.products_prices_list_4, self.label_4, [self.start_time_bttn_4, self.start_open_time_bttn_4],
            lambda : self.device4_counter(0), lambda : self.device4_open(0) )))
                                # - - - - - - - - - -  - - - - - - - - - - - - - - -  #

        self.start_open_time_bttn_4.clicked.connect(lambda : self.open_time_execution(self.timer_4, self.timeEdit_4, 
            [self.start_time_bttn_4, self.start_open_time_bttn_4, self.pause_bttn_4], 
                lambda : self.open_time_mechanics(self.timeEdit_4, lambda : self.device4_counter(1) ),
                lambda : self.device4_open(1) ) ) 
        # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


    def rename_groupBoxes(self):
        ID_index = 1
        for i in self.groupboxes:
            name  = cursor.execute(f'SELECT Name FROM "Consoles and Screens" WHERE ID = {ID_index}').fetchone()[0]
            i.setTitle(name)
            ID_index +=1


    # buttons = [Start, Start open, Pause]
    def timer_execution(self, time_edit, timer, buttons, function):
        if time_edit.time().toPyTime() != time(0,0):
            timer.timeout.connect(function)
            timer.start(1000)
            buttons[0].setDisabled(True)
            buttons[1].setDisabled(True)
            buttons[2].setEnabled(True)
            time_edit.setReadOnly(True)


    def show_foods(self, combobox):
        products_list = [i[0] for i  in cursor.execute('SELECT Name FROM Foods').fetchall()]
        combobox.addItems(products_list)


    def add(self, spinbox, listwidget, combobox, products_list):
        for i in range(spinbox.value()):
            listwidget.addItem(combobox.currentText())
            products_list.append(combobox.currentText())


    def delete_list_item(self, listwidget ,products_list):
        try :
            if listwidget.count() != 0:
                row_index  = listwidget.currentRow()
                products_list.remove(listwidget.item(row_index).text())
                listwidget.takeItem(row_index)
            else :
                pass
        except AttributeError :
            pass


    # buttons = [Start, Start open, Pause]
    def timer_timeEdit_mechanics(self, time_edit, timer, label,  buttons, fun):
        if time_edit.time().toPyTime() != time(0,0):
            currentTime = time_edit.time().toPyTime()
            current = datetime.combine(date.today(), currentTime)
            deltaT = timedelta(minutes= 1)
            current -= deltaT
            time_edit.setTime(current.time())
            fun()
        else :
            with concurrent.futures.ThreadPoolExecutor() as ex:
                ex.submit(lambda : playsound('styles/annoy.mp3', block= False) )
            buttons[0].setEnabled(True)
            timer.stop()
            timer.disconnect()
            buttons[2].setDisabled(True)
            buttons[1].setDisabled(True)
            buttons[0].setDisabled(True)
            time_edit.setDisabled(True)
            label.setText("Time out")
            label.setStyleSheet("background-color: black; color: white;")
         

    def open_time_mechanics(self, time_edit, fun):
        currentTime = time_edit.time().toPyTime()
        current = datetime.combine(date.today(), currentTime)
        deltaT = timedelta(minutes= 1)
        current += deltaT
        time_edit.setTime(current.time())
        fun()


    # buttons = [Start, Start open, Pause]    
    def open_time_execution(self, timer, time_edit, buttons, function, fun):
        fun()
        timer.timeout.connect(function)
        timer.start(1000)
        buttons[2].setEnabled(True)
        buttons[0].setDisabled(True)
        buttons[1].setDisabled(True)
        time_edit.setReadOnly(True)


    # buttons = [Start, Start open, Pause]
    def pause_time(self, timer, buttons, TimeOpen):
        try :
            if TimeOpen:
                timer.stop()
                timer.disconnect()
                buttons[1].setEnabled(True)
                buttons[2].setDisabled(True)
            else:
                timer.stop()
                timer.disconnect()
                buttons[0].setEnabled(True)
                buttons[2].setDisabled(True)
        except TypeError:
            pass


     # radios = [Singlr radio, Multi1 radio, Multi2 radio]
     # buttons  = [Start, Start open]   
    def submit(self, counter, timer, time_edit ,groupbox, radios, password_input, food_list, products_list, products_prices_list, price_label, buttons, fun, fun2, fun3 = None):
        if (not timer.isActive()):
            try : 
                user_name = self.global_user_name
                user_password = cursor.execute(f'SELECT Password FROM Users WHERE User_Name = "{user_name}" ').fetchone()[0]
                singleHour = float(cursor.execute(f'SELECT "Price/Hour" FROM "Consoles and Screens" WHERE Name = "{groupbox.title()}" ').fetchone()[0])
                controllerHour = float(cursor.execute(f'SELECT "Controller price/hour" FROM "Consoles and Screens" WHERE Name = "{groupbox.title()}" ').fetchone()[0])
                if radios[0].isChecked():
                    HoursType = "Signle"
                    PricePerHour = singleHour
                elif radios[1].isChecked():
                    HoursType = "Multi 1"
                    PricePerHour = singleHour + controllerHour
                elif radios[2].isChecked():
                    HoursType = "Multi 2"
                    PricePerHour = singleHour + (2*controllerHour)
                
                if password_input.text() == user_password:
    # Setting "itmes:count" to be put in the list with the correct form
                    products_list = collections.Counter(products_list)
                    products_list = [f"{i}:{products_list[i]}" for i in products_list.keys()]

    # Setting variables that will sent to the table
                    device = groupbox.title()
                    start_time =( datetime.now() - timedelta(minutes= counter) ).time().strftime("%I:%M %p")
                    end_time = datetime.now().time().strftime("%I:%M %p")
                    total_foods_prices = 0
                    total_hours_prices = counter * (PricePerHour/60)
                    food_list_items = " / ".join(products_list)
                    
    # Getting the price for each item in the ListWidget & and all the prices to the "total_foods_prices"
    # Setting the "total_prices" variable
                    for i in range(food_list.count()):
                        products_prices_list.append(cursor.execute(f'''
                        SELECT "Price" FROM Foods WHERE "Name" = "{food_list.item(i).text()}" 
                        ''').fetchone()[0])
                    for i in products_prices_list:
                        total_foods_prices += i

                    total_prices = (total_foods_prices + total_hours_prices)

    # Sending the data to the table
                  
                # Insert data into yields
                    cursor2.execute(f'''
                    INSERT INTO "{date.today()}" VALUES ("{user_name}", "{device}", "{HoursType}", "{start_time}", "{end_time}", "{f'{counter} ' + 'Minutes' }", {round(total_hours_prices)}, "{food_list_items}", {total_foods_prices}, {round(total_prices)});
                    ''')

                # Update clients numbers for this user
                    current_numbers_of_clients = cursor2.execute(f'SELECT clients_numbers FROM users_rates WHERE user_name = "{user_name}" AND date = "{date.today()}" ').fetchone()[0] 
                    cursor2.execute(f'UPDATE users_rates SET clients_numbers = {current_numbers_of_clients+1} WHERE user_name = "{user_name}" AND date = "{date.today()}"  ')
                    
                    TotalMoney =  cursor2.execute(f'SELECT total FROM users_rates WHERE user_name = "{self.global_user_name}" AND date = "{date.today()}" ').fetchone()[0]
                    cursor2.execute(f'UPDATE users_rates SET total = {TotalMoney + round(total_prices)} WHERE user_name = "{self.global_user_name}" AND date = "{date.today()}" ')
                    conn2.commit()

                    self.blabla()
                    self.show_targrt()
                    self.listWidget_19.clear()
                    self.Today_Inventory()

                    price_label.setText(f"Required Paid is only {round(total_prices)} EG")
                    price_label.setStyleSheet("background-color: green; color: white;")
                    QTimer.singleShot(30000,lambda : price_label.setStyleSheet("background-color: none; color:#f0f0f0;") )

                
# Cleaning the form to start another operation

                    fun()
                    fun2()

                    products_prices_list.clear()
                    products_list.clear()
                    password_input.setText("")
                    food_list.clear()
                    time_edit.setEnabled(True)
                    time_edit.setTime(time(0,0))
                    time_edit.setReadOnly(False)
                    buttons[1].setEnabled(True)
                    buttons[0].setEnabled(True)
                    radios[0].setChecked(True)
                    

                else :
                    # msg = QMessageBox.warning(self, 'Ucorrect Data', 'Uncorrect Password! Maybe caps lock is turned on ??', QMessageBox.Ok)
                    price_label.setText('Uncorrect password')
                    price_label.setStyleSheet("background-color: red; color: white;")
                    QTimer.singleShot(3000,lambda : price_label.setStyleSheet("background-color: none; color:#f0f0f0;") )
                    password_input.setText("")
                    pass

            except ValueError or TypeError:
                price_label.setText('Unrecoginzed Prices for this device')
                price_label.setStyleSheet("background-color: black; color: white;")
                QTimer.singleShot(3000,lambda : price_label.setStyleSheet("background-color: none; color:#f0f0f0;") )

            except sqlite3.OperationalError :
                check_rates_existant(self.global_user_name)
                check_TDtable_existant()
                fun3()
                
        else:
            price_label.setText('Timer is running')
            price_label.setStyleSheet("background-color: blue; color: white;")
            QTimer.singleShot(3000,lambda : price_label.setStyleSheet("background-color: none; color:#f0f0f0;") )
            pass 


# def main():
#     import sys
#     app = QApplication(sys.argv)
#     window = User_Page("Hema")
#     window.show()
#     app.exec_()

# if __name__ == "__main__":
#     main()