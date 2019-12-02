from flask import Blueprint, jsonify
from flask import abort, request
from app.system import *
from app.constants import *
from app.dac import exams as exams_dac
from app.dac import grades as grades_dac
from app.dac import general as gen_dac
from app.dac import modules as mod_dac
from flask_cors import cross_origin

from flask_login import current_user, logout_user, login_user
from app import app
from flask_jwt_extended import (
    jwt_required
)

mod = Blueprint('exams', __name__, url_prefix='/api')


@mod.route('/view_exam', methods=["POST"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@authenticated
def api_view_exam():
    """ API endpoint for viewing  an exam

    :return: A response JSON object containing details about an exam
    """

    # getting data from a client's request json object
    data = request.get_json()
    exam_id = data[EXAM_ID]

    # getting the associated exam from the database
    exam = exams_dac.get_exam(exam_id)

    # checking if the exam exists or not and sending appropriate response to the client
    if not exam:
        return ErrorResponse(404).content(), 404

    # getting all the questions of the specified exam
    questions = exam.Questions.all()
    ques_list = []

    # Checking if the current user is a student and if he/she has submitted the exam
    isStudent = is_User("Student") == 200
    if isStudent:
        submitted = exams_dac.check_sub_exam(exam_id, current_user.User_ID)
    else:
        submitted = False

    # if the student has submitted, get his/her answer sheets
    if submitted:
        user_sheet = exams_dac.get_ans_sheet({
            EXAM_ID: exam_id,
            STUDENT_ID: current_user.User_ID
        })

        answers = user_sheet.Answers

    total = 0
    correct = 0

    # building response json for each question and adding them into a list
    for question in questions:
        total += 1
        options = [question.Option_1, question.Option_2, question.Option_3, question.Option_4]
        options = parse_options(options)
        correct_answer = question.Correct_ans
        temp = {
            QUESTION_ID: question.Question_ID,
            QUESTION: question.Question,
            QUESTION_OPTIONS: options,
        }

        if submitted:
            user_answer = answers.filter_by(Question_ID=question.Question_ID).one().Ans
            temp[QUESTION_ANS] = correct_answer
            temp[USER_ANSWER] = user_answer

            if user_answer == correct_answer:
                temp[QUESTION_STATUS] = "Correct"
                correct += 1
            else:
                temp[QUESTION_STATUS] = "Incorrect"
        else:
            if not isStudent:
                temp[QUESTION_ANS] = correct_answer

        ques_list.append(temp)

    res = Response(200, "Successfully fetched Questions").content()
    if submitted:
        res[GRADE] = (float(correct) / float(total)) * 100

    res[QUESTIONS] = ques_list
    res[EXAM_NAME] = exam.Exam_Name

    # returning the final json object
    return res, 200


@mod.route('/get_exams', methods=["GET", "POST"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@authenticated
def api_get_exams():
    """ API endpoint for getting the list of exams

    :return: A JSON response object containing a list of exams with their details
    """

    # POST - module_id - for students
    # GET - for tutor and students

    stud_id, tut_id, mod_id = (None, None, None)

    # checking if the client has made a POST request or GET request
    is_POST = request.method == "POST"
    if is_POST:
        data = request.get_json()

    # Setting the value of mod_id variable depending on the type of request made by the client
    if is_User('Tutor') == 200:
        if is_POST:
            return ErrorResponse(400).content(), 400

        tut_id = current_user.User_ID
        mod_id = mod_dac.get_tutor_module(tut_id).Module_ID
    else:
        stud_id = current_user.User_ID
        if is_POST:
            if MODULE_ID in data:
                mod_id = data[MODULE_ID]

    # getting a list of exams from the database
    if mod_id:
        Exams = exams_dac.get_exams(mod_id)
    else:
        Exams = exams_dac.get_exams()

    exam_list = []
    if not Exams:
        return ErrorResponse(404).content(), 404

    # constructing response JSON for each exam
    for exam in Exams:
        question_no = len(exam.Questions.all())
        date = exam.Published.date()

        # separating data objects into correct format
        day = date.day
        month = date.month
        year = date.year
        date_str = "{}/{}/{}".format(month, day, year)

        temp = {
            EXAM_ID: exam.Exam_ID,
            EXAM_NAME: exam.Exam_Name,
            QUESTION_NO: question_no,
            PUBLISHED: date_str,
        }

        # checking if the user is a student or not
        if stud_id:
            # checking if the student has already submitted this exam
            completed = exams_dac.check_sub_exam(exam.Exam_ID, stud_id)
            temp[COMPLETED] = completed

        if not mod_id:
            temp[MODULE_ID] = exam.Module_ID

        exam_list.append(temp)

    # creating a response json object
    res = Response(
        200,
        "Fetched exams successfully"
    )

    ret = res.content()
    ret["exams"] = exam_list
    if mod_id:
        ret[MODULE_ID] = mod_id

    # returning the final response json object
    return ret, 200


@mod.route('/submit_exam', methods=["POST"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@is_student  # Ensures that only a use of type "Student" can use this endpoint
def api_submit_exam():
    """ API endpoint for submitting exams

    :return: A JSON response object containing details of the currently submitted exam
    """

    data = request.get_json()
    student_id = current_user.User_ID

    # check if the exam already exists or not
    exam_id = data[EXAM_ID]
    exam = exams_dac.get_exam(exam_id)
    if not exam:
        return Response(
            404,
            "Exam does not exist"
        ).content(), 404

    # check if the user has already submitted this exam or not
    if exams_dac.check_sub_exam(exam_id):
        return Response(
            200,
            "Exam already submitted"
        ).content(), 200

    # if the user has not submitted, make new submission
    sub = data[ANSWERS]

    # get grades
    grade = auto_grade(exam, sub)

    # create a new sheet
    new_ans_sheet = exams_dac.create_ans_sheet({
        STUDENT_ID: student_id,
        EXAM_ID: exam_id
    })

    # sheet creation check
    if not new_ans_sheet:
        return Response(
            500,
            "Unable to create new answer sheet"
        ).content(), 500

    for ans in sub:
        new_ans = exams_dac.create_ans({
            STUDENT_ID: student_id,
            QUESTION_ID: ans[QUESTION_ID],
            ANSWER: ans[ANSWER]
        }, sheet=new_ans_sheet)

        # ans creation check
        if not new_ans:
            return Response(
                500,
                "Unable to create new answers"
            ).content(), 500

    # creating student's answer report
    new_report = grades_dac.create_report({
        STUDENT_ID: student_id,
        EXAM_ID: exam_id,
        SHEET_ID: new_ans_sheet.Sheet_ID,
        GRADE: grade
    })

    # report creation check
    if not new_report:
        return Response(
            500,
            "Unable to create new report"
        ).content(), 500

    # returning the response json object
    return Response(
        200,
        "Exam submitted successfully"
    ).content(), 200


@mod.route('/create_exam', methods=["POST"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@is_admin_tutor  # checks for authentication also
def api_create_exam():
    """ API endpoint for creating exams

    :return: A JSON response object that tells if exam creation was successful or not.
    """
    # mod_id for admin

    # getting data from request data object sent by the client
    data = request.get_json()

    user_id = current_user.User_ID

    # checking if the user is tutor, because in that case a module_id is not required
    if is_User("Tutor") == 200:
        # getting module id of the tutor from tutor_module table
        mod_id = mod_dac.get_tutor_module(user_id)
        if not mod_id:
            return ErrorResponse(404).content(), 404

        mod_id = mod_id.Module_ID
        data[MODULE_ID] = mod_id

    # creating a new exam
    exam = exams_dac.create_exam(data)
    if not exam:
        return ErrorResponse(500).content(), 500

    res = Response(
        200,
        "Exam was created successfully"
    )
    res = gen_dac.exists('Exam', exam, res)
    res = res.content()
    res[EXAM_ID] = exam.Exam_ID

    # returning the JSON response to client
    return res, 200


@mod.route('/check_sub', methods=["POST"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@authenticated
def api_check_sub():
    """ API endpoint for checking if an exam is submitted or not

    :return: A JSON response object containing details about an exam's submission
    """

    data = request.get_json()
    stud_id = data.get(STUDENT_ID)
    if not stud_id:
        stud_id = current_user.User_ID

    # fetching exam from the database
    exam = exams_dac.get_exam(data[EXAM_ID])
    if not exam:
        return Response(
            400,
            "Exam does not exists"
        ).content(), 400
    res = Response(200, "").content()

    # checking if the exam is submitted, and constructing apt. json response
    if exams_dac.check_sub_exam(data[EXAM_ID], stud_id):
        res["message"] = "Fetched exam successfully"
        res["submitted"] = "True"
    else:
        res["message"] = "Exam not submitted"
        res["submitted"] = "False"

    # returning the response json
    return res, 200
