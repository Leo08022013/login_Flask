import os
from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "8bba1a324c83c0dee3ac3e7e045befea6abbb31de8f3e31ed378dca2abb4e065"

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/home-page")
def home_page():
    if "user_id" not in session:
        print("--- DEBUG: Kein user_id in Session! Zurück zum Login. ---")
        flash("Please log in to access the home page.", "warning")
        return redirect(url_for("login"))
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            print(
                f"--- DEBUG: Login erfolgreich! Session user_id gesetzt auf: {user.id} ---"
            )
            flash("Login successful!", "success")
            return redirect(url_for("home_page"))
        else:
            print(
                "--- DEBUG: Login fehlgeschlagen! Falsche Daten oder User existiert nicht. ---"
            )
            flash("Invalid email or password.", "danger")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        print(f"--- DEBUG: Signup-Formular abgeschickt! Email: {email} ---")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print("--- DEBUG: Registrierung gestoppt – Email existiert bereits! ---")
            flash("Email already exists. Please log in.", "warning")
            return redirect(url_for("login"))

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        print(f"--- DEBUG: User erfolgreich in DB gespeichert! ID: {new_user.id} ---")
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    print("--- DEBUG: User ausgeloggt! Session user_id entfernt. ---")
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("--- DEBUG: Datenbank-Tabellen wurden initialisiert! ---")
    app.run(debug=True, port=5002)
