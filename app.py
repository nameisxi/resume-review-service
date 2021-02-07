import os
from os import getenv

from flask import Flask
from flask import redirect, render_template, request, session, url_for, flash

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy


def load_configs(app):
    # Session configs
    app.secret_key = getenv("SECRET_KEY")
    # DB configs
    app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # File saving configs
    app.config['UPLOAD_FOLDER'] = './resumes/'

    db = SQLAlchemy(app)

    return app, db

app = Flask(__name__)
app, db = load_configs(app)   


def create_account(email, password, reviewer):
    """
        Creates an account.
    """
    hash_value = generate_password_hash(password)

    sql = "INSERT INTO users (email,password,reviewer) VALUES (:email,:password,:reviewer)"
    
    db.session.execute(sql, {"email":email,"password":hash_value,"reviewer":reviewer})
    db.session.commit()

    return sign_in(email)

def sign_in(email, reviewer):
    session["email"] = email
    session["reviewer"] = reviewer

    print("****************")
    print(session.get('reviewer'))

    return redirect("/")

def validate_credentials(email, password):
    """ 
        Validates weather given email and password 
        can be used to create a new account. If yes,
        this function returns a None. If not okay,
        it returns an error message.
    """
    if not email.strip():
        return "Invalid email address"

    if not password.strip():
        return "Invalid password"

    sql = "SELECT password FROM users WHERE email=:email"
    result = db.session.execute(sql, {"email":email})
    user = result.fetchone()  

    if user:
        return "There's already an account with this email address"

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

    sql = "SELECT password, reviewer FROM users WHERE email=:email"
    result = db.session.execute(sql, {"email":email}).fetchone()   

    if result == None:
        return "Invalid username", None
    else:
        hash_value = result[0]
        reviewer = result[1]
        if check_password_hash(hash_value,password):
            return None, reviewer
        else:
            return "Invalid password", None

def fetch_resumes(email, reviewer):
    if not email:
        return []

    query = """
                SELECT resumes.name, users2.email, resumes.created_at 
                FROM resumes
                LEFT JOIN users AS users1
                ON resumes.user_id = users1.id
                LEFT JOIN users AS users2
                ON resumes.reviewer_id = users2.id
                WHERE users1.email = :email
            """

    if reviewer:
        query = """
                    SELECT resumes.name, users2.email, resumes.created_at 
                    FROM resumes
                    LEFT JOIN users AS users1
                    ON resumes.reviewer_id = users1.id
                    LEFT JOIN users AS users2
                    ON resumes.user_id = users2.id
                    WHERE users1.email = :email
                """

    resumes = db.session.execute(query, {"email": email}).fetchall()

    return resumes

def allowed_filename(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in 'pdf'

def upload_resume(request):
    if 'resume' not in request.files:
        flash('No resume part')
        return redirect(request.url)
        
    resume = request.files['resume']

    if resume.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if resume and allowed_filename(resume.filename):
        filename = secure_filename(resume.filename)
        file_address = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        resume.save(file_address)

        user_id = db.session.execute("SELECT id FROM users WHERE email = :email", {"email": session.get('email')}).fetchone()[0]
        # By using ORDER BY random() LIMIT 1, a random reviewer will be picked
        reviewer_id =  db.session.execute("SELECT id FROM users WHERE reviewer = true ORDER BY random() LIMIT 1").fetchone()[0]      

        sql = """
                   INSERT INTO resumes (user_id,reviewer_id,file_address,name) VALUES (:user_id,:reviewer_id,:file_address,:name) 
                """

        db.session.execute(sql, {"user_id": user_id, "reviewer_id": reviewer_id, "file_address": file_address, "name": filename})
        db.session.commit()

        return redirect("/resumes")

@app.route("/")
def index():
    if session.get('email'):
        return redirect("/resumes")
    return render_template("index.html") 

@app.route("/resumes")
def resumes():
    if session.get('email'):
        resumes = fetch_resumes(session.get('email'), session.get('reviewer'))
        return render_template("resumes.html", resumes=resumes)
    return redirect("/")

@app.route("/add-resume", methods=['GET'])
def add_resume_template():
    if session.get('email'):
        return render_template("add_resume.html")
    return redirect("/")

@app.route("/add-resume", methods=['POST'])
def add_resume():
    if session.get('email'):
        upload_resume(request)
    return redirect("/")

@app.route("/signup", methods=['GET'])
def signup_template():
    return render_template("signup.html")

@app.route("/signup", methods=["POST"])
def signup():
    email = request.form["email"].lower().strip()
    password = request.form["password"].strip()
    user_type = request.form["user-type"]

    result = validate_credentials(email, password)

    if result is None:
        return create_account(email, password, user_type == "1")
    return result

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"].lower().strip()
    password = request.form["password"].strip()

    result, reviewer = check_credentials(email, password)

    if result is None:
        return sign_in(email, reviewer)

    return result

@app.route("/logout")
def logout():
    del session["email"]
    del session['reviewer']
    return redirect("/")


