from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship
# from sqlalchemy import create_engine
from datetime import timedelta, datetime
from app import db, login
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash


class relationship():

    def __init__(self):
        pass

    def one_to_one(self, from_Model, to_Model):
        return db.relationship(to_Model,
                               backref=from_Model,
                               lazy='dynamic',
                               # uselist=False
                               )

        return temp

    def one_to_many(self, from_Model, to_Model):
        print(from_Model, to_Model)
        return db.relationship(to_Model,
                               backref=from_Model,
                               lazy='dynamic',
                               # uselist=False
                               )


rel_obj = relationship()


# USER

class UserRole(db.Model):
    Role_ID = Column(Integer, primary_key=True)
    User_Type = Column(String(50), unique=True)
    UserInfo = rel_obj.one_to_many('UserRole', 'UserInfo')  # A user role can point to many users


class UserInfo(UserMixin, db.Model):
    User_ID = Column(Integer, primary_key=True)
    First_Name = Column(String(250), nullable=False)
    Last_Name = Column(String(250), nullable=False)
    Username = Column(String(250), nullable=False, unique=True)
    Email = Column(String(400), nullable=False, unique=True)
    Phone = Column(String(20), nullable=False, unique=True)

    Role_ID = Column(Integer, db.ForeignKey('user_role.Role_ID'))

    Reports = rel_obj.one_to_many('UserInfo', 'StudentReport')  # 1 Student will have many reports
    Pref_table = rel_obj.one_to_one('UserInfo', 'FC_Preference')  # 1 student has 1 pref table
    Discussions = rel_obj.one_to_many('UserInfo', 'Discussion')  # 1 user can have many discussions
    Replies = rel_obj.one_to_many('UserInfo', 'DiscussionThread')  # 1 user can have many replies

    Last_Login = Column(db.DateTime, default=datetime.now())
    Login_password = Column(String(128), nullable=False)
    Security_password = Column(String(128), nullable=True)

    def get_id(self):
        return self.User_ID

    def set_password(self, password):
        self.Login_password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.Login_password_hash, password)


# Used by the flask login to load the user
"""
@login.user_loader
def load_user(id):
    user = session.query(UserInfo).filter_by(User_ID=int(id)).one()
    return user  # Assuming it returns the user
"""


# Module


class Module(db.Model):
    # __tablename__ = "module"
    Module_ID = Column(Integer, primary_key=True)
    Module_Name = Column(String(100), nullable=False, unique=True)

    Exams = rel_obj.one_to_many('Module', 'Exam')  # 1 module will have many exams
    Flashcards = rel_obj.one_to_many('Module', 'FlashcardSet')  # 1 module will have many flashcards


# Exam

class ExamQuestion(db.Model):
    Question_ID = Column(Integer, primary_key=True)
    Question = Column(String(80))
    # I think our db should just have the correct ans field
    Option_1 = Column(String(100))
    Option_2 = Column(String(100))
    Option_3 = Column(String(100))
    Option_4 = Column(String(100))
    Correct_ans = Column(Integer, nullable=False)
    Exam_ID = Column(Integer, db.ForeignKey('exam.Exam_ID'))


class Exam(db.Model):
    Exam_ID = Column(Integer, primary_key=True)
    Exam_Name = Column(String(100), nullable=False)

    Questions = rel_obj.one_to_many('Exam', 'ExamQuestion')  # 1 exam has many questions
    Published = Column(db.DateTime, default=datetime.now())
    Expired = Column(db.DateTime, default=datetime.now() + timedelta(hours=24))

    Module_ID = Column(Integer, db.ForeignKey('module.Module_ID'))

    Reports = rel_obj.one_to_many('Exam', 'StudentReport')  # 1 exam will have many reports


"""
{
  "exam": [
    {
      "correctAnswer": "Second Option",
      "Question": "This is the first question",
      "options": [
        "First option",
        "Second Option",
        "Third Option"
      ]
    },
    {
      "correctAnswer": "First Option",
      "Question": "This is the first question",
      "options": [
        "First option",
        "Second Option",
        "Third Option"
      ]
    }
  ]
}

"""


# Report
class StudentReport(db.Model):
    Student_ID = Column(Integer, db.ForeignKey('user_info.User_ID'), primary_key=True)
    Exam_ID = Column(Integer, db.ForeignKey('exam.Exam_ID'), primary_key=True)
    Sheet_ID = Column(Integer, db.ForeignKey('student_answer_sheet.Sheet_ID'))
    Grade = Column(Float)


class StudentAnswerSheet(db.Model):
    Sheet_ID = Column(Integer, primary_key=True)
    Student_ID = Column(Integer, db.ForeignKey('user_info.User_ID'))
    Exam_ID = Column(Integer, db.ForeignKey('exam.Exam_ID'))
    Answers = rel_obj.one_to_many('StudentAnswerSheet', 'UserAnswer')


class UserAnswer(db.Model):
    # Answer_ID = db.Model(Integer, primary_key=True)
    Sheet_ID = Column(Integer, db.ForeignKey('student_answer_sheet.Sheet_ID'))
    Student_ID = Column(Integer, db.ForeignKey('user_info.User_ID'), primary_key=True)
    Question_ID = Column(Integer, db.ForeignKey('exam_question.Question_ID'), primary_key=True)
    Ans = Column(Integer, nullable=False)


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
    Difficulty = Column(Integer, default=2)


# Discussion
class Discussion(db.Model):
    Discussion_ID = Column(Integer, primary_key=True)
    Discussion_Title = Column(String(100), default="")
    Main_Discussion = Column(String(1000), nullable=False)
    User_ID = Column(Integer, db.ForeignKey('user_info.User_ID'))
    Module_ID = Column(Integer, db.ForeignKey('module.Module_ID'))

    Replies = rel_obj.one_to_many('Discussion', 'DiscussionThread')  # 1 discussion can have many replies

    Time = Column(DateTime, default=datetime.now())


class DiscussionThread(db.Model):
    Thread_ID = Column(Integer, primary_key=True)
    Discussion_ID = Column(Integer, db.ForeignKey('discussion.Discussion_ID'))
    User_ID = Column(Integer, db.ForeignKey('user_info.User_ID'))
    Message = Column(String(10000), nullable=False)
    Time = Column(DateTime, default=datetime.now())

# engine = create_engine('sqlite:///getSatPro.db')
# Base.metadata.create_all(engine)
# db.create_all()
