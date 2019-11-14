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

    return res.content(), 200


@login.user_loader
def load_user(id):
    # print(id)
    return UserInfo.query.filter_by(User_ID=int(id)).one()


# Get users
@app.route('/users/<int:id>')
@jwt_required
@authenticated
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

@app.route('/api/get_students')
@jwt_required
@is_admin_tutor
def api_get_students():
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
        return ret, 200
    else:
        return ErrorResponse(404).content(), 404


@app.route('/api/add_module', methods=['POST'])
@jwt_required
@is_admin  # checks authentication automatically
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

        return res.content(), res.code

    except Exception as e:
        # print(e)
        res = ErrorResponse(400)
        return res.content(), 400


@app.route('/api/get_modules', methods=["GET", "POST"])
@jwt_required
@is_admin_student
def api_get_mods():
    """ End-point for adding listing modules.
            ---
            description: Get modules
            get:
                description: Getting list of modules
                responses:
                    200:
                        description: Successfully fetched modules
                        content:
                            application/json:
                                schema:
                                    type: object
                                    properties:
                                        Status:
                                            type: integer
                                            example: 200
                                        message:
                                            type: string
                                            example: Sucessfully fetched all the modules
                                        mod_list:
                                            type: array
                                            items:
                                                type: object
                                                properties:
                                                    mod_id:
                                                        type: integer
                                                        description : Module id
                                                        example: 34
                                                    mod_name:
                                                        type: string
                                                        description: the name of the Module
                                                        example: Maths
                                                    progress:
                                                        type: flaot
                                                        description: The progress of the student in the module
                                                        example: 20.0
                    400:
                        description: Bad request
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
                                            example: Bad request
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
                                            example: Only admins and students are allowed to make this request.
            post:
                description: Getting list of modules
                requestBody:
                    description : Request body
                    content:
                        application/json:
                            schema:
                                type: object
                                properties:
                                    stud_id:
                                        type: integer
                                        description: The id of the student whose modules you want to see
                                        example: 34
                responses:
                    200:
                        description: Successfully fetched modules
                        content:
                            application/json:
                                schema:
                                    type: object
                                    properties:
                                        Status:
                                            type: integer
                                            example: 200
                                        message:
                                            type: string
                                            example: Sucessfully fetched all the modules
                                        mod_list:
                                            type: array
                                            description: Won't see progress unless stud_id is provided
                                            items:
                                                type: object
                                                properties:
                                                    mod_id:
                                                        type: integer
                                                        description : Module id
                                                        example: 34
                                                    mod_name:
                                                        type: string
                                                        description: the name of the Module
                                                        example: Maths
                                                    progress:
                                                        type: flaot
                                                        description: The progress of the student in the module
                                                        example: 20.0
                    400:
                        description: Bad request
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
                                            example: Bad request
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
                                            example: Only admins and students are allowed to make this request.
            """

    data = request.get_json()
    is_POST = request.method == "POST"
    empty = not (STUDENT_ID in data)

    # Admin cannot make a GET request
    if not is_POST and is_User("Student") != 200:
        return ErrorResponse(400).content(), 400

    # User cannot make a POST request
    if is_POST and is_User("Student") == 200:
        return ErrorResponse(400).content(), 400

    if is_POST and not empty:
        stud_id = data[STUDENT_ID]
    else:
        stud_id = current_user.User_ID

    modules = get_modules()
    if not modules:
        return Response(404, "No modules found").content(404)

    mod_list = []
    for module in modules:
        temp = {
            MODULE_ID: module.Module_ID,
            MODULE_NAME: module.Module_Name
        }
        if (not is_POST) or (is_POST and not empty):
            prog = get_progress(module, stud_id)
            temp[PROGRESS] = prog

        mod_list.append(temp)

    res = Response(
        200,
        "Modules fetched successfully."
    ).content()

    res[MODULE_LIST] = mod_list
    return res, 200


@app.route('/api/delete', methods=['POST'])
@jwt_required
@is_admin  # Checks authentication automatically
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
        return ErrorResponse(404).content(), 404

    deleted = delete(field)
    if not deleted:
        return ErrorResponse(500).content(), 500

    return Response(
        200,
        "Successfully deleted."
    ).content(), 200


# Exams
# Create Exam Request

@app.route('/api/create_exam', methods=["POST"])
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

    exam = create_exam(data)
    if not exam:
        return ErrorResponse(500).content(), 500

    res = Response(
        200,
        "Exam was created successfully"
    )
    res = exists('Exam', exam, res)

    return res.content(), res.code


@app.route('/api/view_grade', methods=["POST"])
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


@app.route('/api/view_grades', methods=["POST"])
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


@app.route('/api/submit_exam', methods=["POST"])
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
    exam = get_exam(exam_id)
    if not exam:
        return Response(
            404,
            "Exam does not exist"
        ).content(), 404

    # check if the user has already submitted this exam or not
    if check_sub_exam(exam_id):
        return Response(
            200,
            "Exam already submitted"
        ).content(), 200

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
        ).content(), 500

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
            ).content(), 500

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
        ).content(), 500

    return Response(
        200,
        "Exam submitted successfully"
    ).content(), 200


