from flask import session

from db import db


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

