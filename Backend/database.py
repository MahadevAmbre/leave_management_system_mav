'''
import mysql.connector

db = mysql.connector.connect(
    host="YOUR_RDS_ENDPOINT",
    user="admin",
    password="yourpassword",
    database="leave_db"
)

cursor = db.cursor(dictionary=True)
'''
print("LOADING DATABASE FILE FROM:", __file__)

import sqlite3

def get_db_connection():
    conn = sqlite3.connect("leave_management.db")
    conn.row_factory = sqlite3.Row
    return conn
