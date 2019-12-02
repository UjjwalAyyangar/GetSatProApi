# DATA ACCESS LAYER - EXAMS

from app.models import *
from app import db, flask_bcrypt
import sqlalchemy
from flask_login import current_user
from app.constants import *

from app.dac import general as gen_dac


def get_exam(id):
    """ Method for getting an exam by it's id

    :param id: integer :  id of the exam
    :return: Exam object if the Exam exists, None otherwise
    """
    try:
        # Querying the  Exam model/table by Exam ID and returning
        return Exam.query.filter_by(
            Exam_ID=id
        ).one()

    except sqlalchemy.orm.exc.NoResultFound:
        return None


def get_exams(mod_id=None):
    """ A method to get a list of all the exams available in a module/system

    :param mod_id: integer : the module id of the module whose exams need to be fetched. Optional. Default: None
    :return: a list of  Exam model/table object if query was successful, None otherwise
    """
    try:
        # checking if the exams of a specific module need to be fetched
        if mod_id:
            # querying the module model/table to find the module
            module = Module.query.filter_by(Module_ID=mod_id).one()
            # finding all the exams associated with the module
            exams = module.Exams.all()
            return exams
        else:
            # querying the module model/table to find all the modules
            modules = Module.query.all()
            exams = []
            for module in modules:
                # fetching all the exams associated with a module
                t_exams = module.Exams.all()
                exams.extend(t_exams)

            # returning list of exams
            return exams
    except:
        return None


def check_sub_exam(exam_id, stud_id=None):
    """ A method that is used to check if an exam has been submitted or not.

    :param exam_id: integer :  exam id of an exam
    :param stud_id: integer : user id of a student (optional)
    :return: True if the exam has been submitted by the user, False otherwise
    """
    if not stud_id:
        # getting student id from the logged in session if the client is a Student
        stud_id = current_user.User_ID

    # querying the AnswerSheet model/table to check if a student with the specified entry exists in it, and returning
    # the apt. bool value
    return db.session.query(
        StudentAnswerSheet.Exam_ID,
        StudentAnswerSheet.Student_ID).filter_by(
        Exam_ID=exam_id, Student_ID=stud_id).scalar() is not None


def create_exam(data):
    """ A method used to create an exam

    :param data:  a dictionary that contains the information about a new exam
    :return: None if there was trouble creating an exam, an exam model object otherwise
    """
    new_exam = Exam(
        Exam_Name=data[EXAM_NAME],
        Module_ID=data[MODULE_ID]
    )
    # insert created exam into database
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
            # creating a question object and adding it to the database
            _ = create_question(temp_data)

        return new_exam
    else:
        return None


def create_question(data):
    """ A method that is used to create a question in the database for an exam

    :param data: a dictionary that contains the information about a new question
    :return: None if there was trouble creating a question, a Question model object otherwise
    """

    options = data[QUESTION_OPTIONS]
    for i in range(4):
        try:
            access = options[i]
        except:
            options.append(None)

    new_question = ExamQuestion(
        Exam_ID=data[EXAM_ID],
        Question=data[QUESTION],
        Option_1=options[0],
        Option_2=options[1],
        Option_3=options[2],
        Option_4=options[3],
        Correct_ans=data[QUESTION_ANS]
    )

    # insert created question into database
    return gen_dac.insert(new_question)


def create_ans_sheet(data):
    """ A method that is used to create a student's answer sheet

    :param data: a dictionary that contains the information about a new answer sheet
    :return: None if there was trouble creating an answer sheet, a StudentAnswerSheet model object otherwise
    """
    new_ans_sheet = StudentAnswerSheet(
        Student_ID=data[STUDENT_ID],
        Exam_ID=data[EXAM_ID]
    )

    # insert created answer sheet into database
    return gen_dac.insert(new_ans_sheet)


def get_ans_sheet(data):
    """ A method used to fetch an answer sheet

    :param data: request data object sent by the client. Contains exam_id and student_id of required to fetch the
                answer sheet.
    :return: None if there was trouble finding the answer sheet in the model/table , a StudentAnswerSheet model object
            otherwise.
    """
    try:
        # querying the StudentAnswerSheet model/table for the answer sheet
        return StudentAnswerSheet.query.filter_by(
            Exam_ID=data[EXAM_ID],
            Student_ID=data[STUDENT_ID]
        ).one()

    # returning none if no result was found
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def create_ans(data, sheet=None):
    """ A method used for creating answer objects that are inserted into the database

    :param data: request object sent by the client containing - student_id, question_id and answer
    :param sheet: the sheet to which the answer belongs
    :return: None if there was trouble creating the answer in the model/table , an Answer model object
            otherwise.
    """
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
