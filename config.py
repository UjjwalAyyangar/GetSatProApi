import os
import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = 'ujjwal-is-awesome'
    JWT_SECRET_KEY = 'secret'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'getSatPro.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# 'sqlite:///getSatPro.db' 'sqlite:///' +