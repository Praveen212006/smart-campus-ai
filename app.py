from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv
from google import genai
load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
def ask_ai(question):
    generation_config = {
        "temperature": 1,
        "max_output_tokens": 65536,
        "top_p": 0.95,
        "thinking_level": "high",
    }

    interaction = client.interactions.create(
        model="models/gemini-3-flash-preview",
        input=question,
        generation_config=generation_config,
    )

    return interaction.output_text

from predict import predict_admission

app = Flask(__name__)
app.secret_key = "smart_ai_portal"


from flask import jsonify
@app.route("/get_districts/<state>")
def get_districts(state):

    df = pd.read_csv("colleges.csv")

    districts = sorted(
        df[df["state"] == state]["district"]
        .dropna()
        .unique()
        .tolist()
    )

    return jsonify(districts)

# ---------------- URL FIX ----------------

def fix_url(url):
    if pd.isna(url):
        return ""

    url = str(url).strip()

    if url == "":
        return ""

    if url.startswith(("http://", "https://")):
        return url

    return "https://" + url


# ---------------- CREATE DATABASE ----------------

def create_database():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # Users Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    # Admin Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    #add colleges table
    cur.execute("""
CREATE TABLE IF NOT EXISTS colleges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    college_name TEXT NOT NULL,
    location TEXT NOT NULL,
    course TEXT NOT NULL,
    cutoff TEXT NOT NULL,
    admission_chance TEXT NOT NULL
)
""")

    # Default Admin
    cur.execute("SELECT * FROM admins WHERE username=?", ("admin",))
    admin = cur.fetchone()

    if not admin:
        password = generate_password_hash("admin123")
        cur.execute(
            "INSERT INTO admins(username, password) VALUES(?, ?)",
            ("admin", password)
        )

    conn.commit()
    conn.close()
create_database()

# ---------------- HOME ----------------

@app.route("/")
def home():

    df = pd.read_csv("colleges.csv")

    states = sorted(df["state"].dropna().unique())

    return render_template(
        "index.html",
        states=states
    )


@app.route("/ask", methods=["POST"])
def ask():

    question = request.form["question"]

    answer = ask_ai(question)

    df = pd.read_csv("colleges.csv")

    states = sorted(df["state"].dropna().unique())

    return render_template(
        "index.html",
        answer=answer,
        states=states
    )


# ---------------- REGISTER ----------------


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect("database.db")
            cur = conn.cursor()

            cur.execute(
                """
                INSERT INTO users(name,email,password)
                VALUES(?,?,?)
                """,
                (name, email, hashed_password)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:
            return "Email already registered"

    return render_template("register.html")

# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session["user"] = user[1]
            return redirect("/dashboard")
        else:
            return "Invalid Email or Password"

    return render_template("login.html")

#-----------------admin login----------------#

@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM admins WHERE username=?",
            (username,)
        )

        admin = cur.fetchone()
        conn.close()

        if admin and check_password_hash(admin[2], password):
            session["admin"] = admin[1]
            return redirect("/admin_dashboard")
        else:
            return "Invalid Admin Username or Password"

    return render_template("admin_login.html")

#---------------- ADMIN DASHBOARD ----------------#
@app.route("/admin_dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM admins")
    total_admins = cur.fetchone()[0]

    conn.close()

    return render_template(
        "admin_dashboard.html",
        admin=session["admin"],
        total_users=total_users,
        total_admins=total_admins
    )
# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        username=session["user"]
    )


# ---------------- ADMISSION PREDICTION ----------------
@app.route("/predict", methods=["GET", "POST"])
def predict():

    result = None
    chance = None
    colleges = []

    try:
        df = pd.read_csv("colleges.csv")

        if "website" in df.columns:
            df["website"] = df["website"].apply(fix_url)

        if "cutoff" in df.columns:
            df["cutoff"] = pd.to_numeric(
                df["cutoff"],
                errors="coerce"
            ).fillna(0)

    except Exception as e:
        return f"Error loading colleges.csv: {e}"

    if request.method == "POST":

        try:

            cgpa = float(request.form["cgpa"])
            mark12 = float(request.form["mark12"])
            cutoff = float(request.form["cutoff"])
            entrance = float(request.form["entrance"])

            state = request.form.get("state", "").strip().lower()
            district = request.form.get("district", "").strip().lower()

            student_data = {
                "CGPA": cgpa,
                "12th_Mark": mark12,
                "Cutoff": cutoff,
                "Entrance_Score": entrance
            }

            result, chance = predict_admission(student_data)

            # Cutoff filter
            eligible = df[df["cutoff"] <= cutoff].copy()

            # Clean values
            eligible["state"] = (
                eligible["state"]
                .astype(str)
                .str.strip()
                .str.lower()
            )

            eligible["district"] = (
                eligible["district"]
                .astype(str)
                .str.strip()
                .str.lower()
            )

            # Filter by State + District
            if state and district:
                colleges = eligible[
                    (eligible["state"] == state) &
                    (eligible["district"] == district)
                ]

            elif state:
                colleges = eligible[
                    eligible["state"] == state
                ]

            else:
                colleges = eligible

            colleges = colleges.sort_values(
                by="cutoff",
                ascending=False
            )

            colleges = colleges.to_dict("records")

        except Exception as e:
            return f"Prediction Error: {e}"

    if "state" in df.columns:
        states = sorted(df["state"].dropna().unique())
    else:
        states = []

    return render_template(
        "predict.html",
        result=result,
        chance=chance,
        colleges=colleges,
        states=states
    )
# ---------------- COLLEGES ----------------

@app.route("/colleges")
def colleges():
    return render_template("colleges.html")

#------------------ ADD COLLEGE ----------------#
@app.route("/add_college", methods=["GET", "POST"])
def add_college():

    if "admin" not in session:
        return redirect("/admin")

    if request.method == "POST":

        college_name = request.form["college_name"]
        location = request.form["location"]
        course = request.form["course"]
        cutoff = request.form["cutoff"]
        admission_chance = request.form["admission_chance"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO colleges
        (college_name, location, course, cutoff, admission_chance)
        VALUES (?, ?, ?, ?, ?)
        """,
        (college_name, location, course, cutoff, admission_chance))

        conn.commit()
        conn.close()

        return redirect("/admin_dashboard")

    return render_template("add_college.html")

#----------------CHAT AI----------------#
@app.route("/chat", methods=["GET", "POST"])
def chat():
    answer = ""

    if request.method == "POST":
        question = request.form.get("question", "").strip()

        if question:
            try:
                answer = ask_ai(question)
            except Exception as e:
                answer = f"Error: {str(e)}"

    return render_template("chat.html", answer=answer)
# ---------------- ABOUT ----------------

@app.route("/about")
def about():
    return render_template("about.html")


# ---------------- CONTACT ----------------

@app.route("/contact")
def contact():
    return render_template("contact.html")


# ---------------- COURSES ----------------

@app.route("/courses")
def courses():
    return render_template("courses.html")


# ---------------- EVENTS ----------------

@app.route("/events")
def events():
    return render_template("events.html")


# ---------------- FACULTY ----------------

@app.route("/faculty")
def faculty():
    return render_template("faculty.html")


# ---------------- GALLERY ----------------

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")


# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app.run(debug=True)