# The data access layer

# Some of these methods could have been written in models
# but I wanted these separate. For better code organization.
from app.models import *
from app import db, flask_bcrypt
import sqlalchemy
from flask_login import current_user
from app.constants import *

from app.dac import general as gen_dac


def get_user(uname=None, user_id=None):
    try:
        if uname:
            return UserInfo.query.filter_by(Username=uname).one()
        elif user_id:
            return UserInfo.query.filter_by(User_ID=user_id).one()
        else:
            return None
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def get_users(role_id):
    try:
        return UserInfo.query.filter_by(Role_ID=role_id).all()
    except:
        return None


def create_user(data):
    """

    :param data: a dictionary that contains the information about a new user
    :return: None if there was trouble creating a user, a UserInfo model object otherwise
    """
    pwd = flask_bcrypt.generate_password_hash(data.get('password'))

    new_user = UserInfo(
        Username=data[USERNAME],
        Login_password=pwd,
        First_Name=data[USER_FNAME],
        Last_Name=data[USER_LNAME],
        Email=data[EMAIL],
        Phone=data[PHONE],
        Role_ID=int(data[ROLE_ID])
    )

    #print(new_user)
    return gen_dac.insert(new_user)
