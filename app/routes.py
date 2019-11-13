from app import app
from flask import abort, request, jsonify, g, url_for, redirect, render_template
from flask_httpauth import HTTPBasicAuth
from flask_login import current_user, login_user, logout_user
from app import db, flask_bcrypt, jwt, login
from app.models import *
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity
)
from app.system import *
from app.dac import *


@app.route('/base', methods=["GET", "POST"])
def function():
    data = request.get_json()


# from app.constants import *

# app = create_app()

@app.route('/')
@app.route('/doc')
@app.route('/index')
def doc():
    return render_template('doc.html')


# User Registration
@app.route('/register', methods=['POST'])
def register():
    """ End-point for user registration.
    ---
    description: User Registration.
    post:
        description: User Registration.
        requestBody:
            description : Request body
            content:
                application/json:
                    schema:
                        type: object
                        required:
                            - username
                            - fname
                            - lname
                            - password
                            - email
                            - phone
                            - role_id
                        properties:
                            username:
                                type: string
                                description: Username
                                example: ObiWan
                            fname:
                                type: string
                                description: First name of the user
                                example: Obi
                            lname:
                                type: string
                                description: Last name of the user
                                example: Wan
                            password:
                                type: string
                                description: The password that the user wants to set
                                example: Ob12W@n
                            email:
                                type: string
                                description: Email id of the user
                                example: obi@wan.com
                            phone:
                                type: string
                                description: Phone number of the user
                                example: 999-999-9999
                            role_id:
                                type: string
                                description: Used to denote the type of user. 1 = Student, 2 = Tutor, 3 = Admin
                                example: 1
        responses:
            200:
                description: Successful creation of a user
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
                                    example: User created successfully
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
                                    example: Only Admins can add new users to the system.
            405:
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
                                    example: Method not allowed
    """
    admin_check = is_User("Admin")
    if current_user.is_authenticated:
        if admin_check != 200:
            res = ErrorResponse(admin_check)

            if admin_check == 401:
                res.msg = "Only Admins can add new users to the system."

            return res.content()

    data = request.get_json()
    print(data)
    if not complete_request:
        res = ErrorResponse(405)
        return res.content()

    user = create_user(data)
    print(user)
    res = Response(
        200,
        "User created successfully"
    )
    res = exists('User', user, res)

    return res.content()


@login.user_loader
def load_user(id):
    # print(id)
    return UserInfo.query.filter_by(User_ID=int(id)).one()


# Get users
@app.route('/users/<int:id>')
@jwt_required
def show_user(id):
    user = UserInfo.query.get(id)
    if not user:
        res = ErrorResponse(404)
        return res.content()

    data = {}

    data['UserType'] = user.UserRole.User_Type
    data['userInfo'] = {
        'FirstName': user.First_Name,
        'LastName': user.Last_Name,
        'userId': user.User_ID,
        'lastloggedin': user.Last_Login,
    }
    return jsonify(data)


# is_admin_tutor

@app.route('/api/list_students')
@jwt_required
@is_admin_tutor
def api_list_students():
    """ End-point for getting list of students.
    ---
    description: List of students. [Jwt]
    get:
        description: List of students.

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
                                students:
                                    type: array
                                    description: A list of dictionary of students
                                    items:
                                        type: object
                                        description: Student list
                                        properties:
                                            username:
                                                type: string
                                                example: ObiWan
                                                description: Username of the student
                                            user_id:
                                                type: string
                                                example: 1234
                                                description: User ID of the student
                                            fname:
                                                type: string
                                                example: Obi
                                                description: First name of the student
                                            lname:
                                                type: string
                                                example: Wan
                                                description: Last name of the student
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
            404:
                description: Students not found
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
    """
    students = get_users(1)
    print(students)
    if students:
        res = Response(
            200,
            "Successfully fetched the list of students"
        )
        ret = res.content()
        stud_list = []
        for student in students:
            temp = {
                USERNAME: student.Username,
                USER_FNAME: student.First_Name,
                USER_LNAME: student.Last_Name,
                USER_ID: student.User_ID
            }

            stud_list.append(temp)

        ret[STUDENTS] = stud_list
        return ret
    else:
        return ErrorResponse(404).content()


