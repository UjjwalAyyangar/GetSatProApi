from app.models import *
from app import db

def add_fields(fields):
    for field in fields:
        db.session.add(field)
        db.session.commit()


# UserRole
Student_Role = UserRole(User_Type='Student')
Tutor_Role = UserRole(User_Type='Tutor')
Admin_Role = UserRole(User_Type='Admin')

add_fields([Student_Role, Tutor_Role, Admin_Role])
