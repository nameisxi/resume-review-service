from flask import redirect, render_template, request, session, send_from_directory

from app import app
from logic import *
from resumes import *
from messages import * 
from ratings import *
from delete import *


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
