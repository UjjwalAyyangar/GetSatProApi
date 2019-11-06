from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
#from sqlalchemy import create_engine
from app import engine, session, Base,login
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


# Permission
class Permission(Base):
    __tablename__ = "permission"
    Permission_ID = Column(Integer, primary_key=True)


class PermissionGroup(Base):
    __tablename__ = "permission_group"
    Group_ID = Column(Integer, primary_key=True)

    Permission_ID = Column(Integer, ForeignKey('permission.Permission_ID'))
    Permission = relationship(Permission)

    Group_Desc = Column(String(200), nullable=True)


# USER

class UserRole(Base):
    __tablename__ = "user_role"
    Role_ID = Column(Integer, primary_key=True)
    User_Type = Column(String(50))


class UserInfo(UserMixin, Base):
    __tablename__ = "user_info"
    User_ID = Column(Integer, primary_key=True)
    First_Name = Column(String(250), nullable=False)
    Last_Name = Column(String(250), nullable=False)
    Username = Column(String(250), nullable=False)
    Email = Column(String(400), nullable=False)
    Phone = Column(String(20), nullable=False)

    Role_ID = Column(Integer, ForeignKey('user_role.Role_ID'))
    UserRole = relationship(UserRole)
    Group_ID = Column(Integer, ForeignKey('permission_group.Permission_ID'))
    PermissionGroup = relationship(PermissionGroup)

    Last_Login = Column(DateTime, server_default=func.now())
    Login_password = Column(String(128))

    def set_password(self, password):
        self.Login_password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.Login_password_hash, password)

    @property
    def serialize(self):
        return {
            'FirstName': self.First_Name,
            'LastName': self.Last_Name,
            'userId': self.User_ID,
            'lastloggedIn': self.Last_Login
        }


# Used by the flask login to load the user
@login.user_loader
def load_user(id):
    user = session.query(UserInfo).filter_by(User_ID=int(id)).one()
    return user # Assuming it returns the user
# Module

class Submodule(Base):
    __tablename__ = "submodule"
    Submodule_ID = Column(Integer, primary_key=True)
    Submodule_name = Column(String(100), nullable=False)


class Module(Base):
    __tablename__ = "module"
    Module_ID = Column(Integer, primary_key=True)

    Submodule_ID = Column(Integer, ForeignKey('submodule.Submodule_ID'))
    Submodule = relationship(Submodule)

    Module_Name = Column(String(100), nullable=False)

    @property
    def serialize(self):
        return {
            'moduleName': self.Module_Name,
            'progress': 0
        }


# Exam

class ExamQuestion(Base):
    __tablename__ = 'exam_question'
    Question_ID = Column(Integer, primary_key=True)
    Question = Column(String(80))
    Option_1 = Column(Integer)
    Option_2 = Column(Integer)
    Option_3 = Column(Integer)


class Exam(Base):
    __tablename__ = "exam"
    Exam_ID = Column(Integer, primary_key=True)
    Exam_Name = Column(String(100), nullable=False)
    Question_Set = Column(Integer, ForeignKey('exam_question.Question_ID'))
    ExamQuestion = relationship(ExamQuestion)

    Published = Column(Integer)
    Expired = Column(Integer)

    Module_ID = Column(Integer, ForeignKey('module.Module_ID'))
    Module = relationship(Module)

    @property
    def serialize(self):
        return {
            "examName": self.Exam_Name,
            "examId": self.Exam_ID,
            "isCompleted": False
        }


# Report
class StudentReport(Base):
    __tablename__ = "student_report"

    Student_ID = Column(Integer, ForeignKey('user_info.User_ID'), primary_key=True)
    UserInfo = relationship(UserInfo)
    Exam_ID = Column(Integer, ForeignKey('exam.Exam_ID'), primary_key=True)
    Exam = relationship(Exam)

    Grade = Column(Integer)


# Flashcards

class Flashcards(Base):
    __tablename__ = "flashcards"
    FC_ID = Column(Integer, primary_key=True)
    Name = Column(String(100), nullable=False)
    Question = Column(String(100), nullable=False)
    Answer = Column(Integer, nullable=False)
    Module_ID = Column(Integer, ForeignKey('module.Module_ID'))
    Module = relationship(Module)
    Submodule_ID = Column(Integer, ForeignKey('submodule.Submodule_ID'))
    Submodule = relationship(Submodule)

    @property
    def serialize(self):
        return {
            'flashcardId': self.FC_ID,
            'flashcardFront': self.Question,
            'flashcardBack': self.Answer
        }


# Hard easy and medium?
class FC_Category(Base):
    __tablename__ = "fc_category"
    Category_ID = Column(Integer, primary_key=True)
    Category_Name = Column(String(100), nullable=False)


class FC_Preference(Base):
    __tablename__ = "fc_preference"
    Student_ID = Column(Integer, ForeignKey('user_info.User_ID'), primary_key=True)
    UserInfo = relationship(UserInfo)
    FC_ID = Column(Integer, ForeignKey('flashcards.FC_ID'), primary_key=True)
    Flashcards = relationship(Flashcards)
    Category_ID = Column(Integer, ForeignKey('fc_category.Category_ID'), primary_key=True)
    FC_Category = relationship(FC_Category)


# Discussion
class Discussion(Base):
    __tablename__ = "discussion"
    Discussion_ID = Column(Integer, primary_key=True)
    Main_Discussion = Column(String(1000), nullable=False)
    User_ID = Column(Integer, ForeignKey('user_info.User_ID'))
    UserInfo = relationship(UserInfo)
    Module_ID = Column(Integer, ForeignKey('module.Module_ID'))
    Module = relationship(Module)

    Time = Column(DateTime, server_default=func.now())

    @property
    def serialize(self):
        return {
            'discussionId': self.Discussion_ID,
        }


class DiscussionThread(Base):
    __tablename__ = "discussion_thread"
    Thread_ID = Column(Integer, primary_key=True)
    Discussion_ID = Column(Integer, ForeignKey('discussion.Discussion_ID'))
    Discussion = relationship(Discussion)
    User_ID = Column(Integer, ForeignKey('user_info.User_ID'))
    UserInfo = relationship(UserInfo)
    Message = Column(String(10000), nullable=False)

    Time = Column(DateTime, server_default=func.now())

    @property
    def serialize(self):
        return {
            'threadId': self.Thread_ID,
            'threadContent': self.Message,
            'createdBy': UserInfo.Username,
        }


#engine = create_engine('sqlite:///getSatPro.db')
Base.metadata.create_all(engine)
