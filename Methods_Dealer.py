import sqlite3
import datetime
def check_rates_existant(user):
    conn = sqlite3.connect('styles/yields.db')
    c = conn.cursor()
    UserRatesDates = [i[0] for i in c.execute(f'SELECT date FROM users_rates WHERE user_name = "{user}" ').fetchall()]
    if str(datetime.date.today()) in UserRatesDates :
        pass
    else :
        c.execute(f'INSERT INTO users_rates VALUES ("{user}", 0, 0, "" ,"{datetime.date.today()}") ')
        conn.commit()

def check_TDtable_existant():
    try:
        conn = sqlite3.connect("styles/yields.db")
        c = conn.cursor()
        td_date = str(datetime.date.today())
        c.execute(f"""
CREATE TABLE "{td_date}" (
"User name"	TEXT,
"Device"	TEXT,
"Type"	TEXT,
"Start Time"	TEXT,
"End time"	TEXT,
"Time Spent"	TEXT,
"Paid for Hours"	REAL,
"Food"	TEXT,
"Paid for Food"	REAL,
"Total Paid"	REAL
);
        """)
        conn.commit()
    except sqlite3.OperationalError :
        pass

