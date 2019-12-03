# DATA ACCESS LAYER - GENERAL

from app.models import *
from app import db, flask_bcrypt
import sqlalchemy
from flask_login import current_user
from app.constants import *
# from .general import *

from app.dac import modules as mod_dac
from app.dac import users as users_dac
from app.dac import exams as exams_dac
from app.dac import flashcards as fc_dac
from app.dac import discussions as disc_dac
from app.dac import files as files_dac
from app.dac import grades as grade_dac


def exists(name, obj, res):
    """
    :param name: string:  The name of the object - Discussion, Module, User, etc
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
    """ A method that is used to insert a field into it's relevant database model/table

    :param field: the object of the field that needs to be inserted

    :return: None if the field already exists, otherwise the field object
    """
    try:
        db.session.add(field)
        db.session.commit()
        return field
    except sqlalchemy.exc.IntegrityError as e:
        # returns none of there was trouble inserting the field
        return None


def delete(field):
    """ A method that is used to delete a field from it's respective model/table

    :param field: the object of the field that needs to be deleted
    :return: True if deletion was successful, False otherwise
    """
    try:
        db.session.delete(field)
        db.session.commit()
        return True
    except sqlalchemy.orm.exc.NoResultFound:
        return False


def delete_list(lis):
    try:
        for item in lis:
            db.session.delete(item)
            db.session.commit()
    except:
        return None


def del_exist_util(field):
    if not field:
        return True
    return False


def delete_user(field):
    try:

        if field.Role_ID == 1:
            user_id = field.User_ID

            # delete fc_preference table of that user
            fc_prefs = FC_Preference.query.filter_by(Student_ID=user_id).all()

            if fc_prefs:
                _ = delete_list(fc_prefs)

            # delete UserAnswers
            user_ans = UserAnswer.query.filter_by(Student_ID=user_id).all()
            if user_ans:
                _ = delete_list(user_ans)

            # delete Student answer sheets
            ans_sheets = StudentAnswerSheet.query.filter_by(Student_ID=user_id).all()
            if ans_sheets:
                _ = delete_list(ans_sheets)

            # delete Student report
            user_reports = StudentReport.query.filter_by(Student_ID=user_id).all()

            if user_reports:
                _ = delete_list(user_reports)

            # delete discussion reply
            del_threads = DiscussionThread.query.filter_by(User_ID=user_id).all()

            if del_threads:
                _ = delete_list(del_threads)

            # delete discussion
            del_discussions = Discussion.query.filter_by(User_ID=user_id).all()

            if del_discussions:

                # delete all replies from the user's discussion
                for discussion in del_discussions:
                    replies = discussion.Replies.all()
                    if replies:
                        _ = delete_list(replies)

                # delete discussions
                _ = delete_list(del_discussions)

            return delete(field)

        # delete tutor
        else:
            delete(field)


    except:
        return False


def del_discussion(field):
    try:
        # replies
        replies = field.Replies.all()
        if replies:
            _ = delete_list(replies)

        # return discussion
        return delete(field)
    except:
        return False


def del_exam(field):
    any_ans = StudentReport.query.filter_by(Exam_ID=field.Exam_ID).all()
    if any_ans:
        return False

    return delete(field)


def get_model_obj(model_name):
    """ A method that is used to return the model associated with the model_name

    :param model_name: string:  name of the model whose object you want
    :return: model object
    """
    model = {
        'Module': Module,
        'UserInfo': UserInfo,
        'UserRole': UserRole,
        'Discussion': Discussion,
        'D_thread': DiscussionThread,
        'Flashcard': Flashcard,
        'FlashcardSet': FlashcardSet,
        'File': File
    }

    return model[model_name]


def get_model_field(model_name, data):
    """ A method that is used to get a field from a specific model

    :param model_name: string: name of the module whose field you want
    :param data: dict: a dictionary containing details about the module whose field we want
    :return: respective module field, if found. None otherwise
    """
    if model_name == 'Module':
        return mod_dac.get_module(data)
    elif model_name == 'User':
        return users_dac.get_user(user_id=data)
    elif model_name == 'Discussion':
        return disc_dac.get_discussion(data)
    elif model_name == 'Exam':
        return exams_dac.get_exam(data)
    elif model_name == 'Flashcard_set':
        return fc_dac.get_flashcard_set(data)
    elif model_name == 'Flashcard':
        return fc_dac.get_flashcard(data)
    elif model_name == "Flashcard_pref":
        return fc_dac.get_fcpref(data)
    elif model_name == "File":
        return files_dac.get_file(data)
    else:
        return None


def get_progress(Module, stud_id):
    """ A method that is used to find the a student's progress in a module

    :param Module: Object of the module whose progress you want
    :param stud_id: user_id of the student
    :return:
    """
    exams = Module.Exams.all()
    total = len(exams)
    taken = 0
    # finding progress in the module's exams
    for exam in exams:
        # checking if the student has submitted the exam
        if exams_dac.check_sub_exam(exam.Exam_ID, stud_id):
            taken += 1

    # finding progress in the module's flashcards
    sets = FlashcardSet.query.filter_by(Module_ID=Module.Module_ID).all()
    flash_prog = 0.0
    for flash_set in sets:
        prog = fc_dac.get_progress({
            STUDENT_ID: stud_id,
            FLASHCARD_SET_ID: flash_set.Set_ID
        })
        flash_prog += prog

    flash_prog = float(flash_prog) / len(sets)

    print("total", total)
    # calculating the total progress
    if total != float(0):
        exam_prog = (float(taken) / float(total)) * 100
        total_prog = (exam_prog + flash_prog) / float(2)
        return round(total_prog, 2)
    else:
        return round(flash_prog, 2)
