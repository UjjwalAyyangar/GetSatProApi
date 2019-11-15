# The data access layer

# Some of these methods could have been written in models
# but I wanted these separate. For better code organization.
from app.models import *
from app import db, flask_bcrypt
import sqlalchemy
from flask_login import current_user
from app.constants import *

from app.dac import general as gen_dac


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


def check_sub_exam(exam_id, stud_id=None):
    if not stud_id:
        stud_id = current_user.User_ID
    return db.session.query(
        StudentAnswerSheet.Exam_ID,
        StudentAnswerSheet.Student_ID).filter_by(
        Exam_ID=exam_id, Student_ID=stud_id).scalar() is not None


def create_exam(data):
    """

    :param data:  a dictionary that contains the information about a new exam
    :return: None if there was trouble creating an exam, an exam model object otherwise
    """
    new_exam = Exam(
        Exam_Name=data[EXAM_NAME],
        Module_ID=data[MODULE_ID]
    )

    new_exam = gen_dac.insert(new_exam)

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

    return gen_dac.insert(new_question)


def create_ans_sheet(data):
    """

    :param data: a dictionary that contains the information about a new answer sheet
    :return:
    """
    new_ans_sheet = StudentAnswerSheet(
        Student_ID=data[STUDENT_ID],
        Exam_ID=data[EXAM_ID]
    )

    return gen_dac.insert(new_ans_sheet)


def create_ans(data, sheet=None):
    new_ans = UserAnswer(
        Student_ID=data[STUDENT_ID],
        Question_ID=data[QUESTION_ID],
        Ans=data[ANSWER]
    )
    if sheet:
        sheet.Answers.append(new_ans)
    else:
        new_ans = gen_dac.insert(new_ans)

    return new_ans
