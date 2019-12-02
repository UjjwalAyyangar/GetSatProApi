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

from flask_cors import cross_origin

mod = Blueprint('modules', __name__, url_prefix='/api')


@mod.route('/add_module', methods=['POST'])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@is_admin  # checks authentication automatically
def api_add_module():
    """ API endpoint which is used to add a new module to the system

    :return: JSON response indicated whether a new module was added successfully or not.
    """

    data = request.get_json()
    if data is None:
        abort(404)

    # returning apt. response to the client
    try:
        module = mod_dac.create_module(data)
        res = Response(
            200,
            "Module added successfully"
        )

        # checking if the module exists already
        res = gen_dac.exists('Module', module, res)
        return res.content(), res.code

    except Exception as e:
        res = ErrorResponse(400)
        return res.content(), 400


@mod.route('/get_modules', methods=["GET", "POST"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@is_admin_student
def api_get_mods():
    """ API endpoint for getting a list of modules available in the system

    :return: response JSON containing details about the list of modules
    """

    # checking the client request method type
    is_Post = request.method == "POST"
    student = is_User("Student") == 200
    admin = is_User("Admin") == 200
    prog = False  # becomes true if the user is a student

    if is_Post:
        data = request.get_json()
        if student:
            return ErrorResponse(400).content(), 400

        if not STUDENT_ID in data:
            return ErrorResponse(400).content(), 400

        stud_id = data[STUDENT_ID]
        prog = True

    if student:
        stud_id = current_user.User_ID
        prog = True

    # fetching all the modules from the database
    modules = mod_dac.get_modules()
    if not modules:
        return Response(404, "No modules found").content(404), 404

    mod_list = []
    for module in modules:
        # constructing json response for each module
        temp = {
            MODULE_ID: module.Module_ID,
            MODULE_NAME: module.Module_Name
        }
        if prog:
            # getting a student's progress from a  module and adding it to response
            progress = gen_dac.get_progress(module, stud_id)
            temp[PROGRESS] = progress

        mod_list.append(temp)

    res = Response(
        200,
        "Modules fetched successfully."
    ).content()

    res[MODULE_LIST] = mod_list
    # returning the final json response object to the client
    return res, 200
