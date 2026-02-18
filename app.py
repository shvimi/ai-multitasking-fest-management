from flask import Flask, render_template, request, redirect, session
from datetime import date, datetime   # ← yahan datetime add karo
import sqlite3, os
app = Flask(__name__)
app.secret_key = "secretai"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "fest.db")

def get_db():
    return sqlite3.connect(DB)
 # 🤖 STEP 3: AI ROOM ASSIGN FUNCTION (YAHI LIKHNA HAI)
def ai_assign_room(date, start, end):
    db = get_db()

    rooms = ["Auditorium", "Room A", "Room B", "Room C"]

    for room in rooms:
        clash = db.execute("""
            SELECT id FROM events
            WHERE room=? AND date=?
            AND NOT (end_time<=? OR start_time>=?)
        """, (room, date, start, end)).fetchone()

        if not clash:
            db.close()
            return room

    db.close()
    return None
# 🤖 AI HELPERS

def ai_predict_budget(event_type, people=100):
    base = {
        "Dance": 6000,
        "Music": 9000,
        "Sports": 7000,
        "Knowledge": 4000
    }
    return base.get(event_type, 5000) + (people * 40)


def ai_predict_crowd(event_type):
    return {
        "Music": 300,
        "Dance": 250,
        "Sports": 200,
        "Knowledge": 120
    }.get(event_type, 150)


def ai_risk_status(crowd, capacity=250):
    return "🚨 Overcrowding Risk" if crowd > capacity else "✅ Safe"


def ai_attendance_prediction(reg):
    return int(reg * 0.8)


def ai_marketing_caption(name):
    return f"🔥 {name} is coming! Don’t miss the excitement 🎉"

def ai_recommend_events(user_id):
    db = get_db()

    interests = db.execute(
        "SELECT interest FROM user_interests WHERE user_id=?",
        (user_id,)
    ).fetchall()

    if not interests:
        db.close()
        return []

    interests = [i[0] for i in interests]

    query = f"""
        SELECT * FROM events
        WHERE type IN ({','.join('?'*len(interests))})
    """

    events = db.execute(query, interests).fetchall()
    db.close()
    return events

  
# ---------- HOME ----------
@app.route("/")
def index():
    return render_template("index.html")
#---------------AI CHATBOT--------
@app.route("/chatbot", methods=["POST"])
def chatbot():
    msg = request.form["message"].lower()

    if "time" in msg:
        return "⏰ Event timing Events page pe milega"
    if "venue" in msg:
        return "📍 Venue Admin panel me diya hai"
    if "help" in msg:
        return "🤖 I help with events, timing & registration"

    return "🤖 Samajh nahi aaya, please try again"


# ---------- LOGIN ----------
from datetime import datetime

@app.route("/login", methods=["GET","POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        pwd = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, pwd)
        ).fetchone()
        db.close()

        if user:
            session["user_id"] = user[0]
            session["name"] = user[1]
            session["role"] = user[4]

            # 🔴 STEP-4: LOGIN ENTRY SAVE (YAHI LIKHNA THA)
            db = get_db()
            db.execute(
                "INSERT INTO login_logs (user_id, login_time) VALUES (?, ?)",
                (user[0], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            db.commit()
            db.close()

            return redirect("/events")
        else:
            error = "Invalid Email or Password"

    return render_template("login.html", error=error) 
# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------- REGISTER ----------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        pwd = request.form["password"]
        role = request.form["role"]

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
                (name,email,pwd,role)
            )
            db.commit()
        except:
            return "Email already exists"
        finally:
            db.close()

        return redirect("/login")

    return render_template("register.html")

# ---------- EVENTS ----------
@app.route("/events")
def events():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    ev = db.execute("SELECT * FROM events").fetchall()
    db.close()

    recommended = ai_recommend_events(session["user_id"])

    return render_template(
        "events.html",
        events=ev,
        recommended=recommended
    )



# ---------- JOIN EVENT ----------
@app.route("/join_event", methods=["POST"])
def join_event():
    if "user_id" not in session:
        return redirect("/login")

    uid = session["user_id"]
    eid = request.form["event_id"]

    db = get_db()
    db.execute(
        "INSERT INTO registrations(user_id,event_id) VALUES(?,?)",
        (uid, eid)
    )
    db.commit()
    db.close()
    return redirect("/events")

# ---------- ADD EVENT ----------
@app.route("/add_event", methods=["GET", "POST"])
def add_event():

    # 🔐 Admin check
    if "user_id" not in session or session.get("role") != "Admin":
        return redirect("/login")

    if request.method == "POST":
        name = request.form["name"]
        type_ = request.form["type"]
        date_ = request.form["date"]
        start = request.form["start"]
        end = request.form["end"]

        # 🤖 AI Room Assign
        room = ai_assign_room(date_, start, end)
        if not room:
            return "❌ No room available"

        # 🤖 AI Predictions
        crowd = ai_predict_crowd(type_)
        budget = ai_predict_budget(type_, crowd)
        caption = ai_marketing_caption(name)

        # 💾 Save to DB
        db = get_db()
        db.execute("""
            INSERT INTO events (name, type, room, date, start_time, end_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, type_, room, date_, start, end))
        db.commit()
        db.close()

        # 🧠 AI Logs (console)
        print("AI Crowd:", crowd)
        print("AI Budget:", budget)
        print("AI Caption:", caption)

        return redirect("/admin")

    return render_template("add_events.html")



# ---------- ADMIN ----------
@app.route("/admin")
def admin():
    if "user_id" not in session or session.get("role") != "Admin":
        return redirect("/login")

    today = date.today().isoformat()
    db = get_db()

    events = db.execute("SELECT * FROM events").fetchall()

    ai_data = []
    for e in events:
        crowd = ai_predict_crowd(e[2])
        risk = ai_risk_status(crowd)
        ai_data.append({
            "event": e,
            "crowd": crowd,
            "risk": risk
        })

    db.close()
    return render_template("admin.html", ai_data=ai_data)

    # 🔥 DELETE OLD EVENTS
    old_events = db.execute(
        "SELECT id FROM events WHERE date < ?", (today,)
    ).fetchall()

    for e in old_events:
        db.execute("DELETE FROM registrations WHERE event_id=?", (e[0],))
        db.execute("DELETE FROM events WHERE id=?", (e[0],))

    db.commit()

    events = db.execute("SELECT * FROM events").fetchall()
    db.close()

    return render_template("admin.html", events=events)

    #-------delete------
@app.route("/delete_event", methods=["POST"])
def delete_event():
    if "user_id" not in session or session.get("role") != "Admin":
        return redirect("/login")

    eid = request.form.get("event_id")

    db = get_db()
    db.execute("DELETE FROM registrations WHERE event_id=?", (eid,))
    db.execute("DELETE FROM events WHERE id=?", (eid,))
    db.commit()
    db.close()

    return redirect("/admin")
if __name__ == "__main__":
    app.run(debug=True)
