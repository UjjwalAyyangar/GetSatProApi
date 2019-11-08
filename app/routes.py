from app import app
from flask import abort, request, jsonify, g, url_for, redirect
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
@app.route('/index')
def index():
    return 'Hello, World!'


# User Registration
@app.route('/register', methods=['POST'])
def register():
    admin_check = is_User("Admin")
    if admin_check != 200:
        res = ErrorResponse(admin_check)

        if admin_check == 401:
            res.msg = "Only Admins can make this request"

        return res.content()

    data = request.get_json()

    if not complete_request:
        res = ErrorResponse(405)
        return res.content()

    _ = create_user(data)

    res = Response(
        200,
        "User created successfully"
    )

    return res.content()


@login.user_loader
def load_user(id):
    # print(id)
    return UserInfo.query.filter_by(User_ID=int(id)).one()


# Get users
@app.route('/users/<int:id>')
@jwt_required
def get_user(id):
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


@app.route('/api/add_module', methods=['POST'])
@jwt_required
def add_module():
    """
    api structure :
    {
        "mod_name" : "Maths"
    }
    """
    data = request.get_json()
    if data is None:
        abort(404)

    try:
        _ = create_module(data)
        res = Response(
            200,
            "Module added successfully"
        )

        return res.content()

    except:
        res = ErrorResponse(400)


# Exams
# Create Exam Request

@app.route('/api/create_exam', methods=["POST"])
@jwt_required
def create_exam():
    """
    api_structure :
    {
    "mod_id": 1,
    "name": "random",
    "questions": [
        {
            "question": "What is the answer of life?",
            "correct_ans": "42",
            "options": ["31", "0", "42"]

        },
        {
            "question": "Who is Arsenal's best manager",
            "correct_ans": "Arsene Wenger",
            "options": ["Arsene Wenger", "Unai Emery", "Herbery Chapman"]
        }
    ]
}

    """
    data = request.get_json()
    ad_tut_check = is_User("Admin") or is_User("Tutor")
    if ad_tut_check != 200:
        res = ErrorResponse(ad_tut_check)

        if ad_tut_check == 401:
            res.msg = "Only Admins or Tutors can make this request"

        return res.content()

    _ = create_exam(data)
    res = Response(
        200,
        "Exam was created successfully"
    )

    return res.content()


@app.route('/api/view_grade', methods=["POST"])
@jwt_required
def view_grade():
    data = request.get_json()

    if is_User("Student") == 200:
        student_id = current_user.User_ID
    else:
        try:
            student_id = data["student_id"]
        except:
            res = ErrorResponse(400)
            return res.content()

    exam = get_exam(data["exam_id"])

    report = get_report(student_id, data["exam_id"])

    res = Response(
        200,
        "Grades displayed successfully"
    )
    ret = res.content()
    ret["exam_name"] = exam.Exam_Name
    ret["grade"] = report.Grade

    return ret


@app.route('/api/submit_exam', methods=["POST"])
@jwt_required
def submit_exam():
    stud_check = is_User("Student")
    if stud_check != 200:
        res = ErrorResponse(401)
        if stud_check == 401:
            res.msg = "Only a student can submit an exam."

        return res.content()

    data = request.get_json()
    student_id = current_user.User_ID

    exam_id = data["exam_id"]
    exam = Exam.query.filter_by(Exam_ID=exam_id).one()
    sub = data["sub"]
    grade = auto_grade(exam, sub)

    # create an answerSheet
    new_ans_sheet = create_ans_sheet({
        "student_id": student_id,
        "exam_id": data["exam_id"]
    })

    # Create answers and add them into sheets
    for ans in sub:
        _ = create_ans({
            "student_id": student_id,
            "question_id": ans["ques_id"],
            "ans": ans["ans"]
        }, sheet=new_ans_sheet)

    # Create report
    _ = create_report({
        "student_id": student_id,
        "exam_id": exam_id,
        "sheet_id": new_ans_sheet.Sheet_ID,
        "grade": grade
    })

    res = Response(
        200,
        "Exam submitted successfully"
    )

    return res.content()


# Exam available to a user in a selected module
@app.route('/api/get_exams')
@jwt_required
def get_exams():
    if not current_user.is_authenticated:
        res = ErrorResponse(401)
        return res.content()

    data = request.get_json()

    module = get_module(data["mod_id"]).one()

    Exams = module.Exams.all()

    exam_list = []

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


# /users/<int:id>

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    # return data

    if data is None:
        abort(404)

    if current_user.is_authenticated:
        res = Response(
            200,
            "User already logged in"
        )
        return res.content()


    username = data['username']

    del data["username"]
    password = data['password']
    user = UserInfo.query.filter_by(Username=username).first()
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
#@jwt_required
def logout():

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


# TODO
"""
Implement Login from this - https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
Combine it with this - https://blog.miguelgrinberg.com/post/restful-authentication-with-flask
JWT - https://medium.com/@riken.mehta/full-stack-tutorial-3-flask-jwt-e759d2ee5727

"""
