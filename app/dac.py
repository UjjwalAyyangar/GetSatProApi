# The data access layer

# Some of these methods could have been written in models
# but I wanted these separate. For better code organization.
from app.models import *
from app import db, flask_bcrypt
import sqlalchemy
from flask_login import current_user
from app.constants import *


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


def get_user(uname=None, user_id=None):
    try:
        if uname:
            return UserInfo.query.filter_by(Username=uname).one()
        else:
            return UserInfo.query.filter_by(User_ID=user_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def get_users(role_id):
    try:
        return UserInfo.query.filter_by(Role_ID=role_id).all()
    except:
        return None


def create_user(data):
    """

    :param data: a dictionary that contains the information about a new user
    :return: None if there was trouble creating a user, a UserInfo model object otherwise
    """
    pwd = flask_bcrypt.generate_password_hash(data.get('password'))
    print(pwd)
    new_user = UserInfo(
        Username=data[USERNAME],
        Login_password=pwd,
        First_Name=data[USER_FNAME],
        Last_Name=data[USER_LNAME],
        Email=data[EMAIL],
        Phone=data[PHONE],
        Role_ID=int(data[ROLE_ID])
    )

    return insert(new_user)


def get_module(mod_id):
    """

    :param mod_id: the id of the module you want to get
    :return: None if the modules does not exist, a Module model object otherwise
    """
    try:
        return Module.query.filter_by(Module_ID=mod_id)
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def create_module(data):
    """

    :param data: a dictionary that contains the information about a new module
    :return: None if there was trouble creating a module, a Module model object otherwise
    """
    new_module = Module(
        Module_Name=data[MODULE_NAME]
    )

    return insert(new_module)


def get_exam(id):
    """

    :param id:
    :return:
    """
    try:
        return Exam.query.filter_by(
            Exam_ID=id
        ).one()

    except sqlalchemy.orm.exc.NoResultFound:
        return None


def get_exams(mod_id=None):
    try:
        if mod_id:
            module = Module.query.filter_by(Module_ID=mod_id).one()
            exams = module.Exams.all()
            return exams
        else:
            modules = Module.query.all()
            exams = []
            for module in modules:
                t_exams = module.Exams.all()
                exams.extend(t_exams)

            return exams
    except:
        return None


def create_exam(data):
    """

    :param data:  a dictionary that contains the information about a new exam
    :return: None if there was trouble creating an exam, an exam model object otherwise
    """
    new_exam = Exam(
        Exam_Name=data[EXAM_NAME],
        Module_ID=data[MODULE_ID]
    )

    new_exam = insert(new_exam)

    # add questions to the exam
    questions = data[QUESTIONS]

    if new_exam:
        for question in questions:
            temp_data = {
                EXAM_ID: new_exam.Exam_ID,
                QUESTION: question[QUESTION],
                QUESTION_OPTIONS: question[QUESTION_OPTIONS],
                QUESTION_ANS: question[QUESTION_ANS]
            }
            _ = create_question(temp_data)

        return new_exam
    else:
        return None


def create_question(data):
    """

    :param data: a dictionary that contains the information about a new question
    :return: None if there was trouble creating a question, a Question model object otherwise
    """
    new_question = ExamQuestion(
        Exam_ID=data[EXAM_ID],
        Question=data[QUESTION],
        Option_1=data[QUESTION_OPTIONS][0],
        Option_2=data[QUESTION_OPTIONS][1],
        Option_3=data[QUESTION_OPTIONS][2],
        Correct_ans=data[QUESTION_ANS]
    )

    return insert(new_question)


def create_ans_sheet(data):
    """

    :param data: a dictionary that contains the information about a new answer sheet
    :return:
    """
    new_ans_sheet = StudentAnswerSheet(
        Student_ID=data[STUDENT_ID],
        Exam_ID=data[EXAM_ID]
    )

    return insert(new_ans_sheet)


def create_ans(data, sheet=None):
    new_ans = UserAnswer(
        Student_ID=data[STUDENT_ID],
        Question_ID=data[QUESTION_ID],
        Ans=data[ANSWER]
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
        Student_ID=data[STUDENT_ID],
        Exam_ID=data[EXAM_ID],
        Sheet_ID=data[SHEET_ID],
        Grade=data[GRADE]
    )

    return insert(new_report)


def get_discussion(data):
    try:
        return Discussion.query.filter_by(
            Discussion_ID=data[DISCUSS_ID]
        ).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def create_discussion(data):
    new_discussion = Discussion(
        Discussion_Title=data[DISCUSS_TITLE],
        Main_Discussion=data[DISCUSS_MAIN],
        User_ID=data[USER_ID],
        Module_ID=data[MODULE_ID],
    )

    return insert(new_discussion)


def create_discus_thread(data):
    new_dthread = DiscussionThread(
        User_ID=data[USER_ID],
        Discussion_ID=data[DISCUSS_ID],
        Message=data[DISCUSS_CONTENT],
    )

    return insert(new_dthread)


# Flashcards

def get_flashcard_set(data):
    try:
        return FlashcardSet.query.filter_by(
            Set_ID=data[FLASHCARD_SET_ID]
        ).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def get_flashcard(data):
    try:
        return Flashcard.query.filter_by(
            FC_ID=data[FLASHCARD_ID]
        ).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def get_fcpref(data):
    try:
        return FC_Preference.query.filter_by(
            Student_ID=data[STUDENT_ID],
            FC_ID=data[FLASHCARD_ID],
        ).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None
