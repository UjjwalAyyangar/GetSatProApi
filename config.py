import os
import datetime

class Config(object):
    SECRET_KEY = 'ujjwal-is-awesome'
    JWT_SECRET_KEY = 'secret'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)
