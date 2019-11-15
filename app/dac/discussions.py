# The data access layer

# Some of these methods could have been written in models
# but I wanted these separate. For better code organization.
from app.models import *
from app import db
import sqlalchemy
from flask_login import current_user
from app.constants import *

from app.dac import general as gen

def get_discussion(data):
    try:
        return Discussion.query.filter_by(
            Discussion_ID=data[DISCUSS_ID]
        ).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def create_discussion(data):
    new_discussion = Discussion(
        Discussion_Title=data[DISCUSS_TITLE],
        Main_Discussion=data[DISCUSS_MAIN],
        User_ID=data[USER_ID],
        Module_ID=data[MODULE_ID],
    )

    return gen.insert(new_discussion)


def create_discus_thread(data):
    new_dthread = DiscussionThread(
        User_ID=data[USER_ID],
        Discussion_ID=data[DISCUSS_ID],
        Message=data[DISCUSS_CONTENT],
    )

    return gen.insert(new_dthread)


def disc_exists(discuss_id, user_id=None, mod_id=None):
    if not user_id and not mod_id:
        return db.session.query(Discussion.Discussion_ID).filter_by(
            Discussion_ID=discuss_id).scalar() is not None
    else:
        return db.session.query(Discussion.Discussion_ID).filter_by(
            User_ID=user_id, Module_ID=mod_id
        ).scalar() is not None
