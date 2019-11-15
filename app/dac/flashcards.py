# The data access layer

# Some of these methods could have been written in models
# but I wanted these separate. For better code organization.
from app.models import *
from app import db, flask_bcrypt
import sqlalchemy
from flask_login import current_user
from app.constants import *
import app.dac.general as gen_dac


def get_flashcard_set(data):
    try:
        return FlashcardSet.query.filter_by(
            Set_ID=data[FLASHCARD_SET_ID]
        ).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def get_flashcard(data):
    try:
        return Flashcard.query.filter_by(
            FC_ID=data[FLASHCARD_ID]
        ).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def get_fcpref(data):
    try:
        return FC_Preference.query.filter_by(
            Student_ID=data[STUDENT_ID],
            FC_ID=data[FLASHCARD_ID],
        ).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None
