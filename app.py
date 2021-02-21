import os, time
from os import getenv

from flask import Flask
from flask import redirect, render_template, request, session, url_for, flash, send_from_directory

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

def get_user_id(email):
    user_id = db.session.execute("SELECT id FROM users WHERE email = :email", {"email": session.get('email')}).fetchone()[0]
    return user_id

def create_account(email, password, reviewer):
    """
        Creates an account.
    """
    hash_value = generate_password_hash(password)

    sql = "INSERT INTO users (email,password,reviewer) VALUES (:email,:password,:reviewer)"
    
    db.session.execute(sql, {"email":email,"password":hash_value,"reviewer":reviewer})
    db.session.commit()

    return sign_in(email, reviewer)

def sign_in(email, reviewer):
    session["email"] = email
    session["user_id"] = get_user_id(email)
    session["reviewer"] = reviewer

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
        return "Invalid email address", None

    if not password:
        return "Invalid password", None

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
                SELECT resumes.name, users2.email, resumes.created_at, resumes.id, resumes.file_address 
                FROM resumes
                LEFT JOIN users AS users1
                ON resumes.user_id = users1.id
                LEFT JOIN users AS users2
                ON resumes.reviewer_id = users2.id
                WHERE users1.email = :email
            """

    if reviewer:
        query = """
                    SELECT resumes.name, users2.email, resumes.created_at, resumes.id, resumes.file_address
                    FROM resumes
                    LEFT JOIN users AS users1
                    ON resumes.reviewer_id = users1.id
                    LEFT JOIN users AS users2
                    ON resumes.user_id = users2.id
                    WHERE users1.email = :email
                """

    resumes = db.session.execute(query, {"email": email}).fetchall()

    return resumes

def resume_chunks(resumes, n):
    """
        Splits a list into n-sized chunks 
    """
    for i in range(0, len(resumes), n):
        yield resumes[i:i + n]

def allowed_filename(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in 'pdf'

def upload_resume(request):
    if 'resume-field' not in request.files:
        flash('No resume part')
        return redirect(request.url)
        
    resume = request.files['resume-field']

    if resume.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if resume and allowed_filename(resume.filename):
        filename = f"{session.get('email')}_{time.time()}_identifier_{resume.filename}"
        filename = secure_filename(filename)
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

def fetch_messages(resume_id):
    if not resume_id:
        return []

    query = """
                SELECT users.email, messages.created_at, messages.message 
                FROM messages
                LEFT JOIN users 
                ON messages.sender_id = users.id
                WHERE messages.resume_id = :resume_id
                ORDER BY messages.created_at ASC
            """

    messages = db.session.execute(query, {"resume_id": resume_id}).fetchall()

    return messages

def save_message(resume_id, message):
    sender_id = db.session.execute("SELECT id FROM users WHERE email = :email", {"email": session.get('email')}).fetchone()[0]

    sql = "INSERT INTO messages (sender_id,resume_id,message) VALUES (:sender_id,:resume_id,:message)"
    
    db.session.execute(sql, {"sender_id":sender_id,"resume_id":resume_id,"message":message})
    db.session.commit()

    return redirect(f"/resumes/{resume_id}")

@app.route("/", methods=['GET'])
def index():
    if session.get('email'):
        return redirect("/resumes")
    return render_template("index.html") 

@app.route("/resumes", methods=['GET'])
def resumes():
    if session.get('email'):
        resumes = fetch_resumes(session.get('email'), session.get('reviewer'))
        resumes = resume_chunks(resumes, 3)
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

@app.route("/send-message/<int:resume_id>", methods=['POST']) 
def send_message(resume_id):
    if session.get('email'):
        message = request.form["message"].strip()
        resumes = fetch_resumes(session.get('email'), session.get('reviewer'))
        
        for resume in resumes:
            if resume[3] == resume_id and message:
                return save_message(resume_id, message)
    
    return redirect("/")
        

@app.route("/resumes/<int:resume_id>", methods=['GET'])
def resume_view(resume_id):
    if session.get('email'):
        resumes = fetch_resumes(session.get('email'), session.get('reviewer'))
        resume_index = None

        for i, resume in enumerate(resumes):
            if resume[3] == resume_id:
                resume_index = i

        if resume_index is not None:
            resume = resumes[resume_index]
            messages = fetch_messages(resume_id)
            return render_template("single_resume_view.html", resume=resume, messages=messages)

    return redirect("/")

@app.route("/uploads/<path:file_address>", methods=['GET']) 
def serve_resume(file_address):
    file_address = f"./{file_address}"

    if session.get("email"):
        resumes = fetch_resumes(session.get('email'), session.get('reviewer'))
        
        for resume in resumes:
            if resume[4] == file_address:
                return send_from_directory('', file_address)
        
        return "No resume found"

    return redirect("/")

@app.route("/signup", methods=['GET'])
def signup_template():
    return render_template("signup.html")

@app.route("/signup", methods=["POST"])
def signup():
    email = request.form["email"].lower().strip()
    password = request.form["password"].strip()
    user_type = request.form["user-type"]

    error = validate_credentials(email, password)

    if error is None:
        return create_account(email, password, user_type == "1")
    return render_template("signup.html", error=error)

@app.route("/signin", methods=["POST"])
def signin():
    email = request.form["email"].lower().strip()
    password = request.form["password"].strip()

    error, reviewer = check_credentials(email, password)

    if error is None:
        return sign_in(email, reviewer)
    return render_template("index.html", error=error)

@app.route("/signout")
def signout():
    del session["email"]
    del session["user_id"]
    del session['reviewer']

    return redirect("/")


