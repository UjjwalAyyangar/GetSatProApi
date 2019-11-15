from flask import Blueprint, jsonify
from flask import abort, request
from app.system import *
from app.constants import *
from app.dac import exams as exams_dac
from app.dac import grades as grades_dac
from app.dac import general as gen_dac

from flask_login import current_user, logout_user, login_user
from app import app
from flask_jwt_extended import (
    jwt_required
)

mod = Blueprint('exams', __name__, url_prefix='/api')


@mod.route('/get_exams', methods=["POST"])
@jwt_required
@is_tutor_student
def api_get_exams():
    """ End-point for getting list of Exams.
       ---
       description: List of Exams. [Jwt]
       post:
           description: List of Exams

           requestBody:
               description: List of exams
               content:
                   application/json:
                       schema:
                           type: object
                           properties:
                               mod_id:
                                  type: integer
                                  example: 324
                                  description: OPTIONAL
                               stud_id:
                                  type: integer
                                  example: 34
                                  description: REQUIRED if Tutor is making the request
           responses:
               200:
                   description: Successfully fetched the list of students
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
                                       example: Successfully fetched the list of students
                                   exams:
                                       type: array
                                       description: A list of exams
                                       items:
                                           type: object
                                           description: Exam list
                                           properties:
                                               exam_id:
                                                   type: integer
                                                   example: 1
                                                   description: Id of the exam of the student
                                               exam_name:
                                                   type: string
                                                   example: Sample
                                                   description: The name of the exam
                                               ques_no:
                                                   type: integer
                                                   example: 10
                                                   description: Number of questions in an exam
                                               published:
                                                   type: string
                                                   example: 11/2/2019
                                                   description: The date on which the exam was published
                                               mod_id:
                                                   type: integer
                                                   example: 23
                                                   description: The id of the module to whom the exam belongs.
                                               completed:
                                                   type: boolean
                                                   example: true
               404:
                   description: Exams not found
                   content:
                       application/json:
                           schema:
                               type: object
                               properties:
                                   Status:
                                       type: string
                                       example: 404
                                   message:
                                       type: string
                                       example: Not found
               401:
                   description: Unauthorized request. Cannot be made without login
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
                                       example: Only Tutors and Students can make this request
       """

    data = request.get_json()

    if STUDENT_ID not in data and is_User("Tutor") == 200:
        return ErrorResponse(400).content(), 400

    if STUDENT_ID in data:
        stud_id = data[STUDENT_ID]
    else:
        stud_id = current_user.User_ID

    if MODULE_ID in data:
        mod_id = data[MODULE_ID]
    else:
        mod_id = None

    if mod_id:
        Exams = exams_dac.get_exams(mod_id)
    else:
        Exams = exams_dac.get_exams()

    exam_list = []

    if not Exams:
        return ErrorResponse(404).content(), 404

    for exam in Exams:
        question_no = len(exam.Questions.all())
        date = exam.Published.date()
        day = date.day
        month = date.month
        year = date.year
        completed = exams_dac.check_sub_exam(exam.Exam_ID, stud_id)

        date_str = "{}/{}/{}".format(month, day, year)

        temp = {
            EXAM_ID: exam.Exam_ID,
            EXAM_NAME: exam.Exam_Name,
            QUESTION_NO: question_no,
            PUBLISHED: date_str,
            COMPLETED: completed,

        }

        if not mod_id:
            temp[MODULE_ID] = exam.Module_ID

        exam_list.append(temp)

    res = Response(
        200,
        "Fetched exams successfully"
    )

    ret = res.content()
    ret["exams"] = exam_list
    if mod_id:
        ret[MODULE_ID] = mod_id

    return ret, 200


