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
from flasgger import Swagger

# from app.models import *

# engine = create_engine('sqlite:///getSatPro.db')
# DBSession = sessionmaker(bind=engine)
# session = DBSession()
# Base = declarative_base()


app = Flask(__name__)
app.config.from_object(Config)

CORS(app)
db = SQLAlchemy(app)

migrate = Migrate(app, db)

flask_bcrypt = Bcrypt(app)
jwt = JWTManager(app)
login = LoginManager(app)
# Swagger(app)

from app import routes
from app.scripts import openapi

openapi.make_doc()
"""
from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin

import json

spec = APISpec(
    title="Get Sat Pro API",
    version="0.0.1",
    info=dict(
        description='For devs, by a devs',
    ),
    plugins=[FlaskPlugin()],
    openapi_version="3.0.2"
)

from app.routes import *

with app.test_request_context():
    spec.path(view=index)

with open('swagger.json', 'w') as f:
    json.dump(spec.to_dict(), f)

"""
"""

db = SQLAlchemy()
migrate = Migrate()
flask_bcrypt = Bcrypt()
jwt = JWTManager()
login = LoginManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    flask_bcrypt.init_app(app)
    jwt.init_app(app)
    login.init_app(app)

    return app

app = create_app()
"""

# from app import routes
