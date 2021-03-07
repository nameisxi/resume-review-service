import os

from flask import session

from db import db
from resumes import fetch_resumes


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
