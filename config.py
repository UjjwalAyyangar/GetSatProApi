import os
import datetime

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = 'ujjwal-is-awesome'
    JWT_SECRET_KEY = 'secret'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'getSatPro.db')
    # 'postgresql://localhost/getSatPro.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_HEADERS = 'Content-Type'
    # SESSION_COOKIE_SAMESITE = 'Lax'

# 'sqlite:///getSatPro.db' 'sqlite:///' +

# 'postgresql://localhost/wordcount_dev'
# 'sqlite:///' '+ os.path.join(basedir,' 'getSatPro.db')
