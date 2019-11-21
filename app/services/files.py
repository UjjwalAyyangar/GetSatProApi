from flask import Blueprint
from app import firebase_app, firebase_db
from google.cloud import storage
from werkzeug.utils import secure_filename
from firebase_admin import credentials, firestore, initialize_app
from flask import request
from app.system import *

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