@app.route('/api/check_sub', methods=["POST"])
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

    exam = get_exam(data[EXAM_ID])
    if not exam:
        return Response(
            400,
            "Exam does not exists"
        ).content(), 400
    res = Response(200, "").content()
    if check_sub_exam(data[EXAM_ID], stud_id):
        res["message"] = "Fetched exam successfully"
        res["submitted"] = "True"
    else:
        res["message"] = "Exam not submitted"
        res["submitted"] = "False"

    return res, 200


# @app.route('/api/get_exams/<int:module_id>')
# Exam available to a user in a selected module
@app.route('/api/get_exams', methods=["Post"])
@jwt_required
@authenticated
def api_get_exams():
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
                                               ques_no:
                                                   type: integer
                                                   example: 10
                                                   description: Number of questions in an exam
                                               published:
                                                   type: string
                                                   example: 11/2/2019
                                                   description: The date on which the exam was published
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

    data = request.get_json()
    if USER_ID in data:
        stud_id = data[USER_ID]
    else:
        stud_id = current_user.User_ID

    if MODULE_ID in data:
        mod_id = data[MODULE_ID]
    else:
        mod_id = None

    if mod_id:
        Exams = get_exams(mod_id)
    else:
        Exams = get_exams()

    exam_list = []

    if not Exams:
        return ErrorResponse(404).content(), 404

    for exam in Exams:
        question_no = len(exam.Questions.all())
        date = exam.Published.date()
        day = date.day
        month = date.month
        year = date.year
        submitted = check_sub_exam(exam.Exam_ID, stud_id)

        date_str = "{}/{}/{}".format(month, day, year)

        temp = {
            EXAM_ID: exam.Exam_ID,
            EXAM_NAME: exam.Exam_Name,
            QUESTION_NO: question_no,
            PUBLISHED: date_str,
            SUBMITTED: submitted,

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


# Exam discussion

# Create

@app.route('/api/create_discussion', methods=["POST"])
@jwt_required
@authenticated
def api_create_discussion():
    """ End-point for creating a new discussion
                ---
                description: Create Discussion
                post:
                    description: Create Discussion
                    requestBody:
                        description : Request body
                        content:
                            application/json:
                                schema:
                                    type: object
                                    required:
                                        - title
                                        - content
                                        - mod_id
                                    properties:
                                        title:
                                            type: string
                                            description: Title of the main discussion
                                            example: Doubt in Algebra
                                        content:
                                            type: string
                                            description: Content of the main discussion
                                            example: How to derive (x+y)^2 ?
                                        mod_id:
                                            type: integer
                                            description: ID of the module where the discussion has to be created
                                            example: 3
                    responses:
                        200:
                            description: Successfully created a new discussion
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
                                                example: New discussion created successfully
                        401:
                            description: Need to be logged in to make this request
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
                                                example: Unauthorized request.
                        400:
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
                """

    data = request.get_json()
    data[USER_ID] = current_user.User_ID

    new_discus = create_discussion(data)

    try:
        res = Response(
            200,
            "Discussion created successfully"
        )

        res = exists('Discussion', new_discus, res)

        return res.content(), 200
    except:
        res = ErrorResponse(400)
        return res.content(), 400


@app.route('/api/create_discus_thread', methods=["POST"])
@jwt_required
@authenticated
def api_create_discus_thread():
    """ End-point for creating a new discussion reply
                    ---
                    description: Create Reply/Thread
                    post:
                        description: Create Reply/Thread
                        requestBody:
                            description : Request body
                            content:
                                application/json:
                                    schema:
                                        type: object
                                        required:
                                            - discuss_id
                                            - content
                                        properties:
                                            discuss_id:
                                                type: integer
                                                description: ID of the discussion where you want to reply
                                                example: 3
                                            content:
                                                type: string
                                                description: Content of the reply
                                                example: Make a square and divide it.
                        responses:
                            200:
                                description: Successfully replied to the discussion
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
                                                    example: New discussion reply created.
                            401:
                                description: Need to be logged in to make this request
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
                                                    example: Unauthorized request.
                            400:
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
                            404:
                                description: The main discussion associated with the given discuss_id was not found
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
                                                    example: Not found.
                    """
    data = request.get_json()
    data["user_id"] = current_user.User_ID

    if not disc_exists(data[DISCUSS_ID]):
        return ErrorResponse(404).content(), 404

    new_dthread = create_discus_thread(data)
    try:
        res = Response(
            200,
            "Discussion thread created successfully"
        )

        res = exists('Discussion', new_dthread, res)

        return res.content(), res.code
    except:
        return ErrorResponse(400).content(), 400


@app.route('/api/view_discussion')
@jwt_required
@authenticated
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

        return ret, 200
    else:
        res = ErrorResponse(400)
        return res.content(), 400


# Flashcards
@app.route('/api/view_flashcard')
@jwt_required
@authenticated
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

        return ret, 200
    else:
        return ErrorResponse(400).content(), 400


@app.route('/api/set_pref')
@jwt_required
@authenticated
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
        ).content(), 200

    else:
        return ErrorResponse(400).content(), 400


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
            400,
            "User already logged in"
        )
        username = current_user.Username
        ret = res.content()
        ret['username'] = username
        return ret, 400

    username = data['username']
    # print(data)
    del data["username"]
    password = data['password']
    # user = UserInfo.query.filter_by(Username=username).one()
    user = get_user(uname=username)
    if not user:
        return ErrorResponse(404).content(), 404

    # print(user)

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
        }), 401


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
@authenticated
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
