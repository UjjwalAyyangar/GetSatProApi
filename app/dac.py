# The data access layer

# Some of these methods could have been written in models
# but I wanted these separate. For better code organization.
from app.models import *
from app import db, flask_bcrypt
import sqlalchemy
from flask_login import current_user


def exists(name, obj, res):
    """

    :param name: The name of the object - Discussion, Module, User, etc
    :param obj: The object
    :param res: Our response object, which will return the final API response
    :return: The response object
    """
    if obj:
        return res
    else:
        res.code = 400
        res.msg = "Bad Request. Probably {} already exists".format(name)
        return res


def insert(field):
    """

    :param field: the object of the field that needs to be inserted

    :return: None if the field already exists, otherwise the field object
    """
    try:
        db.session.add(field)
        db.session.commit()
        return field
    except sqlalchemy.exc.IntegrityError:
        return None


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

    return insert(new_user)


def get_module(mod_id):
    try:
        return Module.query.filter_by(Module_ID=mod_id)
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def create_module(data):
    new_module = Module(
        Module_Name=data["mod_name"]
    )

    return insert(new_module)


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

    new_exam = insert(new_exam)

    # add questions to the exam
    questions = data["questions"]

    if new_exam:
        for question in questions:
            temp_data = {
                "exam_id": new_exam.Exam_ID,
                "question": question["question"],
                "options": question["options"],
                "correct_ans": question["correct_ans"]
            }
            _ = create_question(temp_data)

        return new_exam
    else:
        return None


def create_question(data):
    new_question = ExamQuestion(
        Exam_ID=data["exam_id"],
        Question=data["question"],
        Option_1=data["options"][0],
        Option_2=data["options"][1],
        Option_3=data["options"][2],
        Correct_ans=data["correct_ans"]
    )

    return insert(new_question)


def create_ans_sheet(data):
    new_ans_sheet = StudentAnswerSheet(
        Student_ID=data["student_id"],
        Exam_ID=data["exam_id"]
    )

    return insert(new_ans_sheet)


def create_ans(data, sheet=None):
    new_ans = UserAnswer(
        Student_ID=data["student_id"],
        Question_ID=data["ques_id"],
        Ans=data["ans"]
    )
    if sheet:
        sheet.Answers.append(new_ans)
    else:
        new_ans = insert(new_ans)

    return new_ans


def get_report(student_id, exam_id):
    try:
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

    return insert(new_report)


def get_discussion(data):
    try:
        return Discussion.query.filter_by(
            Discussion_ID=data["discuss_id"]
        ).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def create_discussion(data):
    new_discussion = Discussion(
        Discussion_Title=data["title"],
        Main_Discussion=data["content"],
        User_ID=data["user_id"],
        Module_ID=data["mod_id"],
    )

    return insert(new_discussion)


def create_discus_thread(data):
    new_dthread = DiscussionThread(
        User_ID=data["user_id"],
        Discussion_ID=data["discuss_id"],
        Message=data["content"],
    )

    return insert(new_dthread)


# Flashcards

def get_flashcard_set(data):
    try:
        return FlashcardSet.query.filter_by(
            Set_ID=data["set_id"]
        ).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None

def get_flashcard(data):
    try:
        return Flashcard.query.filter_by(
            FC_ID = data["fc_id"]
        ).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None

def get_fcpref(data):
    try:
        return FC_Preference.query.filter_by(
            Student_ID = data["stud_id"],
            FC_ID = data["fc_id"],
        ).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None