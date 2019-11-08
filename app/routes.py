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
from app.system import auto_grade


@app.route('/')
@app.route('/index')
def index():
    return 'Hello, World!'


# User Registration
@app.route('/register', methods=['POST'])
def register():
    # print (type(request.get_json()))
    # return jsonify(request.get_json())

    data = request.get_json()

    for key in request.get_json():
        if data[key] == None:
            abort(400)

    username = request.json.get('username')
    password = flask_bcrypt.generate_password_hash(request.json.get('password'))
    fname = request.json.get('fname')
    lname = request.json.get('lname')
    email = request.json.get('email')
    phone = request.json.get('phone')
    role_id = request.json.get('role_id')

    new_user = UserInfo(
        Username=username,
        Login_password=password,
        First_Name=fname,
        Last_Name=lname,
        Email=email,
        Phone=phone,
        Role_ID=int(role_id)
    )

    db.session.add(new_user)
    db.session.commit()

    logout_user()
    return {
            'Status': 200,
            'Message': "User created successfully"
        }




@login.user_loader
def load_user(id):
    # print(id)
    return UserInfo.query.filter_by(User_ID=int(id)).one()


# Get users
@app.route('/users/<int:id>')
@jwt_required
def get_user(id):
    user = UserInfo.query.get(id)

    data = {}
    # print (user.UserRole)
    # return {"type":"asd"}
    data['UserType'] = user.UserRole.User_Type
    # data['Modules'] = user.
    data['userInfo'] = {
        'FirstName': user.First_Name,
        'LastName': user.Last_Name,
        'userId': user.User_ID,
        'lastloggedin': user.Last_Login,
    }
    # print (user)
    if not user:
        abort(400)
    return jsonify(data)


@app.route('/api/add_module', methods=['POST'])
@jwt_required
def add_module():
    data = request.get_json()
    if data is None:
        abort(404)

    try:
        mod_name = data['module_name']
        new_module = Module(Module_Name=mod_name)
        db.session.add(new_module)
        db.session.commit()
        return {
            "Status": 200
        }
    except:
        return {
            "Status": 400
        }


# Exams
# Create Exam Request
{
    "mod_id": 1,
    "name": "random",
    "exam": [
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


@app.route('/api/create_exam', methods=["POST"])
@jwt_required
def create_exam():
    user_type = current_user.UserRole.User_Type
    print(user_type)
    res = {}
    if user_type == "Tutor":
        try:
            data = request.get_json()
            if data is None:
                return {
                    "Status": 400
                }

            questions = data["exam"]
            # print (questions[0])
            name = data["name"]
            # print(name)
            mod_id = data["mod_id"]

            # create a new exam
            new_exam = Exam(Exam_Name=name, Module_ID=mod_id)
            db.session.add(new_exam)
            db.session.commit()

            # add questions to that exam
            for question in questions:
                options = question["options"]
                new_question = ExamQuestion(
                    Exam_ID=new_exam.Exam_ID,
                    Question=question["question"],
                    Option_1=options[0],
                    Option_2=options[1],
                    Option_3=options[2],
                    Correct_ans=question["correct_ans"]
                )

                db.session.add(new_question)
                db.session.commit()

            return {"Status": 200}
        except:
            # print("up")
            return {"Status": 400}
    return {
        "Status": 400,
        "Reason": "Only Tutors can create exams"
    }

"""
@app.route('/api/get_exam', methods=["GET"])
@jwt_required
def get_exam():
    data = request.get_json()
    user_id = current_user.User_ID
    e_id = int(data['exam_id'])
    exam = Exam.query.filter_by(Exam_ID=e_id).one()
    print(exam.Questions.all())
    return {
        "Done": 200
    }
"""

@app.route('/api/view_grade', methods=["POST"])
@jwt_required
def view_grade():
    data = request.get_json()
    user_id = current_user.User_ID
    exam_id = data["exam_id"]
    exam = Exam.query.filter_by(
        Exam_ID=exam_id
    ).one()

    report = StudentReport.query.filter_by(
        Student_ID=user_id,
        Exam_ID=exam_id
    ).one()

    return {
        "exam_name":exam.Exam_Name,
        "grade":report.Grade,
        "status":200
    }


@app.route('/api/submit_exam',methods=["POST"])
@jwt_required
def submit_exam():
    data = request.get_json()
    user_id = current_user.User_ID
    user_type = current_user.UserRole.User_Type

    if user_type == "Student":
        exam_id = data["exam_id"]
        exam = Exam.query.filter_by(Exam_ID=exam_id).one()
        sub = data["sub"]
        grade = auto_grade(exam, sub)

        # create an answerSheet
        new_ans_sheet = StudentAnswerSheet(
            Student_ID=user_id,
            Exam_ID=exam_id
        )
        db.session.add(new_ans_sheet)
        db.session.commit()

        for answer in sub:
            # add answer to the UserAnswer table
            new_ans = UserAnswer(
                Student_ID=user_id,
                Question_ID=answer['ques_id'],
                Ans=answer['ans']
            )
            # Add answers to the sheet
            new_ans_sheet.Answers.append(new_ans)

        # create a new student report
        new_report = StudentReport(
            Student_ID=user_id,
            Exam_ID=exam_id,
            Sheet_ID=new_ans_sheet.Sheet_ID,
            Grade=grade
        )
        db.session.add(new_report)
        db.session.commit()

        return {
            "Status": 200
        }


    else:
        return {
            "Status": 400
        }


@app.route('/api/get_exams')
@jwt_required
def get_exams():
    data = request.get_json()
    user_id = int(data["user_id"])
    mod_id = int(data["selected_mod"])

    user = UserInfo.query.filter_by(User_ID=user_id)
    module = Module.query.filter_by(Module_ID=mod_id)

    Exams = module.Exams.all()

    data = {}
    data["exams"] = []
    for exam in Exams:
        temp = {
            "exam_id": exam.Exam_ID,
            "exam_name": exam.Exam_Name,

        }
    print(Exams)
    return {
        "s": "s"
    }


# /users/<int:id>

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    # return data

    if data is None:
        abort(404)

    if current_user.is_authenticated:
        return {
            "Status":200,
            "Message":"User already logged in."
        }


    # whatever username is entered
    username = data['username']
    password = data['password']
    user = UserInfo.query.filter_by(Username=username).first()
    # print (user.Login_password)
    # return data
    if user and flask_bcrypt.check_password_hash(user.Login_password, password):
        access_token = create_access_token(identity=data)
        refresh_token = create_refresh_token(identity=data)
        del data['password']
        data['token'] = access_token
        data['refresh'] = refresh_token
        data['UserType'] = user.UserRole.User_Type
        # data['Modules'] = user.
        data['userInfo'] = {
            'FirstName': user.First_Name,
            'LastName': user.Last_Name,
            'userId': user.User_ID,
            'lastloggedin': user.Last_Login,
        }

        data["Status"] = 200
        login_user(user)
        # return data
        return jsonify(data)

    else:
        return jsonify({'Status': 'Invalid'})


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
    return jsonify({
        'message': 'Missing Authorization header'
    }
    ), 401


@app.route('/logout')
@jwt_required
def logout():
    logout_user()
    return {
        "Status":200,
        "Message": "Logged out successfully"
    }


# TODO
"""
Implement Login from this - https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
Combine it with this - https://blog.miguelgrinberg.com/post/restful-authentication-with-flask
JWT - https://medium.com/@riken.mehta/full-stack-tutorial-3-flask-jwt-e759d2ee5727

"""
