from flask import Blueprint, jsonify
from flask import request
from app.system import *
from app.constants import *

from app.dac import exams as exam_dac

from app.dac import grades as grade_dac

from flask_login import current_user, logout_user, login_user
from app import app
from flask_jwt_extended import (
    jwt_required
)
from flask_cors import cross_origin

mod = Blueprint('grades', __name__, url_prefix='/api')


@mod.route('/view_grade', methods=["POST"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@authenticated
def api_view_grade():
    """ API endpoint to view grades

    :return: JSON response object containing the details of an exam's grade
    """

    data = request.get_json()
    exam_id = data[EXAM_ID]

    if is_User("Student") == 200:
        stud_id = current_user.User_ID
    else:
        try:
            stud_id = data[STUDENT_ID]
        except:
            res = ErrorResponse(400)
            return res.content(), 400

    # check if that exam exists
    exam = exam_dac.get_exam(exam_id)
    if not exam:
        return ErrorResponse(400).content(), 400

    # check if the student has submitted that exam
    if not exam_dac.check_sub_exam(exam_id, stud_id):
        return ErrorResponse(400).content(), 400

    report = grade_dac.get_report(stud_id, exam_id)

    # report cannot be null at this point
    res = Response(
        200,
        "Grade displayed successfully"
    ).content()

    res[GRADE] = report.Grade
    res[EXAM_NAME] = exam.Exam_Name
    return res, 200


@mod.route('/view_grades', methods=["POST"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@authenticated
def api_view_grades():
    """ API endpoint for getting the grades of a student in a module/ whole system

    :return: response JSON containing details about the grades of a student.
    """

    data = request.get_json()

    module_id = data.get(MODULE_ID)

    if is_User("Student") == 200:
        stud_id = current_user.User_ID
    else:
        try:
            stud_id = data[STUDENT_ID]
        except:
            res = ErrorResponse(400)
            return res.content(), 400

    # checking if module id is specified by the client in the request object
    if module_id:
        # fetching exams from the db of the specified module
        exams = exam_dac.get_exams(module_id)
    else:
        # fetching all exams from the db
        exams = exam_dac.get_exams()

    exam_list = []
    for exam in exams:
        exam_id = exam.Exam_ID
        if not exam_dac.check_sub_exam(exam_id, stud_id):
            continue

        # getting a student's report in an exam
        report = grade_dac.get_report(stud_id, exam_id)
        # constructing response report json
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

    # returning constructed json response to the client
    return res, 200
