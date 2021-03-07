from os import getenv 

from flask import Flask


def load_configs(app):
    # Session configs
    app.secret_key = getenv("SECRET_KEY")
    # DB configs
    app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # File saving configs
    app.config['UPLOAD_FOLDER'] = './resumes/'
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1000 * 1000

    return app

app = Flask(__name__, static_folder="static")
app = load_configs(app) 

import routes
