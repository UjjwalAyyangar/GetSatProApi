from flask import Blueprint

from werkzeug.utils import secure_filename
from flask import request
from app.system import *
from app import storage
import os

from app.dac import files as files_dac
from app.dac import modules as mod_dac

from app.constants import *

from flask_login import current_user
from flask_jwt_extended import (
    jwt_required
)
from flask_cors import cross_origin

mod = Blueprint('files', __name__, url_prefix='/api')


@mod.route('/add_file/', methods=["GET", "POST"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
# @jwt_required
# @is_admin_tutor
def add_file():
    if request.method == "GET":
        return '''
                <!doctype html>
                <title>Upload new File</title>
                <h1>Upload new File</h1>
                <form method=post enctype=multipart/form-data>
                  <input type=file name=file>
                  <input type=submit value=Upload>
                </form>
                '''

    if is_User("Admin") == 200:
        if MODULE_ID in request.form:
            mod_id = request.form['mod_id']
        else:
            return ErrorResponse(400).content(), 400
    else:
        mod_id = 2
        # mod_id = mod_dac.get_tutor_module(current_user.User_ID).Module_ID

    mod_id = 2
    if 'file' not in request.files:
        return Response(
            "Please specify a file to be uploaded",
            400
        ).content(), 400

    file = request.files['file']

    if file.filename == '':
        return Response(
            "The file has no name",
            400
        ).content(), 400

    if file and is_acceptable_file(file.filename):
        filename = secure_filename(file.filename)

        data = {
            FILE_NAME: filename,
            PUB_ID: 4,  # ,current_user.User_ID,
            MODULE_ID: mod_id
        }
        folder = get_folder(mod_id)

        new_file_path = os.path.join(folder, filename)
        new_file_path = new_file_path.replace(os.sep, '/')

        storage.child(new_file_path).put(file)
        data[FILE_LINK] = storage.child(new_file_path).get_url(None)
        # new_file = files_dac.create_file(data)

        # if not new_file:
        #    return ErrorResponse(500).content(), 500

        ret = Response(
            "File uploaded successfully",
            200
        ).content()
        # ret[FILE_ID] = new_file.File_ID
        return ret, 200
    else:
        return ErrorResponse(404).content(), 404


@mod.route('/get_files', methods=["GET", "POST"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@is_admin_tutor
def get_files():
    is_POST = request.method == "POST"
    all_modules = False
    if is_POST:
        if is_User("Tutor") == 200:
            return Response(401, "Tutors cannot make POST request on this endpoint").content(), 401
        data = request.get_json()
        if MODULE_ID not in data:
            return ErrorResponse(400).content()
        else:
            mod_id = data[MODULE_ID]
    else:
        if is_User("Admin") == 200:
            all_modules = True

    if all_modules:
        modules = mod_dac.get_modules()
        mod_lis = []
        for module in modules:
            temp_mod = {
                MODULE_ID: module.Module_ID,
                MODULE_NAME: module.Module_Name
            }
            files = module.Files
            file_lis = []
            for file in files:
                temp = {
                    FILE_NAME: file.File_Name,
                    PUB_ID: file.Publisher_ID,
                    MODULE_ID: file.Module_ID,
                    FILE_LINK: file.Link,
                    FILE_ID: file.File_ID
                }

                file_lis.append(temp)

            temp_mod[FILE_LIST] = file_lis
            mod_lis.append(temp_mod)

        res = Response(200, "Successfully fetched all the files").content()
        res[MODULE_LIST] = mod_lis
        return res, 200
    else:
        if is_User("Tutor") == 200:
            mod_id = mod_dac.get_tutor_module(current_user.User_ID).Module_ID

        files = files_dac.get_files({
            MODULE_ID: mod_id
        })

        file_lis = []
        for file in files:
            temp = {
                FILE_NAME: file.File_Name,
                PUB_ID: file.Publisher_ID,
                MODULE_ID: file.Module_ID,
                FILE_LINK: file.Link,
                FILE_ID: file.File_ID
            }

            file_lis.append(temp)

        res = Response(200, "Successfully fetched all the files").content()
        res[FILE_LIST] = file_lis
        return res, 200


@mod.route('/get_file/<int:file_id>', methods=["GET"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@is_admin_tutor
def get_file(file_id):
    file = files_dac.get_file(file_id)
    if not file:
        return ErrorResponse(404).content(), 404

    if is_User("Tutor") == 200:
        mod_id = mod_dac.get_tutor_module(current_user.User_ID).Module_ID
        if file.Module_ID != mod_id:
            return Response(401, "Only admins can access file of different modules").content()

    res = Response(200).content()
    res[FILE_NAME] = file.File_Name
    res[FILE_LINK] = file.Link
    res[FILE_ID] = file.File_ID
    res[PUB_ID] = file.Publisher_ID
    res[PUBLISHED] = file.Time
    res[MODULE_ID] = file.Module_ID

    return res, 200
