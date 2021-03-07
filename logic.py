from flask import session
from werkzeug.security import check_password_hash, generate_password_hash

from db import db


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
