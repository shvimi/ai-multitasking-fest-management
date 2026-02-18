import sqlite3

conn = sqlite3.connect("fest.db")
cur = conn.cursor()

# ==============================
# 1️⃣ VOLUNTEER ASSIGNMENTS (SAFE)
# ==============================

cur.execute("""
CREATE TABLE IF NOT EXISTS volunteer_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    volunteer_id INTEGER,
    event_id INTEGER,
    duty_role TEXT,
    FOREIGN KEY (volunteer_id) REFERENCES users(id),
    FOREIGN KEY (event_id) REFERENCES events(id)
)
""")

print("✅ volunteer_assignments table ready")


# ==============================
# 2️⃣ USER INTERESTS (NEW AI FEATURE)
# ==============================

cur.execute("""
CREATE TABLE IF NOT EXISTS user_interests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    interest TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

print("✅ user_interests table ready")
# ==============================
# 3️⃣ REGISTRATIONS TABLE (MISSING FIX)
# ==============================

cur.execute("""
CREATE TABLE IF NOT EXISTS registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    event_id INTEGER,
    status TEXT DEFAULT 'confirmed',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (event_id) REFERENCES events(id)
)
""")

print("✅ registrations table ready")



conn.commit()
conn.close()

print("🎉 Database altered successfully (no data loss)")
