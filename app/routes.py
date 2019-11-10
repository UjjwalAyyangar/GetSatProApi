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
    if current_user.is_authenticated:
        if admin_check != 200:
            res = ErrorResponse(admin_check)

            if admin_check == 401:
                res.msg = "Only Admins can add new users to the system."

            return res.content()

    data = request.get_json()

    if not complete_request:
        res = ErrorResponse(405)
        return res.content()

    user = create_user(data)

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


@app.route('/api/add_module', methods=['POST'])
@jwt_required
def add_module():
    """
    api structure :
    {
        "mod_name" : "Maths"
    }
    """

    # Only an admin is allowed to add new modules

    admin_check = is_User("Admin")

    if admin_check != 200:
        res = ErrorResponse(admin_check)

        if admin_check == 401:
            res.msg = "Only an admin is allowed to add new modules"

        return res.content()

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

    exam = create_exam(data)
    res = Response(
        200,
        "Exam was created successfully"
    )
    res = exists('Exam', exam, res)

    return res.content()


@app.route('/api/view_grade', methods=["POST"])
@jwt_required
def view_grade():
    data = request.get_json()

    # print(is_User("Student"), current_user.UserRole.User_Type)
    if is_User("Student") == 200:
        student_id = current_user.User_ID
    else:
        try:
            student_id = data["student_id"]
        except:
            res = ErrorResponse(400)
            return res.content()

    exam = get_exam(data["exam_id"])

    exam_name = "NA"
    if exam:
        exam_name = exam.Exam_Name

    grade = "NA"

    report = get_report(student_id, data["exam_id"])
    if report:
        grade = report.Grade

    res = Response(
        200,
        "Grades displayed successfully"
    )

    ret = res.content()

    if not exam:
        ret["message"] = "No such exam exists"
    elif not report:
        ret["message"] = "The user has not given this exam, yet."

    ret["exam_name"] = exam_name
    ret["grade"] = grade

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

    try:
        # create an answerSheet
        new_ans_sheet = create_ans_sheet({
            "student_id": student_id,
            "exam_id": data["exam_id"]
        })

        # Create answers and add them into sheets
        for ans in sub:
            _ = create_ans({
                "student_id": student_id,
                "ques_id": ans["ques_id"],
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
    except:
        res = Response(
            400,
            "The exam is already submitted"
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


# Exam discussion

# Create

@app.route('/api/create_discussion', methods=["POST"])
@jwt_required
def create_discussion():
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
def create_discus_thread():
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
def view_discussion():
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
def view_flashcards():
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
def set_pref():
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
# @jwt_required
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