@mod.route('/submit_exam', methods=["POST"])
@jwt_required
@is_student  # this ensures authentication check
def api_submit_exam():
    """ End-point for submitting exams.
            ---
            description: Exam Submission
            post:
                description: Exam Submission
                requestBody:
                    description : Request body
                    content:
                        application/json:
                            schema:
                                type: object
                                required:
                                    - exam_id
                                    - sub
                                properties:
                                    exam_id:
                                        type: integer
                                        description: ID of the exam which you want to submit
                                        example: 1
                                    sub:
                                        type: array
                                        description: An array of Questions and Answers
                                        items:
                                            type: object
                                            properties:
                                                ques_id:
                                                    type: integer
                                                    description: ID of a question
                                                    example: 1
                                                ans:
                                                    type: integer
                                                    description: The answer option of a question
                                                    example: 1

                responses:
                    200:
                        description: Successful submission
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
                                            example: Exam submitted successfully
                    401:
                        description: Only a student can make this request
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
                                            example: Only a student user can submit an exam.
                    400:
                        description: Already submitted
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
                                            example: The exam is already submitted.
            """

    data = request.get_json()
    student_id = current_user.User_ID

    # check if the exam already exists or not
    exam_id = data["exam_id"]
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
    sub = data["sub"]

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

    return Response(
        200,
        "Exam submitted successfully"
    ).content(), 200


@mod.route('/create_exam', methods=["POST"])
@jwt_required
@is_admin_tutor  # checks for authentication also
def api_create_exam():
    """ End-point for creating exams.
        ---
        description: Exam creation
        post:
            description: Exam creation
            requestBody:
                description : Request body
                content:
                    application/json:
                        schema:
                            type: object
                            required:
                                - mod_id
                                - exam_name
                                - exam
                            properties:
                                mod_id:
                                    type: integer
                                    description: Module ID
                                    example: 1
                                exam_name:
                                    type: string
                                    description: Name of the exam
                                    example: Midterm
                                exam:
                                    type: array
                                    description : An array of questions
                                    items:
                                        type: object
                                        properties:
                                            question:
                                                type: string
                                                description: The question
                                                example : Who is Obi Wan?
                                                required: true
                                            correct_ans:
                                                type: string
                                                description: Correct answer of the question
                                                example: 2
                                            options:
                                                type: array
                                                description: Options of the question
                                                items:
                                                    type: string
                                                example: [A Jedi,A Sith,Ujjwal's student]
            responses:
                200:
                    description: Successful creation of exam
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
                                        example: Exam created successfully
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
                                        example: Only Admins or Tutors can make this request.
        """
    data = request.get_json()

    exam = exams_dac.create_exam(data)
    if not exam:
        return ErrorResponse(500).content(), 500

    res = Response(
        200,
        "Exam was created successfully"
    )
    res = gen_dac.exists('Exam', exam, res)

    return res.content(), res.code


@mod.route('/check_sub', methods=["POST"])
@jwt_required
@authenticated
def api_check_sub():
    """ End-point for checking if an exam has been submitted by the student
            ---
            description: Check exam submission
            post:
                description: Check exam submission
                requestBody:
                    description : Request body
                    content:
                        application/json:
                            schema:
                                type: object
                                required:
                                    - exam_id
                                    - student_id
                                properties:
                                    exam_id:
                                        type: integer
                                        description: ID of the exam whose grade you want to see
                                        example: 1
                                        required: true
                                    student_id:
                                        type: integer
                                        description: ID of the student whose submission you want to check
                                        example: 45
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
                                            example: Fetched exam successfully or Exam not submitted
                                        submitted:
                                            type: string
                                            example: True or False

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
    stud_id = data.get(STUDENT_ID)
    if not stud_id:
        stud_id = current_user.User_ID

    exam = exams_dac.get_exam(data[EXAM_ID])
    if not exam:
        return Response(
            400,
            "Exam does not exists"
        ).content(), 400
    res = Response(200, "").content()
    if exams_dac.check_sub_exam(data[EXAM_ID], stud_id):
        res["message"] = "Fetched exam successfully"
        res["submitted"] = "True"
    else:
        res["message"] = "Exam not submitted"
        res["submitted"] = "False"

    return res, 200
