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

    return (jsonify(
        {'username': new_user.Username}
    ), 201)


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


@app.route('/api/add_module')
@jwt_required
def add_module():
    data = request.get_json()
    if data is None:
        abort(404)

    mod_name = data['module_name']
    new_module = Module(Module_Name=mod_name)
    db.session.add(new_module)
    db.session.commit()
    return {
        "Sucessfull": "Yes"
    }


# Exams

@app.route('/api/create_exam')
@jwt_required
def create_exam():
    user_type = current_user.UserRole.User_Type
    res = {}
    if user_type == "Tutor":
        try:
            data = request.get_json()
            if data is None:
                abort(404)

            questions = data["exam"]
            name = data["name"]
            m_id = data["mod_id"]
            for question in questions:
                temp = {}
                temp["correct_answer"] = question["correct_answer"]
                temp["Question"] = question["Question"]

                new_question = ExamQuestion(
                    Question=question["question"],
                    Option_1=question["first_option"],
                    Option_2=question["second_option"],
                    Option_3=question["third_option"],
                    Correct_ans=question["correct_ans"]
                )

                db.session.add(new_question)
                db.session.commit()

            new_exam = Exam(Exam_Name=name, Module_ID=mod_id)
            db.session.add(new_exam)
            db.session.commit()
            return {"Status":200}
        except:
            return {"Status":400}

@app.route('/api/get_exams')
@jwt_required
def get_exams():
    data = request.get_json()
    user_id = int(data["user_id"])
    mod_id = int(data["selected_mod"])

    user = UserInfo.query.filter_by(User_ID=user_id)
    module = Module.query.filter_by(Module_ID=mod_id)

    Exams = module.Exams
    print (Exams)
    return {
        "s":"s"
    }


# /users/<int:id>

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    # return data

    if data is None:
        abort(404)

    if current_user.is_authenticated:
        return redirect(url_for('index'))

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
def logout():
    logout_user()
    return redirect(url_for('index'))


# TODO
"""
Implement Login from this - https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
Combine it with this - https://blog.miguelgrinberg.com/post/restful-authentication-with-flask
JWT - https://medium.com/@riken.mehta/full-stack-tutorial-3-flask-jwt-e759d2ee5727

"""
