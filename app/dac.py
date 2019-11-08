# The data access layer

# Some of these methods could have been written in models
# but I wanted these separate. For better code organization.
from app.models import *
from app import db, flask_bcrypt
import sqlalchemy


def get_user(user_id):
    try:
        return UserInfo.query.filter_by(User_ID=user_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def create_user(data):
    pwd = flask_bcrypt.generate_password_hash(data.get('password'))
    print(pwd)
    new_user = UserInfo(
        Username=data["username"],
        Login_password=pwd,
        First_Name=data["fname"],
        Last_Name=data["lname"],
        Email=data["email"],
        Phone=data["phone"],
        Role_ID=int(data["role_id"])
    )


    db.session.add(new_user)
    db.session.commit()
    print(new_user)
    print("Created")
    return new_user


def get_module(mod_id):
    try:
        return Module.query.filter_by(Module_ID=mod_id)
    except sqlalchemy.orm.exc.NoResultFound:
        return None

def create_module(data):
    new_module = Module(
        Module_Name=data["mod_name"]
    )
    db.session.add(new_module)
    db.session.commit()
    return new_module


def get_exam(id):
    try:
        return Exam.query.filter_by(
        Exam_ID=id
        ).one()

    except sqlalchemy.orm.exc.NoResultFound:
        return None


def create_exam(data):
    new_exam = Exam(
        Exam_Name=data["name"],
        Module_ID=data["mod_id"]
    )
    db.session.add(new_exam)
    db.session.commit()

    # add questions to the exam
    questions = data["questions"]

    for question in questions:
        temp_data = {
            "exam_id": new_exam.Exam_ID,
            "question": question["question"],
            "options": question["options"],
            "correct_ans": question["correct_ans"]
        }
        create_question(temp_data)

    return new_exam


def create_question(data):
    new_question = ExamQuestion(
        Exam_ID=data["exam_id"],
        Question=data["question"],
        Option_1=data["options"][0],
        Option_2=data["options"][1],
        Option_3=data["options"][2],
        Correct_ans=data["correct_ans"]
    )

    db.session.add(new_question)
    db.session.commit()

    return new_question


def create_ans_sheet(data):
    new_ans_sheet = StudentAnswerSheet(
        Student_ID=data["student_id"],
        Exam_ID=data["exam_id"]
    )

    db.session.add(new_ans_sheet)
    db.session.commit()

    return new_ans_sheet


def create_ans(data, sheet=None):
    new_ans = UserAnswer(
        Student_ID=data["student_id"],
        Question_ID=data["ques_id"],
        Ans=data["ans"]
    )
    if sheet:
        sheet.Answers.append(new_ans)
    else:
        db.session.add(new_ans)
        db.session.commit()

    return new_ans


def get_report(student_id, exam_id):
    try :
        return StudentReport.query.filter_by(
            Student_ID=student_id,
            Exam_ID=exam_id
        ).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def create_report(data):
    new_report = StudentReport(
        Student_ID=data["student_id"],
        Exam_ID=data["exam_id"],
        Sheet_ID=data["sheet_id"],
        Grade=data["grade"]
    )

    db.session.add(new_report)
    db.session.commit()
    return new_report
