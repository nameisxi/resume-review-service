import os, time
from os import getenv
from datetime import datetime

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
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1000 * 1000

    db = SQLAlchemy(app)

    return app, db

app = Flask(__name__, static_folder="static")
app, db = load_configs(app)   

def get_user_id(email):
    user_id = db.session.execute("SELECT id FROM users WHERE email = :email AND deleted = false", {"email": session.get('email')}).fetchone()[0]
    return user_id

def create_account(email, password, reviewer):
    """
        Creates an account.
    """
    hash_value = generate_password_hash(password)

    sql = "INSERT INTO users (email,password,reviewer) VALUES (:email,:password,:reviewer)"
    
    db.session.execute(sql, {"email":email,"password":hash_value,"reviewer":reviewer})
    db.session.commit()

def sign_in(email, reviewer):
    session["email"] = email
    session["user_id"] = get_user_id(email)
    session["reviewer"] = reviewer

def validate_credentials(email, password, account_type):
    """ 
        Validates weather given email and password 
        can be used to create a new account. If yes,
        this function returns a None. If not okay,
        it returns an error message.
    """
    if email.strip is None:
        return "Invalid email address"

    if password is None:
        return "Invalid password"

    if account_type is None:
        return "Invalid account type"

    if account_type != "0" and account_type != "1":
        return "Invalid account type"

    if len(email) > 1000:
        return "Email address too long. Max length: 1000 characters"

    if len(password) < 8:
        return "Password too short. Min length: 8 characters"
    
    if len(password) > 1000:
        return "Password too long. Max length: 1000 characters"

    sql = "SELECT password FROM users WHERE email=:email AND deleted = false"
    result = db.session.execute(sql, {"email":email})
    user = result.fetchone()  

    if user:
        return "There's already an account with this email address"

    return None

def check_credentials(email, password):
    """ 
        Checks weather given email and password 
        can be used to sign in. If yes, this 
        function returns a None. If not okay,
        it returns an error message.
    """

    if email is None:
        return "Invalid email address", None

    if password is None:
        return "Invalid password", None

    if len(email) > 1000:
        return "Email address too long. Max length: 1000 characters", None
    
    if len(password) > 1000:
        return "Password too long. Max length: 1000 characters", None   

    sql = "SELECT password, reviewer FROM users WHERE email=:email AND deleted = false"
    result = db.session.execute(sql, {"email":email}).fetchone()   

    if result == None:
        return "Wrong username", None
    else:
        hash_value = result[0]
        reviewer = result[1]
        if check_password_hash(hash_value, password):
            return None, reviewer
        else:
            return "Wrong password", None

def validate_password_change(current_password, new_password):
    """ 
        Validates weather password change can be made. 
        If yes, this function returns a None. If not okay,
        it returns an error message.
    """
    if current_password is None:
        return "Invalid current password"

    if new_password is None:
        return "Invalid new password"

    if len(current_password) > 1000:
        return "Current password too long. Max length: 1000 characters"

    if len(new_password) < 8:
        return "New password too short. Min length: 8 characters"
    
    if len(new_password) > 1000:
        return "New password too long. Max length: 1000 characters"

    if current_password == new_password:
        return "Current password and new password are the same. Please input different passwords."

    sql = "SELECT password FROM users WHERE id=:user_id AND deleted = false"
    result = db.session.execute(sql, {"user_id":session.get("user_id")}).fetchone()  

    hash_value = result[0]
    if check_password_hash(hash_value, current_password):
        return None
    else:
        return "Wrong current password"

def change_password(new_password):
    sql = """
            UPDATE users
            SET password = :new_password
            WHERE id = :user_id
            AND deleted = false
        """

    hash_value = generate_password_hash(new_password)

    db.session.execute(sql, {"new_password":hash_value,"user_id":session.get("user_id")})
    db.session.commit()

def delete_rating(resume_id):
    """ Deletes a rating from a specified resume associated with the current user_id """

    ratings_sql = """
                    UPDATE ratings
                    SET deleted = true
                    WHERE customer_id = :user_id
                    AND resume_id = :resume_id
                    AND ratings.deleted = false
                  """
    db.session.execute(ratings_sql, {"user_id": session.get("user_id"), "resume_id": resume_id})
    db.session.commit()


