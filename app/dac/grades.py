# The data access layer

# Some of these methods could have been written in models
# but I wanted these separate. For better code organization.
from app.models import *
from app import db, flask_bcrypt
import sqlalchemy
from flask_login import current_user
from app.constants import *

from app.dac import general as gen_dac


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

    return gen_dac.insert(new_report)
