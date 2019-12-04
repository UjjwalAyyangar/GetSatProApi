# DATA ACCESS LAYER - USERS

from app.models import *
from app import db, flask_bcrypt
import sqlalchemy
from flask_login import current_user
from app.constants import *
from app.dac import flashcards as fc_dac
from app.dac import general as gen_dac


def get_user(uname=None, user_id=None):
    """

    :param uname: string : The username of a user
    :param user_id: integer : the user_id of a user
    :return: the object of a field from the user model/table, None otherwise
    """

    try:
        if uname:
            # querying by username
            return UserInfo.query.filter_by(Username=uname).one()
        elif user_id:
            # querying by user id
            return UserInfo.query.filter_by(User_ID=user_id).one()
        else:
            return None
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def get_users(role_id):
    """ A utility function that is used to return all the users of a given role_id

    :param role_id: the role id of a user
    :return: a list containing fields from UserInfo table as objects
    """
    try:
        # quering all the users of the specified role id
        return UserInfo.query.filter_by(Role_ID=role_id).all()
    except:
        return None


def create_user(data):
    """

    :param data: a dictionary that contains the information about a new user
    :return: None if there was trouble creating a user, a UserInfo model object otherwise
    """
    pwd = flask_bcrypt.generate_password_hash(data.get('password'))

    if int(data[ROLE_ID] == 3):  # creating an admin
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
    else:  # creating a non-admin
        new_user = UserInfo(
            Username=data[USERNAME],
            Login_password=pwd,
            First_Name=data[USER_FNAME],
            Last_Name=data[USER_LNAME],
            Email=data[EMAIL],
            Phone=data[PHONE],
            Role_ID=int(data[ROLE_ID])
        )

    return gen_dac.insert(new_user)


def get_tutors(data):
    """ A utility function that is used to return all the tutors in a module/system

    :param data: dict : empty if we want all the tutors in the system, contains mod_id otherwise :
                        - mod_id : integer : id of the module whose tutors are wanted
    :return: list of tutors
    """
    if MODULE_ID in data:
        return TutorModule.query.filter_by(Module_ID=data[MODULE_ID]).all()
    else:
        return TutorModule.query.all()


def admin_auth(data):
    """ A utility function that is used for checking the second admin authorization

    :param data: dict: contains details about the request data sent by the client
    :return: True, if the security password received from the client is correct, False otherwise
    """
    if SECURITY_PWD not in data:
        return False

    pwd = data[SECURITY_PWD]
    if flask_bcrypt.check_password_hash(current_user.Security_password, pwd):
        return True
    else:
        return False


def setup_pref(user):
    """ A utility function that is used to setup the preference table when a user is created

    :param user: obj : newly created user object
    """
    # Make the user's preference table
    if user.Role_ID == 1:
        flashcards = Flashcard.query.all()
        for card in flashcards:
            new_fc_pref = fc_dac.fc_pref_init(card.FC_ID, user.User_ID)
