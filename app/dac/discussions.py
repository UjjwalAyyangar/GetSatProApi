# DATA ACCESS LAYER - DISCUSSIONS

from app.models import *
from app import db
import sqlalchemy
from flask_login import current_user
from app.constants import *
from app.dac import modules as mod_dac

from app.dac import general as gen


def get_discussion(data):
    """ Method for querying discussion table and returning the apt. discussion

    :param data: request json data sent by the client
    :return: Discussion model object
    """
    try:
        # Querying Discussion model/table by discussion id and sending it back
        if isinstance(data, dict):
            return Discussion.query.filter_by(
                Discussion_ID=data[DISCUSS_ID]
            ).one()
        elif isinstance(data, int):
            return Discussion.query.filter_by(
                Discussion_ID=data
            ).one()


    except sqlalchemy.orm.exc.NoResultFound:
        # returning none if the discussion was not found in the model/table
        return None


def get_discussions(data):
    """ Method for querying discussion table and returning all the discussions

    :param data: request json data sent by the client
    :return: a list of Discussion model object
    """
    try:
        # querying all the discussions in module and returning them
        module = mod_dac.get_module(data[MODULE_ID])
        return module.Discussions.all()
    except:
        # returning None if the query did not find anything
        return None


def create_discussion(data):
    """ Method for creating a Discussion model object for the Discussion table/model

        :param data: request json data sent by the client
        :return: Discussion model object if new Discussion, None otherwise
    """
    new_discussion = Discussion(
        Discussion_Title=data[DISCUSS_TITLE],
        Main_Discussion=data[DISCUSS_MAIN],
        User_ID=data[USER_ID],
        Module_ID=data[MODULE_ID],
    )

    return gen.insert(new_discussion)


def create_discus_thread(data):
    """ Method for creating a Discussion_Thread model object for the Discussion_Thread table/model

            :param data: request json data sent by the client
            :return: Discussion_Thread model object if new Discussion_Thread, None otherwise
        """
    new_dthread = DiscussionThread(
        User_ID=data[USER_ID],
        Discussion_ID=data[DISCUSS_ID],
        Message=data[DISCUSS_CONTENT],
    )

    return gen.insert(new_dthread)


def disc_exists(discuss_id, user_id=None, mod_id=None):
    """ A method that is used to check if a discussion exists or not

    :param discuss_id: integer: Id of the discussion
    :param user_id: integer:  Id of the author of the discussion
    :param mod_id: integer: Id of the module in which the discussion was created
    :return: True if the discussion exists, False otherwise
    """
    if not user_id and not mod_id:
        return db.session.query(Discussion.Discussion_ID).filter_by(
            Discussion_ID=discuss_id).scalar() is not None
    else:
        return db.session.query(Discussion.Discussion_ID).filter_by(
            User_ID=user_id, Module_ID=mod_id
        ).scalar() is not None
