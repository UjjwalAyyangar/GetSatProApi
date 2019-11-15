from flask import Blueprint
from flask import request
from app.system import *

import app.dac.discussions as disc_dac
import app.dac.general as gen_dac

from app.constants import *

from flask_login import current_user
from flask_jwt_extended import (
    jwt_required
)

mod = Blueprint('discussions', __name__, url_prefix='/api')


@mod.route('/create_discussion', methods=["POST"])
@jwt_required
@authenticated
def api_create_discussion():
    """ End-point for creating a new discussion
                ---
                description: Create Discussion
                post:
                    description: Create Discussion
                    requestBody:
                        description : Request body
                        content:
                            application/json:
                                schema:
                                    type: object
                                    required:
                                        - title
                                        - content
                                        - mod_id
                                    properties:
                                        title:
                                            type: string
                                            description: Title of the main discussion
                                            example: Doubt in Algebra
                                        content:
                                            type: string
                                            description: Content of the main discussion
                                            example: How to derive (x+y)^2 ?
                                        mod_id:
                                            type: integer
                                            description: ID of the module where the discussion has to be created
                                            example: 3
                    responses:
                        200:
                            description: Successfully created a new discussion
                            content:
                                application/json:
                                    schema:
                                        type: object
                                        properties:
                                            Status:
                                                type: string
                                                example: 200
                                            message:
                                                type: string
                                                example: New discussion created successfully
                        401:
                            description: Need to be logged in to make this request
                            content:
                                application/json:
                                    schema:
                                        type: object
                                        properties:
                                            Status:
                                                type: string
                                                example: 401
                                            message:
                                                type: string
                                                example: Unauthorized request.
                        400:
                            content:
                                application/json:
                                    schema:
                                        type: object
                                        properties:
                                            Status:
                                                type: string
                                                example: 400
                                            message:
                                                type: string
                                                example: Bad Request
                """

    data = request.get_json()
    data[USER_ID] = current_user.User_ID

    new_discus = disc_dac.create_discussion(data)

    try:
        res = Response(
            200,
            "Discussion created successfully"
        )

        res = gen_dac.exists('Discussion', new_discus, res)

        return res.content(), 200
    except:
        res = ErrorResponse(400)
        return res.content(), 400


@mod.route('/create_discus_thread', methods=["POST"])
@jwt_required
@authenticated
def api_create_discus_thread():
    """ End-point for creating a new discussion reply
                    ---
                    description: Create Reply/Thread
                    post:
                        description: Create Reply/Thread
                        requestBody:
                            description : Request body
                            content:
                                application/json:
                                    schema:
                                        type: object
                                        required:
                                            - discuss_id
                                            - content
                                        properties:
                                            discuss_id:
                                                type: integer
                                                description: ID of the discussion where you want to reply
                                                example: 3
                                            content:
                                                type: string
                                                description: Content of the reply
                                                example: Make a square and divide it.
                        responses:
                            200:
                                description: Successfully replied to the discussion
                                content:
                                    application/json:
                                        schema:
                                            type: object
                                            properties:
                                                Status:
                                                    type: string
                                                    example: 200
                                                message:
                                                    type: string
                                                    example: New discussion reply created.
                            401:
                                description: Need to be logged in to make this request
                                content:
                                    application/json:
                                        schema:
                                            type: object
                                            properties:
                                                Status:
                                                    type: string
                                                    example: 401
                                                message:
                                                    type: string
                                                    example: Unauthorized request.
                            400:
                                content:
                                    application/json:
                                        schema:
                                            type: object
                                            properties:
                                                Status:
                                                    type: string
                                                    example: 400
                                                message:
                                                    type: string
                                                    example: Bad Request
                            404:
                                description: The main discussion associated with the given discuss_id was not found
                                content:
                                    application/json:
                                        schema:
                                            type: object
                                            properties:
                                                Status:
                                                    type: string
                                                    example: 404
                                                message:
                                                    type: string
                                                    example: Not found.
                    """
    data = request.get_json()
    data["user_id"] = current_user.User_ID

    if not disc_dac.disc_exists(data[DISCUSS_ID]):
        return ErrorResponse(404).content(), 404

    new_dthread = disc_dac.create_discus_thread(data)
    try:
        res = Response(
            200,
            "Discussion thread created successfully"
        )

        res = gen_dac.exists('Discussion', new_dthread, res)

        return res.content(), res.code
    except:
        return ErrorResponse(400).content(), 400


@mod.route('/view_discussion')
@jwt_required
@authenticated
def api_view_discussion():
    data = request.get_json()
    discuss = disc_dac.get_discussion(data)

    if discuss:
        reply_list = []
        replies = discuss.Replies.all()

        for reply in replies:
            temp = {
                "thread_id": reply.Thread_ID,
                "content": reply.Message,
            }
            reply_list.append(temp)

        res = Response(
            200,
            "Fetched discussion successfully"
        )
        ret = res.content()
        ret["replies"] = reply_list
        ret["discuss_id"] = data["discuss_id"]

        return ret, 200
    else:
        res = ErrorResponse(400)
        return res.content(), 400
