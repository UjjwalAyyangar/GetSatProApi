from flask import Flask
from config import Config, FirebaseConfig
from flask_migrate import Migrate
from flask_login import LoginManager
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, asc
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import pyrebase

app = Flask(__name__)
# cors = CORS(app, resources={r"/foo": {"origins": "http://localhost:port"}})

app.config.from_object(Config)
# app.config.update(
#    SESSION_COOKIE_SAMESITE='Lax',
# )
# print(app.config)
# resources={r"/foo": {"origins": "http://localhost:port"}}
CORS(app, support_credentials=True)  # , resources={r"/get_students": {"origins": "http://localhost:3000"}})
db = SQLAlchemy(app)

migrate = Migrate(app, db)

flask_bcrypt = Bcrypt(app)
jwt = JWTManager(app)
login = LoginManager(app)

firebase_config = FirebaseConfig()
firebase = pyrebase.initialize_app(firebase_config.get_config())
storage = firebase.storage()
# Swagger(app)


from .services import (
    users,
    discussions,
    exams,
    grades,
    modules,
    flashcards,
    admin,
    docs,
    files
)

app.register_blueprint(users.mod)
app.register_blueprint(discussions.mod)
app.register_blueprint(exams.mod)
app.register_blueprint(grades.mod)
app.register_blueprint(modules.mod)
app.register_blueprint(flashcards.mod)
app.register_blueprint(admin.mod)
app.register_blueprint(docs.mod)
app.register_blueprint(files.mod)

# from app import routes
from app.scripts import openapi

# openapi.make_doc()
