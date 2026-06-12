import sqlite3
import os
from datetime import datetime

class DatabaseHandlerDAL:
    def __init__(self, db_name="seq_master.db"):
        self.db_path = os.path.join(os.path.dirname(__file__), db_name)

    def connect(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.curr = self.conn.cursor()
        self.curr.execute('CREATE TABLE IF NOT EXISTS Logs (ID INTEGER PRIMARY KEY, SID TEXT, File TEXT, Length INTEGER, GC REAL, Date TIMESTAMP)')
        self.conn.commit()

    def start_session(self): 
        return datetime.now().timestamp()

    def insert_log(self, sid, file, length, gc):
        self.curr.execute('INSERT INTO Logs (SID, File, Length, GC, Date) VALUES (?, ?, ?, ?, ?)', 
                          (sid, file, length, gc, datetime.now()))
        self.conn.commit()

    def fetch_session_history(self, filter_text=""):
        self.curr.execute("SELECT File, Length, GC FROM Logs WHERE File LIKE ? ORDER BY Date DESC", 
                          (f'%{filter_text}%',))
        return self.curr.fetchall()

    def clear_logs(self):
        self.curr.execute("DELETE FROM Logs")
        self.conn.commit()