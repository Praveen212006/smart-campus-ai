from flask import Flask, render_template, request, redirect, session
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

from predict import predict_admission


app = Flask(__name__)

app.secret_key = "smart_ai_portal"



# ---------------- CREATE DATABASE ----------------

def create_database():

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    conn.commit()

    conn.close()



create_database()



# ---------------- HOME ----------------

@app.route("/")
def home():

    return render_template("index.html")




# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]

        email = request.form["email"]

        password = request.form["password"]


        try:

            conn = sqlite3.connect("database.db")

            cur = conn.cursor()


            cur.execute(
                """
                INSERT INTO users(name,email,password)
                VALUES(?,?,?)
                """,
                (name,email,password)
            )


            conn.commit()

            conn.close()


            return redirect("/login")


        except sqlite3.IntegrityError:

            return "Email already registered"



    return render_template("register.html")





# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":


        email = request.form["email"]

        password = request.form["password"]



        conn = sqlite3.connect("database.db")

        cur = conn.cursor()



        cur.execute(
            """
            SELECT * FROM users
            WHERE email=? AND password=?
            """,
            (email,password)
        )



        user = cur.fetchone()


        conn.close()



        if user:

            session["user"] = user[1]

            return redirect("/dashboard")


        else:

            return "Invalid Email or Password"



    return render_template("login.html")





# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.pop("user",None)

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

@app.route("/predict", methods=["GET","POST"])
def predict():

    result = None

    if request.method == "POST":

        score = float(request.form["score"])

        cutoff = float(request.form["cutoff"])


        result = predict_admission(
            score,
            cutoff
        )


    return render_template(
        "predict.html",
        result=result
    )



# ---------------- COLLEGES ----------------

@app.route("/colleges")
def colleges():

    return render_template(
        "colleges.html"
    )



# ---------------- ABOUT ----------------

@app.route("/about")
def about():

    return render_template(
        "about.html"
    )



# ---------------- CONTACT ----------------

@app.route("/contact")
def contact():

    return render_template(
        "contact.html"
    )



# ---------------- COURSES ----------------

@app.route("/courses")
def courses():

    return render_template(
        "courses.html"
    )



# ---------------- EVENTS ----------------

@app.route("/events")
def events():

    return render_template(
        "events.html"
    )



# ---------------- FACULTY ----------------

@app.route("/faculty")
def faculty():

    return render_template(
        "faculty.html"
    )



# ---------------- GALLERY ----------------

@app.route("/gallery")
def gallery():

    return render_template(
        "gallery.html"
    )




# ---------------- RUN APP ----------------

if __name__ == "__main__":

    app.run(
        debug=True
    )