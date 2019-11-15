# The data access layer

# Some of these methods could have been written in models
# but I wanted these separate. For better code organization.
from app.models import *
from app import db, flask_bcrypt
import sqlalchemy
from flask_login import current_user
from app.constants import *
# from .general import *

from app.dac import modules as mod_dac
from app.dac import users as users_dac
from app.dac import exams as exams_dac
from app.dac import flashcards as fc_dac
from app.dac import discussions as disc_dac
from app.dac import grades as grade_dac


def exists(name, obj, res):
    """
    :param name: The name of the object - Discussion, Module, User, etc
    :param obj: The object
    :param res: Our response object, which will return the final API response
    :return: The response object
    """
    if obj:
        return res
    else:
        res.code = 400
        res.msg = "Bad Request. Probably {} already exists".format(name)
        return res


def insert(field):
    """

    :param field: the object of the field that needs to be inserted

    :return: None if the field already exists, otherwise the field object
    """
    try:
        db.session.add(field)
        db.session.commit()
        return field
    except sqlalchemy.exc.IntegrityError:
        return None


def delete(field):
    """

    :param field: the object of the field that needs to be deleted
    :return: True if deletion was successful, False otherwise
    """
    try:
        db.session.delete(field)
        db.session.commit()
        return True
    except sqlalchemy.orm.exc.NoResultFound:
        return False


def get_model_obj(model_name):
    model = {
        'Module': Module,
        'UserInfo': UserInfo,
        'UserRole': UserRole,
        'Discussion': Discussion,
        'D_thread': DiscussionThread,
        'Flashcard': Flashcard,
        'FlashcardSet': FlashcardSet
    }

    return model[model_name]


def get_model_field(model_name, data):
    if model_name == 'Module':
        return mod_dac.get_module(data)
    elif model_name == 'User':
        return users_dac.get_user(data)
    elif model_name == 'Discussion':
        return disc_dac.get_discussion(data)
    elif model_name == 'Exam':
        return exams_dac.get_exam(data)
    elif model_name == 'Flashcard_set':
        return fc_dac.get_flashcard_set(data)
    elif model_name == 'Flashcard':
        return fc_dac.get_flashcard(data)
    elif model_name == "Flashcard_pref":
        return fc_dac.get_fcpref(data)
    else:
        return None
