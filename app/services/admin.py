from flask import Blueprint, jsonify
from flask import abort, request
from app.system import *
import app.dac.general as gen
from app.constants import *

from flask_jwt_extended import (
    jwt_required
)

mod = Blueprint('admin', __name__, url_prefix='/api')


@mod.route('/delete', methods=['POST'])
@jwt_required
@is_admin_tutor  # Checks authentication automatically
def api_del():
    """ End-point for deleting things.
            ---
            description: Deletion
            post:
                description: Deletion
                requestBody:
                    description : Request body
                    required: true
                    content:
                        application/json:
                            schema:
                                type: object
                                required:
                                    - model_name
                                    - model_id
                                properties:
                                    model_name:
                                        type: string
                                        description: required
                                        example: Module (or Exam or User or Discussion or Flashcard)
                                    model_id:
                                        type: integer
                                        example: 234
                responses:
                    200:
                        description: Successfully deleted
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
                                            example: Deleted successfully
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
                                            example: You are not authorized to make this request.
                    500:
                        description: Bad Method
                        content:
                            application/json:
                                schema:
                                    type: object
                                    properties:
                                        Status:
                                            type: string
                                            example: 405
                                        message:
                                            type: string
                                            example: Internal Server Error
            """
    data = request.get_json()
    model_id = data[MODEL_ID]
    model_name = data[MODEL_NAME]

    if model_name != "Exam" and is_User("Tutor") == 200:
        return Response(
            401,
            "Only an admin can delete this").content(), 401

    field = gen.get_model_field(model_name, model_id)
    if not field:
        return ErrorResponse(404).content(), 404

    deleted = gen.delete(field)
    if not deleted:
        return ErrorResponse(500).content(), 500

    return Response(
        200,
        "Successfully deleted."
    ).content(), 200
