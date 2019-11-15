from flask import Blueprint, jsonify
from flask import abort, request
from app.system import *
from app.dac import *
from flask_login import current_user, logout_user, login_user
from app import app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity
)

mod = Blueprint('grades', __name__, url_prefix='/api')


@mod.route('/view_grade', methods=["POST"])
@jwt_required
@authenticated
def api_view_grade():
    """ End-point for viewing the grade of an exam.
        ---
        description: Viewing grade
        post:
            description: Viewing grade
            requestBody:
                description : Request body
                content:
                    application/json:
                        schema:
                            type: object
                            required:
                                - exam_id
                            properties:
                                exam_id:
                                    type: integer
                                    description: ID of the exam whose grade you want to see
                                    example: 1
                                stud_id:
                                    type: integer
                                    description: ID of the student whose grade you want to see
                                    example: 434
                                    required: false
            responses:
                200:
                    description: Successful display
                    content:
                        application/json:
                            schema:
                                type: object
                                properties:
                                    Status:
                                        type: string
                                        example: 200
                                    message:
                                        type: integer
                                        example: Grade displayed successfully
                                    grade:
                                        type: string
                                        example: 100.0
                                    exam_name:
                                        type: string
                                        example: Midterm
                400:
                    description: Bad Request
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
                                        example: Unauthorized request
        """

    data = request.get_json()
    exam_id = data[EXAM_ID]
    # print(is_User("Student"), current_user.UserRole.User_Type)
    if is_User("Student") == 200:
        stud_id = current_user.User_ID
    else:
        try:
            stud_id = data[STUDENT_ID]
        except:
            res = ErrorResponse(400)
            return res.content(), 400

    # check if that exam exists
    exam = get_exam(exam_id)
    if not exam:
        return ErrorResponse(400).content(), 400

    # check if the student has submitted that exam
    if not check_sub_exam(exam_id, stud_id):
        return ErrorResponse(400).content(), 400

    report = get_report(stud_id, exam_id)

    # report cannot be null at this point
    res = Response(
        200,
        "Grade displayed successfully"
    ).content()

    res[GRADE] = report.Grade
    res[EXAM_NAME] = exam.Exam_Name
    return res, 200


@mod.route('/view_grades', methods=["POST"])
@jwt_required
@authenticated
def api_view_grades():
    """ End-point for viewing the grade of an exam.
            ---
            description: Viewing all grades
            post:
                description: Viewing grades
                requestBody:
                    description : Request body
                    content:
                        application/json:
                            schema:
                                type: object
                                properties:
                                    mod_id:
                                        type: integer
                                        description: ID of the module, the grades of whose exam you want to see
                                        example: 1
                                        required: false
                                    stud_id:
                                        type: integer
                                        description: ID of the student whose grade you want to see. You'll need to enter it if you are not a student.
                                        example: 434
                                        required: false
                responses:
                    200:
                        description: Successful display
                        content:
                            application/json:
                                schema:
                                    type: object
                                    properties:
                                        Status:
                                            type: string
                                            example: 200
                                        message:
                                            type: integer
                                            example: Grade displayed successfully
                                        exams:
                                            type: array
                                            items:
                                                type: object
                                                properties:
                                                    exam_id:
                                                        type: integer
                                                        example: 3
                                                    exam_name:
                                                        type: string
                                                        example: Sample
                                                    grade:
                                                        type: string
                                                        example: 45.5
                                                    mod_id:
                                                        type: integer
                                                        example: 4
                    400:
                        description: Bad Request
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
                                            example: Unauthorized request
            """

    data = request.get_json()
    module_id = data.get(MODULE_ID)
    # print(is_User("Student"), current_user.UserRole.User_Type)
    if is_User("Student") == 200:
        stud_id = current_user.User_ID
    else:
        try:
            stud_id = data[STUDENT_ID]
        except:
            res = ErrorResponse(400)
            return res.content(), 400

    if module_id:
        exams = get_exams(module_id)
    else:
        exams = get_exams()

    exam_list = []
    for exam in exams:
        exam_id = exam.Exam_ID
        if not check_sub_exam(exam_id, stud_id):
            continue

        report = get_report(stud_id, exam_id)
        t_report = {
            EXAM_ID: exam_id,
            EXAM_NAME: exam.Exam_Name,
            GRADE: report.Grade,
            MODULE_ID: exam.Module_ID
        }

        exam_list.append(t_report)

    res = Response(
        200,
        "Grades displayed successfully"
    ).content()

    res["exams"] = exam_list

    return res, 200
