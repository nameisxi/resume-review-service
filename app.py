from flask import Flask
from flask import redirect, render_template, request, session

from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy

from os import getenv


def load_configs(app):
    # Session configs
    app.secret_key = getenv("SECRET_KEY")
    # DB configs
    app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db = SQLAlchemy(app)

    return app, db

app = Flask(__name__)
app, db = load_configs(app)

@app.route("/")
def index():
    return render_template("index.html")

#@app.route("/register", methods=["POST"])
def register(email, password):
    hash_value = generate_password_hash(password)

    sql = "INSERT INTO users (email,password,reviewer) VALUES (:email,:password,:reviewer)"
    
    db.session.execute(sql, {"email":email,"password":hash_value,"reviewer":False})
    db.session.commit()

def login(email):
    session["email"] = email
    return redirect("/")

def validate_credentials(email, password):
    if not email:
        return "Invalid email address"\

    if not password:
        return "Invalid password"

    sql = "SELECT password FROM users WHERE email=:email"
    result = db.session.execute(sql, {"email":email})
    user = result.fetchone()  

    if user:
        return "Username taken"

    return None

def check_credentials(email, password):
    if not email:
        return "Invalid email address"\

    if not password:
        return "Invalid password"

    sql = "SELECT password FROM users WHERE email=:email"
    result = db.session.execute(sql, {"email":email})
    user = result.fetchone()   

    if user == None:
        return "Invalid username"
    else:
        hash_value = user[0]
        if check_password_hash(hash_value,password):
            return None
        else:
            # Invalid password
            return "Invalid password"

@app.route("/authenticate",methods=["POST"])
def authenticate():
    email = request.form["email"]
    password = request.form["password"]

    if request.form["register"]:
        result = validate_credentials()
        if not result():
            return register()
        return result

    if request.form["login"]:
        result = check_credentials()
        if not result:
            return login()
        return result

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

