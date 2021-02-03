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


def create_account(email, password):
    hash_value = generate_password_hash(password)

    sql = "INSERT INTO users (email,password,reviewer) VALUES (:email,:password,:reviewer)"
    
    db.session.execute(sql, {"email":email,"password":hash_value,"reviewer":False})
    db.session.commit()

    return sign_in(email)

def sign_in(email):
    session["email"] = email
    return redirect("/")

def validate_credentials(email, password):
    """ 
        Validates weather given email and password 
        can be used to create a new account. If yes,
        this function returns a None. If not okay,
        it returns an error message.
    """
    if not email.strip():
        return "Invalid email address"\

    if not password.strip():
        return "Invalid password"

    sql = "SELECT password FROM users WHERE email=:email"
    result = db.session.execute(sql, {"email":email})
    user = result.fetchone()  

    if user:
        return "Username taken"

    return None

def check_credentials(email, password):
    """ 
        Checks weather given email and password 
        can be used to login. If yes, this 
        function returns a None. If not okay,
        it returns an error message.
    """

    if not email:
        return "Invalid email address"

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
            return "Invalid password"

@app.route("/")
def index():
    return render_template("index.html") 

@app.route("/signup", methods=['GET'])
def signup_template():
    return render_template("signup.html")

@app.route("/signup", methods=["POST"])
def signup():
    email = request.form["email"].lower().strip()
    password = request.form["password"].strip()

    result = validate_credentials(email, password)

    if result is None:
        return create_account(email, password)
    return result

#@app.route("/signin", methods=['GET'])
#def login_template():
#    pass

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"].lower().strip()
    password = request.form["password"].strip()

    result = check_credentials(email, password)

    if result is None:
        return sign_in(email)
    return result

@app.route("/logout")
def logout():
    del session["email"]
    return redirect("/")

"""@app.route("/authenticate",methods=["POST"])
def authenticate():
    email = request.form["email"].lower().strip()
    password = request.form["password"].strip()
    print("YASS")
    if request.form["register"]:
        print("eiiii")
        result = validate_credentials(email, password)
        if result is None:
            return register(email, password)
        return result

    if request.form["login"]:
        print("yaaas")
        result = check_credentials(email, password)
        if result is None:
            return login(email)
        return result"""

