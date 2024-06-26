from flask import Blueprint, jsonify
from flask import abort, request
from flask_cors import cross_origin
from app.system import *
import gcloud
from app.dac import general as gen
from app.constants import *
from app import storage
from app.dac import files as files_dac

from flask_jwt_extended import (
    jwt_required
)

mod = Blueprint('admin', __name__, url_prefix='/api')


@mod.route('/delete', methods=['POST'])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@is_admin_tutor  # Checks authentication automatically
def api_del():
    """
    API Endpoint function that handles all the delete requests from the client side.
    :return: Json response object
    """
    data = request.get_json()
    model_id = data[MODEL_ID]
    model_name = data[MODEL_NAME]

    if is_User("Tutor") == 200 and not (model_name == "Exam" or model_name == "Discussion" or model_name == "File"):
        return Response(
            401,
            "Only an admin can delete this").content(), 401

    field = gen.get_model_field(model_name, model_id)
    if not field:
        return ErrorResponse(404).content(), 404

    deleted = gen.delete(field)
    if not deleted:
        return ErrorResponse(500).content(), 500

    if model_name == "File":
        mod_id = field.Module_ID
        folder = get_folder(mod_id)
        file_path = "{}/{}".format(folder, field.File_Name)
        try:
            storage.delete(file_path)
        except gcloud.exceptions.NotFound:
            return ErrorResponse(404).content(), 404

    return Response(
        200,
        "Successfully deleted."
    ).content(), 200
