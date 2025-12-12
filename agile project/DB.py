import mysql.connector
from tkinter import messagebox


class DBConnector:
    def __init__(self):
        self.connection_config = {
            "host": "localhost",
            "user": "root",
            "password": "Mohabahmed@2004",  # CHANGE FOR PRODUCTION
            "database": "JoesRide",
            "autocommit": True
        }
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.conn = mysql.connector.connect(**self.connection_config)
            self.cursor = self.conn.cursor(dictionary=True)
            return True
        except mysql.connector.Error as e:
            print(f"DB Connection Error: {e}")
            return False

    def execute_query(self, query, params=None):
        # Reconnect if connection lost
        if not self.conn or not self.conn.is_connected():
            if not self.connect():
                return False

        try:
            self.cursor.execute(query, params or ())
            if query.strip().upper().startswith("SELECT"):
                return self.cursor.fetchall()
            return True
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return False

    def __del__(self):
        if hasattr(self, 'conn') and self.conn and self.conn.is_connected():
            self.conn.close()