@app.route('/api/add_module', methods=['POST'])
@jwt_required
@is_admin
def api_add_module():
    """ End-point for adding new modules.
            ---
            description: Add module
            post:
                description: Adding a new module
                requestBody:
                    description : Request body
                    content:
                        application/json:
                            schema:
                                type: object
                                required:
                                    - mod_name
                                properties:
                                    mod_name:
                                        type: string
                                        description: The name of the module that needs to be added
                                        example: maths
                responses:
                    200:
                        description: Successful creation of a new module
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
                                            example: Module added in successfully
                    401:
                        description: Bad request
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
                                            example: Only an admin is allowed to add modules.
            """

    data = request.get_json()
    if data is None:
        abort(404)

    try:
        module = create_module(data)
        res = Response(
            200,
            "Module added successfully"
        )

        res = exists('Module', module, res)

        return res.content()

    except Exception as e:
        # print(e)
        res = ErrorResponse(400)
        return res.content()


@app.route('/api/delete', methods=['POST'])
@jwt_required
@is_admin
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
    field = get_model_field(model_name, model_id)
    if not field:
        return ErrorResponse(404).content()

    deleted = delete(field)
    if not deleted:
        return ErrorResponse(500).content()

    return Response(
        200,
        "Successfully deleted."
    ).content()


# Exams
# Create Exam Request

@app.route('/api/create_exam', methods=["POST"])
@jwt_required
@is_admin_tutor
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

    exam = create_exam(data)
    if not exam:
        return ErrorResponse(500).content()

    res = Response(
        200,
        "Exam was created successfully"
    )
    res = exists('Exam', exam, res)

    return res.content()


@app.route('/api/view_grade', methods=["POST"])
@jwt_required
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

    if not current_user.is_authenticated:
        return ErrorResponse(401).content()

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
            return res.content()

    # check if that exam exists
    exam = get_exam(exam_id)
    if not exam:
        return ErrorResponse(400).content()

    # check if the student has submitted that exam
    if not check_sub_exam(exam_id, stud_id):
        return ErrorResponse(400).content()

    report = get_report(stud_id, exam_id)

    # report cannot be null at this point
    res = Response(
        200,
        "Grade displayed successfully"
    ).content()

    res[GRADE] = report.Grade
    res[EXAM_NAME] = exam.Exam_Name
    return res


@app.route('/api/view_grades', methods=["POST"])
@jwt_required
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
                                    module_id:
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
    if not current_user.is_authenticated:
        return ErrorResponse(401).content()

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
            return res.content()

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

    return res


