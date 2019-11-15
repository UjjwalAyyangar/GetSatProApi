from app.models import *
from flask_login import current_user, login_user, logout_user
from functools import wraps
from app.dac import *
from flask import jsonify


def get_difficulty(num):
    diff = {
        1: "Easy",
        2: "Medium",
        3: "Hard",
    }
    return diff[num]


def parse_ans(Submission):
    data = {}
    for ans in Submission:
        data[ans["ques_id"]] = ans["ans"]

    return data


def auto_grade(Exam, Submission):
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

    print(total)
    # grade = (float(count) / float(total)) * 100
    grade = 0.0
    return grade


# decorator
def authenticated(function):
    @wraps(function)
    def wrap():
        if current_user.is_authenticated:
            return function()
        else:
            return ErrorResponse(400).content(), 400

    return wrap


# decorator
def is_admin(function):
    @wraps(function)
    def wrap():
        if is_User('Admin') == 200:
            return function()
        else:
            return Response(
                401,
                "Only admins are allowed to make this request."
            ).content(), 401

    return wrap


# decorator
def is_tutor(function):
    @wraps(function)
    def wrap():
        if is_User('Tutor') == 200:
            return function()
        else:
            return Response(
                401,
                "Only tutors are allowed to make this request."
            ).content(), 401

    return wrap


# decorator
def is_admin_tutor(function):
    @wraps(function)
    def wrap():
        if is_User('Tutor') == 200 or is_User('Admin') == 200:
            return function()
        else:
            return Response(
                401,
                "Only admins and tutors are allowed to make this request."
            ).content(), 401

    return wrap

# decorator
def is_admin_student(function):
    @wraps(function)
    def wrap():
        if is_User('Student') == 200 or is_User('Admin') == 200:
            return function()
        else:
            return Response(
                401,
                "Only admins and students are allowed to make this request."
            ).content(), 401

    return wrap

# decorator
def is_tutor_student(function):
    @wraps(function)
    def wrap():
        if is_User('Student') == 200 or is_User('Tutor') == 200:
            return function()
        else:
            return Response(
                401,
                "Only tutors and students are allowed to make this request."
            ).content(), 401

    return wrap

# decorator
def is_student(function):
    @wraps(function)
    def wrap():
        if is_User('Student') == 200:
            return function()
        else:
            return Response(
                401,
                "Only students can make this type of requests."
            ).content(), 401

    return wrap


def is_User(usr_type):
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


class Response():
    def __init__(self, code=200, msg=None):
        self.code = code
        self.msg = msg

    def content(self):
        return {
            'Status': self.code,
            'message': self.msg
        }


class ErrorResponse(Response):
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


"""
Some of the issues I am facing
* DB sync
* Scalability? I'll have to check. But I can do it.


"""
