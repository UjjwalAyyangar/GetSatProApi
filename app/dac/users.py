# DATA ACCESS LAYER - USERS

from app.models import *
from app import db, flask_bcrypt
import sqlalchemy
from flask_login import current_user
from app.constants import *
from app.dac import flashcards as fc_dac
from app.dac import general as gen_dac


def get_user(uname=None, user_id=None):
    print(user_id)
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
    # if admin
    if int(data[ROLE_ID] == 3):
        security_pwd = flask_bcrypt.generate_password_hash(data[SECURITY_PWD])
        new_user = UserInfo(
            Username=data[USERNAME],
            Login_password=pwd,
            First_Name=data[USER_FNAME],
            Last_Name=data[USER_LNAME],
            Email=data[EMAIL],
            Phone=data[PHONE],
            Role_ID=int(data[ROLE_ID]),
            Security_password=security_pwd
        )
    else:
        new_user = UserInfo(
            Username=data[USERNAME],
            Login_password=pwd,
            First_Name=data[USER_FNAME],
            Last_Name=data[USER_LNAME],
            Email=data[EMAIL],
            Phone=data[PHONE],
            Role_ID=int(data[ROLE_ID])
        )

    # print(new_user)
    return gen_dac.insert(new_user)


def get_tutors(data):
    if MODULE_ID in data:
        return TutorModule.query.filter_by(Module_ID=data[MODULE_ID]).all()
    else:
        return TutorModule.query.all()


def admin_auth(data):
    if SECURITY_PWD not in data:
        return False

    pwd = data[SECURITY_PWD]
    if flask_bcrypt.check_password_hash(current_user.Security_password, pwd):
        return True
    else:
        return False


def setup_pref(user):
    # Make the user's preference table
    if user.Role_ID == 1:
        flashcards = Flashcard.query.all()
        for card in flashcards:
            new_fc_pref = fc_dac.fc_pref_init(card.FC_ID, user.User_ID)
