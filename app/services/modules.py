from flask import Blueprint, jsonify
from flask import abort, request
from app.system import *

from app.dac import modules as mod_dac

from app.dac import general as gen_dac
from app.constants import *
from flask_login import current_user, logout_user, login_user
from app import app
from flask_jwt_extended import (
    jwt_required
)

mod = Blueprint('modules', __name__, url_prefix='/api')


@mod.route('/add_module', methods=['POST'])
@jwt_required
@is_admin  # checks authentication automatically
def api_add_module():
    """ End-point for adding new modules.
            ---
            description: Add module
            post:
                description: Adding a new module
                requestBody:
                    description : Request body
                    content:
                        application/json:
                            schema:
                                type: object
                                required:
                                    - mod_name
                                properties:
                                    mod_name:
                                        type: string
                                        description: The name of the module that needs to be added
                                        example: maths
                responses:
                    200:
                        description: Successful creation of a new module
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
                                            example: Module added in successfully
                    401:
                        description: Bad request
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
                                            example: Only an admin is allowed to add modules.
            """

    data = request.get_json()
    if data is None:
        abort(404)

    try:
        module = mod_dac.create_module(data)
        res = Response(
            200,
            "Module added successfully"
        )

        res = gen_dac.exists('Module', module, res)

        return res.content(), res.code

    except Exception as e:
        # print(e)
        res = ErrorResponse(400)
        return res.content(), 400


@mod.route('/get_modules', methods=["GET", "POST"])
@jwt_required
@is_admin_student
def api_get_mods():
    """ End-point for adding listing modules.
            ---
            description: Get modules
            get:
                description: Getting list of modules
                responses:
                    200:
                        description: Successfully fetched modules
                        content:
                            application/json:
                                schema:
                                    type: object
                                    properties:
                                        Status:
                                            type: integer
                                            example: 200
                                        message:
                                            type: string
                                            example: Sucessfully fetched all the modules
                                        mod_list:
                                            type: array
                                            items:
                                                type: object
                                                properties:
                                                    mod_id:
                                                        type: integer
                                                        description : Module id
                                                        example: 34
                                                    mod_name:
                                                        type: string
                                                        description: the name of the Module
                                                        example: Maths
                                                    progress:
                                                        type: flaot
                                                        description: The progress of the student in the module
                                                        example: 20.0
                    400:
                        description: Bad request
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
                                            example: Bad request
                    401:
                        description: Unauthorized request
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
                                            example: Only admins and students are allowed to make this request.
            post:
                description: Getting list of modules
                requestBody:
                    description : Request body
                    content:
                        application/json:
                            schema:
                                type: object
                                properties:
                                    stud_id:
                                        type: integer
                                        description: The id of the student whose modules you want to see
                                        example: 34
                responses:
                    200:
                        description: Successfully fetched modules
                        content:
                            application/json:
                                schema:
                                    type: object
                                    properties:
                                        Status:
                                            type: integer
                                            example: 200
                                        message:
                                            type: string
                                            example: Sucessfully fetched all the modules
                                        mod_list:
                                            type: array
                                            description: Won't see progress unless stud_id is provided
                                            items:
                                                type: object
                                                properties:
                                                    mod_id:
                                                        type: integer
                                                        description : Module id
                                                        example: 34
                                                    mod_name:
                                                        type: string
                                                        description: the name of the Module
                                                        example: Maths
                                                    progress:
                                                        type: flaot
                                                        description: The progress of the student in the module
                                                        example: 20.0
                    400:
                        description: Bad request
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
                                            example: Bad request
                    401:
                        description: Unauthorized request
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
                                            example: Only admins and students are allowed to make this request.
            """

    data = request.get_json()
    is_POST = request.method == "POST"
    empty = not (STUDENT_ID in data)

    # Admin cannot make a GET request
    if not is_POST and is_User("Student") != 200:
        return ErrorResponse(400).content(), 400

    # User cannot make a POST request
    if is_POST and is_User("Student") == 200:
        return ErrorResponse(400).content(), 400

    if is_POST and not empty:
        stud_id = data[STUDENT_ID]
    else:
        stud_id = current_user.User_ID

    modules = mod_dac.get_modules()
    if not modules:
        return Response(404, "No modules found").content(404)

    mod_list = []
    for module in modules:
        temp = {
            MODULE_ID: module.Module_ID,
            MODULE_NAME: module.Module_Name
        }
        if (not is_POST) or (is_POST and not empty):
            prog = gen_dac.get_progress(module, stud_id)
            temp[PROGRESS] = prog

        mod_list.append(temp)

    res = Response(
        200,
        "Modules fetched successfully."
    ).content()

    res[MODULE_LIST] = mod_list
    return res, 200