def delete_ratings():
    """ Deletes all ratings related to the resumes associated with the current user_id 
        that's about to get deleted """

    ratings_sql = """
                    UPDATE ratings
                    SET deleted = true
                    WHERE customer_id = :user_id
                    AND ratings.deleted = false
                  """
    db.session.execute(ratings_sql, {"user_id": session.get("user_id")})
    db.session.commit()

def delete_message(resume_id):
    """ Deletes messages from a specified resume associated with the current user_id """
    messages_sql = """
                    UPDATE messages
                    SET deleted = true
                    WHERE sender_id = :user_id
                    AND resume_id = :resume_id
                    AND messages.deleted = false
                    OR EXISTS(
                        SELECT * FROM resumes 
                        WHERE resumes.user_id = :user_id
                        AND messages.resume_id = :resume_id  
                        AND resumes.deleted = false  
                    )
                   """
    db.session.execute(messages_sql, {"user_id": session.get("user_id"), "resume_id": resume_id})
    db.session.commit()

def delete_messages():
    """ Deletes all messages related to the resumes associated with the current user_id 
        that's about to get deleted """

    messages_sql = """
                    UPDATE messages
                    SET deleted = true
                    WHERE sender_id = :user_id
                    AND messages.deleted = false
                    OR EXISTS(
                        SELECT * FROM resumes 
                        WHERE resumes.user_id = :user_id
                        AND messages.resume_id = resumes.id  
                        AND resumes.deleted = false  
                    )
                   """
    db.session.execute(messages_sql, {"user_id": session.get("user_id")})
    db.session.commit()

def delete_resume(resume_id):
    """ Deletes a specified resume associated with the current user_id """

    # Hard PDF file deletion
    resumes = fetch_resumes(session.get('email'), False)
    for resume in resumes:
        resume_path = resume[4]
        if resume[3] == resume_id and os.path.isfile(resume_path):
            os.remove(resume_path)

    # Soft resume table deletion
    resumes_sql = """
                    UPDATE resumes
                    SET deleted = true
                    WHERE user_id = :user_id
                    AND id = :id
                    AND deleted = false
                  """
    db.session.execute(resumes_sql, {"user_id": session.get("user_id"), "id": resume_id})
    db.session.commit()

def delete_resumes():
    """ Deletes all resumes associated with the current user_id """

    # Hard PDF file deletion
    resumes = fetch_resumes(session.get('email'), False)
    for resume in resumes:
        resume_path = resume[4]
        if os.path.isfile(resume_path):
            os.remove(resume_path)

    # Soft resume table deletion
    resumes_sql = """
                    UPDATE resumes
                    SET deleted = true
                    WHERE user_id = :user_id
                    AND deleted = false
                  """
    db.session.execute(resumes_sql, {"user_id": session.get("user_id")})
    db.session.commit()

def delete_user():
    """ Deletes all users associated with the current user_id """

    users_sql = """
                    UPDATE users
                    SET deleted = true
                    WHERE id = :user_id
                    AND deleted = false
                """
    db.session.execute(users_sql, {"user_id": session.get("user_id")})
    db.session.commit()


def delete_account():
    """
        Soft deletes user's account (except for the actual pdf resume. They get hard deleted.). 
        Not designed - purposefully - to delete reviewer's account.
        For reviewer's account disabling, see disable_account().
    """

    delete_ratings()
    delete_messages()
    delete_resumes()
    delete_user()

def disable_account():
    """
        Disables reviewer's account by soft deleting the account only on the users table, as deleting reviewer's account could cause lots of trouble.
        This way we can communicate to the user, that the reviewer that they used to communicate with, is no longer active.
        This way we also won't face optimization problems, such as multiple reviewers deleting their accounts, and few reviewers getting huge
        review loads, while new reviewers could start from scratch.
        The user can still see the posted resume and all of the previous communication.
    """
    delete_user()