@app.route('/api/submit_exam', methods=["POST"])
@jwt_required
@is_student
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
    exam = get_exam(exam_id)
    if not exam:
        return Response(
            404,
            "Exam does not exist"
        ).content()

    # check if the user has already submitted this exam or not
    if check_sub_exam(exam_id):
        return Response(
            200,
            "Exam already submitted"
        ).content()

    # if the user has not submitted, make new submission
    sub = data["sub"]

    # get grades
    grade = auto_grade(exam, sub)

    # create a new sheet
    new_ans_sheet = create_ans_sheet({
        STUDENT_ID: student_id,
        EXAM_ID: exam_id
    })

    # sheet creation check
    if not new_ans_sheet:
        return Response(
            500,
            "Unable to create new answer sheet"
        ).content()

    for ans in sub:
        new_ans = create_ans({
            STUDENT_ID: student_id,
            QUESTION_ID: ans[QUESTION_ID],
            ANSWER: ans[ANSWER]
        }, sheet=new_ans_sheet)

        # ans creation check
        if not new_ans:
            return Response(
                500,
                "Unable to create new answers"
            ).content()

    new_report = create_report({
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
        ).content()

    return Response(
        200,
        "Exam submitted successfully"
    ).content()


@app.route('/api/check_sub', methods=["POST"])
@jwt_required
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
    if not current_user.is_authenticated:
        return ErrorResponse(401).content()

    data = request.get_json()
    stud_id = data.get(STUDENT_ID)
    if not stud_id:
        stud_id = current_user.User_ID

    exam = get_exam(data[EXAM_ID])
    if not exam:
        return Response(
            400,
            "Exam does not exists"
        ).content()
    res = Response(200, "").content()
    if check_sub_exam(data[EXAM_ID], stud_id):
        res["message"] = "Fetched exam successfully"
        res["submitted"] = "True"
    else:
        res["message"] = "Exam not submitted"
        res["submitted"] = "False"

    return res


# Exam available to a user in a selected module
@app.route('/api/get_exams')
@app.route('/api/get_exams/<int:module_id>')
@jwt_required
def api_get_exams(module_id=None):
    """ End-point for getting list of Exams.
       ---
       description: List of Exams. [Jwt]
       get:
           description: List of Exams

           parameters:
            - in: path
              name: mod_id
              schema:
                type: integer
                required: False
              description: Only required if you want to fetch the exams of a module. [OPTIONAL]
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
                                       example: Unauthorized request
       """
    if not current_user.is_authenticated:
        res = ErrorResponse(401)
        return res.content()

    if module_id:
        Exams = get_exams(module_id)
    else:
        Exams = get_exams()

    exam_list = []

    if not Exams:
        return ErrorResponse(404).content()

    for exam in Exams:
        temp = {
            "exam_id": exam.Exam_ID,
            "exam_name": exam.Exam_Name,

        }
        exam_list.append(temp)

    res = Response(
        200,
        "Fetched exams successfully"
    )

    ret = res.content()
    ret["exams"] = exam_list
    return ret


# Exam discussion

# Create

@app.route('/api/create_discussion', methods=["POST"])
@jwt_required
def api_create_discussion():
    data = request.get_json()
    data["user_id"] = current_user.User_ID
    new_discus = create_discussion(data)

    try:
        res = Response(
            200,
            "Discussion created successfully"
        )

        res = exists('Discussion', new_discus, res)

        return res.content()
    except:
        res = ErrorResponse(400)
        return res.content()


@app.route('/api/create_discus_thread', methods=["POST"])
@jwt_required
def api_create_discus_thread():
    data = request.get_json()
    data["user_id"] = current_user.User_ID
    new_dthread = create_discus_thread(data)
    try:
        res = Response(
            200,
            "Discussion thread created successfully"
        )

        res = exists('Discussion', new_dthread, res)

        return res.content()
    except:
        return res.content()


@app.route('/api/view_discussion')
@jwt_required
def api_view_discussion():
    data = request.get_json()
    discuss = get_discussion(data)

    if discuss:
        reply_list = []
        replies = discuss.Replies.all()

        for reply in replies:
            temp = {
                "thread_id": reply.Thread_ID,
                "content": reply.Message,
            }
            reply_list.append(temp)

        res = Response(
            200,
            "Fetched discussion successfully"
        )
        ret = res.content()
        ret["replies"] = reply_list
        ret["discuss_id"] = data["discuss_id"]

        return ret
    else:
        res = ErrorResponse(400)
        return res.content()


# Flashcards
@app.route('/api/view_flashcard')
@jwt_required
def api_view_flashcards():
    data = request.get_json()
    fset = get_flashcard_set(data)

    if fset:
        flashcards = fset.Flashcards.all()
        card_list = []
        for card in flashcards:
            temp_data = {
                "fc_id": card.FC_ID
            }
            temp_card = get_flashcard(temp_data)
            if temp_card:
                card_data = {
                    "set_id": data["set_id"],
                    "question": temp_card.Question,
                    "answer": temp_card.Answer,
                }

                pref = get_fcpref({
                    "stud_id": current_user.User_ID,
                    "fc_id": card.FC_ID
                })

                card_data["difficulty"] = get_difficulty(pref.Difficulty)

                card_list.append(card_data)
            else:
                continue

        res = Response(
            200,
            "Fetched flashcard sets successfully"
        )

        ret = res.content()
        ret["flashcards"] = card_list.append()

        return ret
    else:
        return ErrorResponse(400).content()


@app.route('/api/set_pref')
@jwt_required
def api_set_pref():
    data = request.get_json()
    fc_pref = get_fcpref({
        "stud_id": current_user.User_ID,
        "FC_ID": data["fc_id"]
    })

    if fc_pref:
        fc_pref.difficulty = data["diff"]
        db.session.commit()
        return Response(
            200,
            "Preference set succesfully"
        ).content()

    else:
        return ErrorResponse(400).content()


# /users/<int:id>

@app.route('/login', methods=['POST'])
def login():
    """ End-point for logging in exams.
            ---
            description: Login
            post:
                description: Login
                requestBody:
                    description : Request body
                    content:
                        application/json:
                            schema:
                                type: object
                                properties:
                                    username:
                                        type: string
                                        description: Username of the user who wants to log in
                                        example: ObiWan
                                        required: true
                                    password:
                                        type: string
                                        description: Password of the user who wants to log in
                                        example: P@$$word
                                        required: true
                responses:
                    200:
                        description: Successful login
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
                                            example: User logged in successfully
                                        token:
                                            type: string
                                            example : the JWT token
                                        refresh:
                                            type: string
                                            example: the refresh token
                                        user_info:
                                            type: object
                                            properties:
                                                first_name:
                                                    type: string
                                                    example: Obi
                                                last_name:
                                                    type: string
                                                    example: Wan
                                                user_id:
                                                    type: string
                                                    example: 123
                                                user_type:
                                                    type: string
                                                    example: Student
                                                username:
                                                    type: string
                                                    example: ObiWan
                    401:
                        description: Invalid credentials
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
                                            example: Invalid credentials
            """

    data = request.get_json()

    # return data

    if data is None:
        abort(404)

    if current_user.is_authenticated:
        res = Response(
            200,
            "User already logged in"
        )
        username = current_user.Username
        ret = res.content()
        ret['username'] = username
        return ret

    username = data['username']

    del data["username"]
    password = data['password']
    # user = UserInfo.query.filter_by(Username=username).one()
    user = get_user(uname=username)
    if not user:
        return ErrorResponse(404).content()

    print(user)

    if user and flask_bcrypt.check_password_hash(user.Login_password, password):
        access_token = create_access_token(identity=data)
        refresh_token = create_refresh_token(identity=data)
        del data['password']
        data['token'] = access_token
        data['refresh'] = refresh_token
        data['user_info'] = {
            "user_type": user.UserRole.User_Type,
            'first_name': user.First_Name,
            'last_name': user.Last_Name,
            'user_id': user.User_ID,
            'last_logged_in': user.Last_Login,
            "username": username
        }

        data["Status"] = 200
        data["message"] = "User logged in successfully"
        login_user(user)
        return jsonify(data)

    else:
        return jsonify({
            'Status': 401,
            'message': "Invalid credentials"
        })


@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    ret = {
        'token': create_access_token(identity=current_user)
    }
    return jsonify({'data': ret})


@jwt.unauthorized_loader
def unauthorized_response(callback):
    res = ErrorResponse(401)
    return res.content()


@app.route('/logout')
# @jwt_required
def logout():
    """ End-point for logging out.
                ---
                description: Logout
                get:
                    description: Logout
                    responses:
                        200:
                            description: Successful Logout
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
                                                example: User logged out successfully
                                            user_id:
                                                type: string
                                                description: the userid of the logged out user
                                                example : 23
                        400:
                            description: Already logged out
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
                                                example: Already logged out i.e. no user is logged in.
                """
    if not current_user.is_authenticated:
        res = Response(
            400,
            "Already logged out i.e. no user is logged in."
        )

        return res.content()

    res = Response(
        200,
        "Logged out successfully"
    )

    ret = res.content()
    ret["user_id"] = current_user.User_ID
    logout_user()

    return ret
