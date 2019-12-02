# DATA ACCESS LAYER - GRADES

from app.models import *
from app import db, flask_bcrypt
import sqlalchemy
from flask_login import current_user
from app.constants import *

from app.dac import general as gen_dac


def get_report(student_id, exam_id):
    """
    :param student_id: integer: id of the student
    :param exam_id: integer: id of the exam whose report you want
    :return: StudentReport if query was successful, None otherwise
    """
    try:
        return StudentReport.query.filter_by(
            Student_ID=student_id,
            Exam_ID=exam_id
        ).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def create_report(data):
    """ A method that is used to create student report

    :param data: dict : contains :
                    - student_id : integer: user_id of the student
                    - exam_id : integer: exam id of an exam
                    - sheet_id : integer: id of the sheet
                    - grade : float: grade in the exam

    :return: StudentReport model object if successful, None otherwise
    """
    new_report = StudentReport(
        Student_ID=data[STUDENT_ID],
        Exam_ID=data[EXAM_ID],
        Sheet_ID=data[SHEET_ID],
        Grade=data[GRADE]
    )

    return gen_dac.insert(new_report)
