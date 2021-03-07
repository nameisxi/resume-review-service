import os, time

from flask import session
from werkzeug.utils import secure_filename

from app import app
from db import db


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
                ORDER BY resumes.created_at DESC
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
                    ORDER BY resumes.created_at DESC
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
