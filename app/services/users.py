from flask import Blueprint, jsonify
from flask import abort, request
from app.system import *
from app.constants import *
from datetime import datetime
import pytz

from app.dac import users as users_dac

from app.dac import general as gen_dac
from app.dac import flashcards as fc_dac
from flask_cors import cross_origin
from flask_login import current_user, logout_user, login_user
from app import db, flask_bcrypt, jwt, login
from app import app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity
)

mod = Blueprint('users', __name__, url_prefix='/api')
est = pytz.timezone('US/Eastern')
utc = pytz.utc


@login.user_loader
def load_user(id):
    # print(id)
    return UserInfo.query.filter_by(User_ID=int(id)).one()

    #return logged_user


@mod.route('/register', methods=["POST"])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'], supports_credentials=True)
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

    user = users_dac.create_user(data)
    print(user)
    res = Response(
        200,
        "User created successfully"
    )

    # Make the user's preference table
    if user.Role_ID == 1:
        flashcards = Flashcard.query.all()
        for card in flashcards:
            new_fc_pref = fc_dac.fc_pref_init(card.FC_ID, user.User_ID)

    res = gen_dac.exists('User', user, res)

    return res.content(), 200


@mod.route('/login', methods=['POST'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'], supports_credentials=True)
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
    user = users_dac.get_user(uname=username)
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
            ROLE_TYPE: user.UserRole.User_Type,
            USER_FNAME: user.First_Name,
            USER_LNAME: user.Last_Name,
            USER_ID: user.User_ID,
            'last_logged_in': user.Last_Login,
            USERNAME: username
        }

        data["Status"] = 200
        data["message"] = "User logged in successfully"
        user.Last_Login = datetime.now(est)
        db.session.commit()
        login_user(user)
        return jsonify(data)

    else:
        return jsonify({
            'Status': 401,
            'message': "Invalid credentials"
        }), 401


@mod.route('/logout')
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'], supports_credentials=True)
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


@mod.route('/refresh', methods=['POST'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'], supports_credentials=True)
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


@mod.route('/get_students')
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'], supports_credentials=True)
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
    students = users_dac.get_users(1)
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
        response = jsonify(ret)
        response.headers.add('Access-Control-Allow-Origin', '*')

        return response, 200
    else:
        return ErrorResponse(404).content(), 404
