from flask import Blueprint, jsonify, make_response
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
    """ This function is used to store the details of the current user in the session

    :param id: id of the user
    :return: UserInfo model object which contains the details of a user
    """
    return UserInfo.query.filter_by(User_ID=int(id)).one()


@mod.route('/register', methods=["POST"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
def register():
    """ API endpoint for user registration

    :return: JSON response indicating whether user registration was successful or not
    """
    admin_check = is_User("Admin")

    # only an admin has the privilege of adding new users(without registration)
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

    # creating a new user in the database
    user = users_dac.create_user(data)

    # checking if the user already exists
    if not user:
        return Response(
            400,
            "User already exists in the system"
        ).content(), 400

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

    # returning apt. json response to the client
    return res.content(), 200


@mod.route('/login', methods=['POST'])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
def login():
    """ API endpoint for logging in to the system.

    :return: response JSON containing details about whether the login was successful or not.
    """

    data = request.get_json()

    if data is None:
        abort(404)

    # checking if the user is already logged in
    if current_user.is_authenticated:
        res = Response(
            400,
            "User already logged in"
        )
        username = current_user.Username
        ret = res.content()
        ret['username'] = username
        return ret, 400

    username = data[USERNAME]

    del data[USERNAME]
    password = data[USER_PWD]
    # getting the user from the database
    user = users_dac.get_user(uname=username)

    # if the user is not present, return 404
    if not user:
        return ErrorResponse(404).content(), 404

    # encrypting the enterted password and checking if it matches with the user's password
    if user and flask_bcrypt.check_password_hash(user.Login_password, password):
        access_token = create_access_token(identity=data)
        refresh_token = create_refresh_token(identity=data)
        del data[USER_PWD]

        data['token'] = access_token  # adding JWT token to the response
        data['refresh'] = refresh_token  # adding refresh token to the response
        # constructing json response for the logged in user's info
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

        # constructing and returning json response for the client
        ret = make_response(jsonify(data))
        return ret

    else:
        return jsonify({
            'Status': 401,
            'message': "Invalid credentials"
        }), 401


@mod.route('/logout')
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@authenticated
def logout():
    """ API endpoint for logging out of the system

    :return: JSON response indicating whether the user was able to log out successfully or not.
    """

    # checking if the user is logged in or not
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

    # logging the user out
    logout_user()
    # returning json response to the client
    return ret


@mod.route('/refresh', methods=['POST'])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_refresh_token_required
def refresh():
    """ API endpoint used for creating a new JWT token when it expires

    :return: JSON response containing the new JWT token
    """
    current_user = get_jwt_identity()  # getting the details about the logged in user
    ret = {
        'token': create_access_token(identity=current_user)  # creating new token using the refresh token
    }
    return jsonify({'data': ret})  # returning the newly created refresh token in a json response to the client


@jwt.unauthorized_loader
def unauthorized_response(callback):
    """ A method for returning "Unauthorized request" json to the client for all the unauthorized requests

    :param callback: the function on which an unauthorized call was issued.
    :return: JSON containing details of unauth request by client
    """
    res = ErrorResponse(401)
    return res.content()


@mod.route('/get_students')
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@is_admin_tutor
def api_get_students():
    """ API endpoint for list of students in the system

    :return: JSON object containing details of the list of students in the system.
    """

    # getting list of students from the system
    students = users_dac.get_users(1)
    if students:
        res = Response(
            200,
            "Successfully fetched the list of students"
        )
        ret = res.content()
        stud_list = []
        for student in students:
            # constructing json response for each student
            temp = {
                USERNAME: student.Username,
                USER_FNAME: student.First_Name,
                USER_LNAME: student.Last_Name,
                USER_ID: student.User_ID
            }

            stud_list.append(temp)

        ret[STUDENTS] = stud_list
        response = jsonify(ret)

        return response, 200
    else:
        return ErrorResponse(404).content(), 404


@mod.route('/get_tutors', methods=["GET", "POST"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@is_admin
def api_get_tutors():
    """ API endpoint for getting the list of tutors in the system

    :return: JSON response object that has the details of all the tutors in the system
    """

    # checking if the request method is POST request or not
    is_Post = request.method == "POST"
    tutors = []
    if not is_Post:
        # getting list of tutors in the system
        tutors = users_dac.get_tutors({})
    else:
        data = request.get_json()
        if MODULE_ID in data:
            # getting list of tutors in a specific module fo the system
            tutors = users_dac.get_tutors(data)
        else:
            return ErrorResponse(400).content(), 400

    tut_lis = []
    for tutor in tutors:
        # constructing json response for the detail of each tutor
        user = users_dac.get_user(user_id=tutor.Tutor_ID)
        temp = {
            TUTOR_ID: tutor.Tutor_ID,
            USERNAME: user.Username,
            USER_FNAME: user.First_Name,
            USER_LNAME: user.Last_Name,
            MODULE_ID: tutor.Module_ID
        }
        tut_lis.append(temp)

    res = Response(200, "Successfully fetched all the tutors").content()
    res[TUTOR_LIST] = tut_lis
    # returning apt response json to the client
    return res, 200


@mod.route('/get_user', methods=["POST"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@authenticated
def get_user():
    """ API endpoint for getting the general details of a user

    :return: JSON object containing details of a user
    """
    data = request.get_json()
    user = users_dac.get_user(user_id=data[USER_ID])
    if not user:
        return ErrorResponse(404).content(), 404

    user_info = {
        # constructing the response json of a user
        USER_ID: user.User_ID,
        USER_FNAME: user.First_Name,
        USER_FNAME: user.Last_Name,
        USERNAME: user.Username
    }

    res = Response("Successfully fetched the user", 200).content()

    res[USER_INFO] = user_info
    # returning apt json to the client
    return res, 200
