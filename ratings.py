from flask import session

from db import db


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