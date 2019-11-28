# The data access layer

# Some of these methods could have been written in models
# but I wanted these separate. For better code organization.
from app.models import *
from app import db, flask_bcrypt
import sqlalchemy
from flask_login import current_user
from app.constants import *

from app.dac import general as gen_dac
from app.dac import exams as exam_dac


def get_module(mod_id):
    """

    :param mod_id: the id of the module you want to get
    :return: None if the modules does not exist, a Module model object otherwise
    """
    try:
        return Module.query.filter_by(Module_ID=mod_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def get_modules():
    try:
        return Module.query.all()
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

    return gen_dac.insert(new_module)


def get_progress(Module, stud_id):
    exams = Module.Exams.all()
    total = len(exams)
    taken = 0
    for exam in exams:
        if exam_dac.check_sub_exam(exam.Exam_ID, stud_id):
            taken += 1

    if total != 0:
        return (float(taken) / float(total)) * 100
    else:
        return 0.0


def get_tutor_module(tutor_id):
    try:
        return TutorModule.query.filter_by(Tutor_ID=tutor_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def assign_tutor_module(tutor_id, mod_id):
    new_tut_mod = TutorModule(
        Tutor_ID=tutor_id,
        Module_ID=mod_id
    )

    return gen_dac.insert(new_tut_mod)