def fetch_resumes(email, reviewer):
    if not email:
        return []

    query = """
                SELECT resumes.name, users2.email, resumes.created_at, resumes.id, resumes.file_address, users2.deleted 
                FROM resumes
                LEFT JOIN users AS users1
                ON resumes.user_id = users1.id
                LEFT JOIN users AS users2
                ON resumes.reviewer_id = users2.id
                WHERE users1.email = :email
                AND resumes.deleted = false
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
                    AND resumes.deleted = false
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
        return "No resume-field in request"
        
    resume = request.files['resume-field']

    if resume.filename == '':
        return "No resume uploaded"

    if resume and allowed_filename(resume.filename):
        filename = f"{session.get('email')}_{time.time()}_identifier_{resume.filename}"
        if len(filename) > 1000:
            filename = f"{session.get('email')}_{time.time()}_identifier_{resume.filename[-500:]}"

        filename = secure_filename(filename)
        file_address = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume.save(file_address)

        # By using ORDER BY random() LIMIT 1, a random reviewer will be picked
        reviewer_id =  db.session.execute("SELECT id FROM users WHERE reviewer = true AND deleted = false ORDER BY random() LIMIT 1").fetchone()[0]      

        sql = """
                INSERT INTO resumes (user_id,reviewer_id,file_address,name) VALUES (:user_id,:reviewer_id,:file_address,:name) 
            """

        db.session.execute(sql, {"user_id": session.get("user_id"), "reviewer_id": reviewer_id, "file_address": file_address, "name": filename})
        db.session.commit()

        return None

def fetch_messages(resume_id):
    if not resume_id:
        return []

    query = """
                SELECT users.email, messages.created_at, messages.message 
                FROM messages
                LEFT JOIN users 
                ON messages.sender_id = users.id
                WHERE messages.resume_id = :resume_id
                AND messages.deleted = false 
                ORDER BY messages.created_at ASC
            """

    messages = db.session.execute(query, {"resume_id": resume_id}).fetchall()

    return messages

def save_message(resume_id, message):
    if len(message) > 15000:
        # Getting a single message this long (equivalent of 500x, 30 character long, words) is highly unlikely, 
        # so I'll just cut it if it gets past this point
        message = message[:15000]

    sql = "INSERT INTO messages (sender_id,resume_id,message) VALUES (:sender_id,:resume_id,:message)"
    
    db.session.execute(sql, {"sender_id":session.get("user_id"),"resume_id":resume_id,"message":message})
    db.session.commit()

def fetch_rating(resume_id):
    if not resume_id:
        return []

    query = """
                SELECT ratings.rating 
                FROM ratings
                WHERE ratings.resume_id = :resume_id
                AND ratings.deleted = false
                ORDER BY created_at DESC
                LIMIT 1
            """

    rating = db.session.execute(query, {"resume_id": resume_id}).fetchone()

    if rating is None:
        rating = -1
    else:
        rating = rating[0]

    return rating

def save_rating(resume_id, rating):
    if rating not in ["1", "2", "3", "4", "5"]:
        return "Invalid rating"

    sql = "INSERT INTO ratings (customer_id,resume_id,rating) VALUES (:customer_id,:resume_id,:rating)"
    
    db.session.execute(sql, {"customer_id":session.get("user_id"),"resume_id":resume_id,"rating":rating})
    db.session.commit()
    

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

@app.route("/add-resume", methods=['POST'])
def add_resume():
    if session.get('email'):
        error = upload_resume(request)

        if error:
            return render_template("resumes.html", resumes=resumes, error=error)
        
        latest_resume = fetch_resumes(session.get("email"), session.get("reviewer"))[0]
        resume_id = latest_resume[3]

        return redirect(f"/resumes/{resume_id}")

    return redirect("/")

@app.route("/delete-resume/<int:resume_id>", methods=['POST'])
def del_resume(resume_id):
    if session.get("user_id") and not session.get("reviewer"):
        delete_rating(resume_id)
        delete_message(resume_id)
        delete_resume(resume_id)
        
        return redirect("/resumes")

    return redirect("/")

@app.route("/send-message/<int:resume_id>", methods=['POST']) 
def send_message(resume_id):
    if session.get('email'):
        message = request.form["message"].strip()
        resumes = fetch_resumes(session.get('email'), session.get('reviewer'))
        
        for resume in resumes:
            if resume[3] == resume_id and message:
                save_message(resume_id, message)
                return redirect(f"/resumes/{resume_id}")
    
    return redirect("/")

@app.route("/give-rating/<int:resume_id>", methods=['POST'])
def give_rating(resume_id):
    if session.get('email') and not session.get('reviewer'):
        rating = request.form['rate'].strip()

        resumes = fetch_resumes(session.get('email'), session.get('reviewer'))
        
        for resume in resumes:
            if resume[3] == resume_id and rating:
                save_rating(resume_id, rating)
                return redirect(f"/resumes/{resume_id}")

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
            rating = fetch_rating(resume_id)
            return render_template("single_resume_view.html", resume=resume, messages=messages, rating=rating)

    return redirect("/")

@app.route("/uploads/<path:file_address>", methods=['GET']) 
def serve_resume(file_address):
    if session.get("email"):
        file_address = f"./{file_address}"
        resumes = fetch_resumes(session.get('email'), session.get('reviewer'))
        
        for resume in resumes:
            if resume[4] == file_address:
                return send_from_directory('', file_address)
        
        return "No resume found"

    return redirect("/")

@app.route("/account/", methods=['GET'])
def account():
    if session.get("email"):
        if session.get("password-change-success"):
            success = session["password-change-success"]
            del session["password-change-success"]

            return render_template("account.html", success=success)

        if session.get("password-change-error"):
            error = session["password-change-error"]
            del session["password-change-error"]

            return render_template("account.html", error=error)
        
        return render_template("account.html") 

    return redirect("/")

@app.route("/change-password/<int:user_id>", methods=['POST'])
def password(user_id):
    if session.get("user_id") and session.get("user_id") == user_id:
        current_password = request.form["current-password"].strip()
        new_password = request.form["new-password"].strip()

        error = validate_password_change(current_password, new_password)

        if error is None:
            change_password(new_password)
            session["password-change-success"] = "Password successfully changed."
            return redirect("/account")

        session["password-change-error"] = error
        return redirect("/account")

    return redirect("/")

@app.route("/change-password/<int:user_id>", methods=['GET'])
def password_attempt():
    if session.get("email"):
        return redirect("/account")
    return redirect("/")

@app.route("/delete-account/<int:user_id>", methods=['POST'])
def delete(user_id):
    if session.get("user_id") and session.get("user_id") == user_id and not session.get("reviewer"):
        delete_account()
        return redirect("/signout")

    return redirect("/")

@app.route("/disable-account/<int:user_id>", methods=['POST'])
def disable(user_id):
    if session.get("user_id") and session.get("user_id") == user_id and session.get("reviewer"):
        disable_account()
        return redirect("/signout")

    return redirect("/")

@app.route("/signup", methods=['GET'])
def signup_template():
    return render_template("signup.html")

@app.route("/signup", methods=["POST"])
def signup():
    if session.get("email"):
        return redirect("/signout")
        
    email = request.form["email"].lower().strip()
    password = request.form["password"].strip()
    account_type = request.form["account-type"].strip()

    error = validate_credentials(email, password, account_type)

    if error is None:
        create_account(email, password, account_type == "1")
        sign_in(email, account_type == "1")
        return redirect("/")
    return render_template("signup.html", error=error)

@app.route("/signin", methods=["POST"])
def signin():
    if session.get("email"):
        return redirect("/signout")

    email = request.form["email"].lower().strip()
    password = request.form["password"].strip()

    error, reviewer = check_credentials(email, password)

    if error is None:
        sign_in(email, reviewer)
        return redirect("/")
    return render_template("index.html", error=error)

@app.route("/signout")
def signout():
    del session["email"]
    del session["user_id"]
    del session['reviewer']

    return redirect("/")


