from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship
# from sqlalchemy import create_engine
from app import db, login
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class relationship():

    def __init__(self):
        pass

    def one_to_one(self, from_Model, to_Model):
        return db.relationship(to_Model,
                               backref=from_Model,
                               lazy='dynamic',
                               #uselist=False
                               )

        return temp

    def one_to_many(self, from_Model, to_Model):
        print(from_Model,to_Model)
        return db.relationship(to_Model,
                               backref=from_Model,
                               lazy='dynamic',
                               #uselist=False
                               )


rel_obj = relationship()


# USER

class UserRole(db.Model):
    Role_ID = Column(Integer, primary_key=True)
    User_Type = Column(String(50))
    UserInfo = rel_obj.one_to_many('UserRole', 'UserInfo')  # A user role can point to many users


class UserInfo(UserMixin, db.Model):
    User_ID = Column(Integer, primary_key=True)
    First_Name = Column(String(250), nullable=False)
    Last_Name = Column(String(250), nullable=False)
    Username = Column(String(250), nullable=False)
    Email = Column(String(400), nullable=False)
    Phone = Column(String(20), nullable=False)

    Role_ID = Column(Integer, db.ForeignKey('user_role.Role_ID'))

    Reports = rel_obj.one_to_many('UserInfo', 'StudentReport')  # 1 Student will have many reports
    Pref_table = rel_obj.one_to_one('UserInfo', 'FC_Preference')  # 1 student has 1 pref table
    Discussions = rel_obj.one_to_many('UserInfo', 'Discussion')  # 1 user can have many discussions
    Replies = rel_obj.one_to_many('UserInfo', 'DiscussionThread')  # 1 user can have many replies

    Last_Login = Column(DateTime, server_default=func.now())
    Login_password = Column(String(128))

    def set_password(self, password):
        self.Login_password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.Login_password_hash, password)


# Used by the flask login to load the user
@login.user_loader
def load_user(id):
    user = session.query(UserInfo).filter_by(User_ID=int(id)).one()
    return user  # Assuming it returns the user


# Module


class Module(db.Model):
    # __tablename__ = "module"
    Module_ID = Column(Integer, primary_key=True)
    Module_Name = Column(String(100), nullable=False)

    Exams = rel_obj.one_to_many('Module', 'Exam')  # 1 module will have many exams
    Flashcards = rel_obj.one_to_many('Module', 'FlashcardSet')  # 1 module will have many flashcards


# Exam

class ExamQuestion(db.Model):
    Question_ID = Column(Integer, primary_key=True)
    Question = Column(String(80))
    Option_1 = Column(Integer)
    Option_2 = Column(Integer)
    Option_3 = Column(Integer)
    Correct_ans = Column(Integer)
    Exam_ID = Column(Integer, db.ForeignKey('exam.Exam_ID'))


class Exam(db.Model):
    Exam_ID = Column(Integer, primary_key=True)
    Exam_Name = Column(String(100), nullable=False)

    Questions = rel_obj.one_to_many('Exam', 'ExamQuestion')  # 1 exam has many questions
    Published = Column(Integer)
    Expired = Column(Integer)

    Module_ID = Column(Integer, db.ForeignKey('module.Module_ID'))

    Reports = rel_obj.one_to_many('Exam', 'StudentReport')  # 1 exam will have many reports


# Report
class StudentReport(db.Model):
    Student_ID = Column(Integer, db.ForeignKey('user_info.User_ID'), primary_key=True)
    Exam_ID = Column(Integer, db.ForeignKey('exam.Exam_ID'), primary_key=True)
    Grade = Column(Integer)


# class StudentAnswerSheet(db.Model):
#    Student_ID = Column(Integer, db.ForeignKey('user_info.User_ID'), primary_key=True)
# UserInfo = relationship(UserInfo)
#    Exam_ID = Column(Integer, db.ForeignKey('exam.Exam_ID'), primary_key=True)


# Flashcards
class FlashcardSet(db.Model):
    Set_ID = Column(Integer, primary_key=True)
    Set_Name = Column(String(100), nullable=False)
    Module_ID = Column(Integer, db.ForeignKey('module.Module_ID'))
    Flashcards = rel_obj.one_to_many('FlashcardSet', 'Flashcard')  # 1 set has many cards


class Flashcard(db.Model):
    FC_ID = Column(Integer, primary_key=True)
    Set_Id = Column(Integer, db.ForeignKey('flashcard_set.Set_ID'))
    Question = Column(String(100), nullable=False)
    Answer = Column(Integer, nullable=False)


class FC_Preference(db.Model):
    Student_ID = Column(Integer, db.ForeignKey('user_info.User_ID'), primary_key=True)
    FC_ID = Column(Integer, db.ForeignKey('flashcard.FC_ID'), primary_key=True)
    Category_Name = Column(String(100), nullable=False)


# Discussion
class Discussion(db.Model):
    Discussion_ID = Column(Integer, primary_key=True)
    Main_Discussion = Column(String(1000), nullable=False)
    User_ID = Column(Integer, db.ForeignKey('user_info.User_ID'))
    Module_ID = Column(Integer, db.ForeignKey('module.Module_ID'))

    Replies = rel_obj.one_to_many('Discussion', 'DiscussionThread')  # 1 discussion can have many replies

    Time = Column(DateTime, server_default=func.now())


class DiscussionThread(db.Model):
    Thread_ID = Column(Integer, primary_key=True)
    Discussion_ID = Column(Integer, db.ForeignKey('discussion.Discussion_ID'))
    User_ID = Column(Integer, db.ForeignKey('user_info.User_ID'))
    Message = Column(String(10000), nullable=False)
    Time = Column(DateTime, server_default=func.now())


# engine = create_engine('sqlite:///getSatPro.db')
# Base.metadata.create_all(engine)
db.create_all()
