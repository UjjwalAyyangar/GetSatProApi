from flask import Blueprint, send_from_directory

from werkzeug.utils import secure_filename
from flask import request
from app.system import *
from app import app
import os

from app.dac import discussions as disc_dac
from app.dac import general as gen_dac
from app.dac import modules as mod_dac

from app.constants import *

from flask_login import current_user
from flask_jwt_extended import (
    jwt_required
)
from flask_cors import cross_origin

"""
files_ref = firebase_db.collection('files')

mod = Blueprint('files', __name__, url_prefix='/api')
@mod.route('/add_files', methods=["POST"])
def upload():
    data = request.get_json()
    path = data[FILE_PATH]
    secure_path = '/bucketname/' + secure_filename(path)
    try:
        bucket = stor

"""

mod = Blueprint('files', __name__, url_prefix='/api')


@mod.route('/add_file', methods=["GET", "POST"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
# @jwt_required
# @authenticated
def upload_file():
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

    if 'file' not in request.files:
        return Response(
            "Please specify a file to be uploaded",
            400
        ).content(), 400
    file = request.files['file']

    print("file is", file.filename)
    if file.filename == '':
        return Response(
            "The file has no name.",
            400
        ).content(), 400

    if file and is_acceptable_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        return Response(
            "File uploaded successfully",
            200
        ).content(), 200


@mod.route('/get_file/<filename>')
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
# @jwt_required
# @authenticated
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
