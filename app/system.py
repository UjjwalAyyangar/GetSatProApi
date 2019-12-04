from app.models import *
from flask_login import current_user, login_user, logout_user
from functools import wraps
from app.dac import *
from flask import jsonify


# utility function to map number to difficulty
def get_difficulty(num):
    diff = {
        1: "Easy",
        2: "Medium",
        3: "Hard",
    }
    return diff[num]


# utility function to parse a user's submission into desired format
def parse_ans(Submission):
    data = {}
    for ans in Submission:
        data[ans["ques_id"]] = ans["ans"]
    return data


# utility function to parse the options of a user's answers into the desired format for computation
def parse_options(options):
    temp = []
    for option in options:
        if option is not None:
            temp.append(option)

    return temp


def auto_grade(Exam, Submission):
    """ A function that is used to calculate the grade of an exam when it is taken by a student.

    :param Exam: exam model object
    :param Submission: dict : contains details of the answers given by the user
    :return: grade obtained by the student as a float
    """
    questions = Exam.Questions.all()

    total = 0
    count = 0
    parsed_ans = parse_ans(Submission)
    for question in questions:
        q_id = question.Question_ID
        total += 1
        cor_ans = question.Correct_ans
        user_ans = parsed_ans[q_id]

        if user_ans == cor_ans:
            count += 1

    grade = round((float(count) / float(total)) * 100, 2)
    # grade = 0.0
    return grade


# decorator function for checking if the client request is authenticated
def authenticated(function):
    @wraps(function)
    def wrap(*args, **kwargs):
        if current_user.is_authenticated:
            return function(*args, **kwargs)
        else:
            return ErrorResponse(400).content(), 400

    return wrap


# decorator function for checking if the client is an admin
def is_admin(function):
    @wraps(function)
    def wrap(*args, **kwargs):
        if is_User('Admin') == 200:
            return function(*args, **kwargs)
        else:
            return Response(
                401,
                "Only admins are allowed to make this request."
            ).content(), 401

    return wrap


# decorator function for checking if the client is a tutor
def is_tutor(function):
    @wraps(function)
    def wrap(*args, **kwargs):
        if is_User('Tutor') == 200:
            return function(*args, **kwargs)
        else:
            return Response(
                401,
                "Only tutors are allowed to make this request."
            ).content(), 401

    return wrap


# decorator function for checking if the client is an admin or a tutor
def is_admin_tutor(function):
    @wraps(function)
    def wrap(*args, **kwargs):
        if is_User('Tutor') == 200 or is_User('Admin') == 200:
            return function(*args, **kwargs)
        else:
            return Response(
                401,
                "Only admins and tutors are allowed to make this request."
            ).content(), 401

    return wrap


# decorator function for checking if the client is an admin or a student
def is_admin_student(function):
    @wraps(function)
    def wrap(*args, **kwargs):
        if is_User('Student') == 200 or is_User('Admin') == 200:
            return function(*args, **kwargs)
        else:
            return Response(
                401,
                "Only admins and students are allowed to make this request."
            ).content(), 401

    return wrap


# decorator function for checking if the client is a tutor or a student
def is_tutor_student(function):
    @wraps(function)
    def wrap(*args, **kwargs):
        if is_User('Student') == 200 or is_User('Tutor') == 200:
            return function(*args, **kwargs)
        else:
            return Response(
                401,
                "Only tutors and students are allowed to make this request."
            ).content(), 401

    return wrap


# decorator function for checking if the client is a student
def is_student(function):
    @wraps(function)
    def wrap(*args, **kwargs):
        if is_User('Student') == 200:
            return function(*args, **kwargs)
        else:
            return Response(
                401,
                "Only students can make this type of requests."
            ).content(), 401

    return wrap


def is_User(usr_type):
    """

    :param usr_type: string : "Student", "Tutor", "Admin"
    :return: integer -> 200: if the user is of the type specified in usr_type, 401 otherwise
    """
    if current_user.is_authenticated:
        if current_user.UserRole.User_Type == usr_type:
            return 200
        else:
            return 401
    else:
        return 401


def complete_request(data):
    for key in data:
        if not data[key]:
            return False

    return True


def is_acceptable_file(filename):
    """ A utility function that checks if the file uploaded follows an acceptable format

    :param filename: name of the file which needs to be uploaded
    :return: True if the file has an acceptable format, False otherwise
    """
    file_ext = filename.split('.')[1].lower()
    allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    if file_ext in allowed_extensions:
        return True
    else:
        return False


# utility function to map module to folder
def get_folder(mod_id):
    folders = {
        1: "Maths",
        2: "English"
    }
    return folders[mod_id]


class Response():
    """ A utility class for constructing generic api response
    """

    def __init__(self, code=200, msg=None):
        self.code = code
        self.msg = msg

    def content(self):
        return {
            'Status': self.code,
            'message': self.msg
        }


class ErrorResponse(Response):
    """ A utility class that inherits the Response class for constructing generic api error response
    """

    def __init__(self, code=None):
        self.code = code
        self.msg = self.get_standard(code)
        super(ErrorResponse, self).__init__(self.code, self.msg)

    def get_standard(self, code):
        standard = {
            405: "Method not allowed",
            400: "Bad Request",
            401: "Unauthorized request",
            404: "Not found",
            500: "Internal Server Error"
        }
        return standard[code]
