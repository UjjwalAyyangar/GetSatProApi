from flask import Flask
from config import Config
from flask_migrate import Migrate
from flask_login import LoginManager
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, asc
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS

#from app.models import *

#engine = create_engine('sqlite:///getSatPro.db')
#DBSession = sessionmaker(bind=engine)
#session = DBSession()
#Base = declarative_base()


app = Flask(__name__)
app.config.from_object(Config)

CORS(app)
db = SQLAlchemy(app)

migrate =Migrate(app,db)

flask_bcrypt = Bcrypt(app)
jwt = JWTManager(app)
login = LoginManager(app)

from app import routes
