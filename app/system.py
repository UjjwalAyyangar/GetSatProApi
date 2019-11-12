from app.models import *
from flask_login import current_user, login_user, logout_user


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

    grade = (float(count) / float(total)) * 100

    return grade


def is_User(usr_type):
    if current_user.is_authenticated:
        if current_user.UserRole.User_Type == usr_type:
            return 200
        else:
            return 401
    else:
        return 400


def complete_request(data):
    for key in data:
        if not data[key]:
            return False

    return True


class Response():
    def __init__(self, code=None, msg=None):
        self.code = code
        self.msg = msg

    def content(self):
        return {
            'status': self.code,
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
            401: "Unauthorized request"
        }

"""
Some of the issues I am facing
* DB sync
* Scalability? I'll have to check. But I can do it.


"""
