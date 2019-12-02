from flask import Blueprint
from flask import request
from app.system import *

from app.dac import discussions as disc_dac
from app.dac import general as gen_dac
from app.dac import modules as mod_dac
from app.dac import users as users_dac

from app.constants import *

from flask_login import current_user
from flask_jwt_extended import (
    jwt_required
)
from flask_cors import cross_origin

mod = Blueprint('discussions', __name__, url_prefix='/api')


@mod.route('/create_discussion', methods=["POST"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@authenticated
def api_create_discussion():
    """
    API endpoint for creating a discussion

    :return: Json response object
    """

    # getting the request json data sent by the client
    data = request.get_json()

    # checking if the user is a tutor, because tutor's don't need to provide module ids
    if is_User("Tutor") == 200:
        mod_id = mod_dac.get_tutor_module(current_user.User_ID).Module_ID
        data[MODULE_ID] = mod_id

    # getting user id from the current user session
    data[USER_ID] = current_user.User_ID

    new_discus = disc_dac.create_discussion(data)

    try:
        # creating a response object
        res = Response(
            200,
            "Discussion created successfully"
        )

        # checking if the newly created discussion already exists and adjusting the response object accordingly
        res = gen_dac.exists('Discussion', new_discus, res)
        ret = res.content()
        ret[DISCUSS_ID] = new_discus.Discussion_ID

        return ret, 200
    except:
        # Return a bad response error
        res = ErrorResponse(400)
        return res.content(), 400


@mod.route('/create_discuss_thread', methods=["POST"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@authenticated
def api_create_discus_thread():
    """
    Api endpoint for creating a discussion thread/reply

    :return: Json response object
    """

    # getting the request json data sent by the client
    data = request.get_json()

    # checking if the user is a tutor, because tutors don't need to provide module ids
    if is_User("Tutor") == 200:
        mod_id = mod_dac.get_tutor_module(current_user.User_ID).Module_ID
        data[MODULE_ID] = mod_id

    # getting current user id from the session
    data["user_id"] = current_user.User_ID

    # checking if the reply already exists or not
    if not disc_dac.disc_exists(data[DISCUSS_ID]):
        return ErrorResponse(404).content(), 404

    # creating a new reply object and updating the DB
    new_dthread = disc_dac.create_discus_thread(data)
    try:
        res = Response(
            200,
            "Discussion thread created successfully"
        )

        res = gen_dac.exists('Discussion', new_dthread, res)

        return res.content(), res.code
    except:
        # returning a bad request error
        return ErrorResponse(400).content(), 400


@mod.route('/view_discussion', methods=["POST"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@authenticated
def api_view_discussion():
    """
    API endpoint for viewing a discussion

    :return: JSON response object
    """

    # getting request json data from the client

    data = request.get_json()

    # getting the discussion object from our Database (ORM)
    discuss = disc_dac.get_discussion(data)

    if discuss:
        reply_list = []
        # getting all the replies associated with the discussion object
        replies = discuss.Replies.all()

        for reply in replies:
            # constructing response json for each reply
            reply_user = users_dac.get_user(user_id=reply.User_ID)
            temp = {
                REPLY_ID: reply.Thread_ID,
                REPLY_CONTENT: reply.Message,
                REPLY_USER_ID: reply.User_ID,
                REPLY_POSTED: reply.Time,
                USER_FNAME: reply_user.First_Name,
                USER_LNAME: reply_user.Last_Name,
                USERNAME: reply_user.Username
            }
            reply_list.append(temp)

        # constructing a response json
        res = Response(
            200,
            "Fetched discussion successfully"
        )
        ret = res.content()
        author = users_dac.get_user(user_id=discuss.User_ID)
        ret["replies"] = reply_list
        ret["discuss_id"] = data["discuss_id"]

        # Adding information about the discussion to the response json
        ret[DISCUSS_CONTENT] = discuss.Main_Discussion
        ret[DISCUSS_TITLE] = discuss.Discussion_Title
        ret[USER_ID] = discuss.User_ID
        ret[MODULE_ID] = discuss.Module_ID
        ret[DISCUSS_POSTED] = discuss.Time
        ret[USERNAME] = author.Username
        ret[USER_FNAME] = author.First_Name
        ret[USER_LNAME] = author.Last_Name

        return ret, 200
    else:
        res = ErrorResponse(400)
        return res.content(), 400


@mod.route('/get_discussions', methods=["GET", "POST"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@authenticated
def get_discussions():
    """
    API endpoint for viewing all the available discussions

    :return: JSON response object
    """

    # checking if the request moethod is POST or GET
    is_POST = request.method == "POST"

    if is_POST:
        # getting request json data from the client
        data = request.get_json()
    else:
        data = {}
    if not is_POST and is_User("Tutor") == 200:
        mod_id = mod_dac.get_tutor_module(current_user.User_ID).Module_ID
        data[MODULE_ID] = mod_id
    elif is_POST and is_User("Tutor") == 200:

        return ErrorResponse(400).content(), 400

    # getting a list of discussions as per the requirements specified by the client in the request json
    discs = disc_dac.get_discussions(data)

    disc_list = []
    for disc in discs:
        # constructing json response structure for each discussion
        temp = {
            DISCUSS_TITLE: disc.Discussion_Title,
            DISCUSS_POSTED: disc.Time,
            DISCUSS_ID: disc.Discussion_ID
        }
        disc_list.append(temp)

    res = Response(200, "Fetched all discussions successfully").content()
    res[DISCUSS_LIST] = disc_list
    return res, 200
