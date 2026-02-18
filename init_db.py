import sqlite3
import os

# SAME DB PATH as app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "fest.db")

conn = sqlite3.connect(DB)
cur = conn.cursor()



# ---------- USERS ----------
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

# ---------- EVENTS ----------
cur.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    room TEXT,
    date TEXT,
    start_time TEXT,
    end_time TEXT
)
""")

# ---------- LOGIN LOGS ----------
cur.execute("""
CREATE TABLE IF NOT EXISTS login_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    login_time TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

# ---------- VOLUNTEER ASSIGNMENTS ----------
cur.execute("""
CREATE TABLE IF NOT EXISTS volunteer_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    volunteer_id INTEGER,
    event_id INTEGER,
    FOREIGN KEY (volunteer_id) REFERENCES users(id),
    FOREIGN KEY (event_id) REFERENCES events(id)
)
""")

conn.commit()
conn.close()

print("✅ Database initialized successfully (users, events, login_logs, volunteer_assignments)")
