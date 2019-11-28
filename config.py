import os
import datetime

# from os.path import join, dirname, realpath

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = 'ujjwal-is-awesome'
    JWT_SECRET_KEY = 'secret'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'getSatPro.db')
    # 'postgresql://localhost/getSatPro.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_HEADERS = 'Content-Type'

    UPLOAD_FOLDER = os.path.join(basedir, "files")

    CORS_ALLOW_CREDENTIALS = True
    # SESSION_COOKIE_SECURE = True
    CORS_ORIGIN_WHITELIST = (
        'localhost:3000'
    )
    # SESSION_COOKIE_SAMESITE = 'Lax'


# 'sqlite:///getSatPro.db' 'sqlite:///' +

# 'postgresql://localhost/wordcount_dev'
# 'sqlite:///' '+ os.path.join(basedir,' 'getSatPro.db')

class FirebaseConfig(object):
    def __init__(self):
        self.service_folder = os.path.join("app", "service_account_firebase.json")
        self.service_path = os.path.join(basedir, self.service_folder)
        self.config = {
            "apiKey": "AIzaSyDs6bBEMn-nxyRpO7t_2xtWBY1QNVKK3yo",
            "authDomain": "get-sat-pro.firebaseapp.com",
            "databaseURL": "https://get-sat-pro.firebaseio.com",
            "projectId": "get-sat-pro",
            "storageBucket": "get-sat-pro.appspot.com",
            "messagingSenderId": "528678626334",
            "appId": "1:528678626334:web:f67ac1dbca8a2a63ed3a0f",
            "measurementId": "G-LT5K4CF5G1",
            "serviceAccount": self.service_path
        }

    def get_config(self):
        return self.config

    def get_service_path(self):
        return self.service_path
