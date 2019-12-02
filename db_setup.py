from app.models import *
from app import db
from app.dac import users as users_dac
from app.dac import general as gen_dac
from app.dac import modules as mod_dac
from app.dac import exams as exams_dac
from app.dac import grades as grades_dac
from app.dac import discussions as discuss_dac
from flask_bcrypt import generate_password_hash
from app.constants import *
from app.system import *
from sys import exit


def add_fields(fields):
    for field in fields:
        db.session.add(field)
        db.session.commit()


# UserRole
Student_Role = UserRole(User_Type='Student')
Tutor_Role = UserRole(User_Type='Tutor')
Admin_Role = UserRole(User_Type='Admin')

# Users

# Student


# def setup():
add_fields([Student_Role, Tutor_Role, Admin_Role])

# Add sample users

# Students
aarohi_data = {
    USERNAME: "aarohi",
    USER_FNAME: "Aarohi",
    USER_LNAME: "Mehta",
    USER_PWD: "aMehta",
    EMAIL: "amehta@umd.edu",
    PHONE: "206-591-8211",
    ROLE_ID: 1
}
aarohi = users_dac.create_user(aarohi_data)
db.session.add(aarohi)
db.session.commit()
users_dac.setup_pref(aarohi)

nithin_data = {
    USERNAME: "nithin",
    USER_FNAME: "Nithin",
    USER_LNAME: "Abraham",
    USER_PWD: "nAbraham",
    EMAIL: "nithinsa@umd.edu",
    PHONE: "206-591-8212",
    ROLE_ID: 1
}
nithin = users_dac.create_user(nithin_data)
db.session.add(nithin)
db.session.commit()
users_dac.setup_pref(nithin)

david_data = {
    USERNAME: "david",
    USER_FNAME: "David",
    USER_LNAME: "Foerester",
    USER_PWD: "dFoerester",
    EMAIL: "david@umd.edu",
    PHONE: "206-591-8213",
    ROLE_ID: 1
}
david = users_dac.create_user(david_data)
db.session.add(david)
db.session.commit()
users_dac.setup_pref(david)

# Tutors
annu_data = {
    USERNAME: "annu",
    USER_FNAME: "Annu",
    USER_LNAME: "Abraham",
    USER_PWD: "aAbraham",
    EMAIL: "nueliza@umd.edu",
    PHONE: "206-591-8214",
    ROLE_ID: 2
}
annu = users_dac.create_user(annu_data)
db.session.add(annu)
db.session.commit()

kuntal_data = {
    USERNAME: "kuntal",
    USER_FNAME: "Kuntal",
    USER_LNAME: "Saxena",
    USER_PWD: "kSaxena",
    EMAIL: "ksaxena@umd.edu",
    PHONE: "206-591-8215",
    ROLE_ID: 2
}
kuntal = users_dac.create_user(kuntal_data)
db.session.add(kuntal)
db.session.commit()

# Admin
ujjwal_data = {
    USERNAME: "ujjwal",
    USER_FNAME: "Ujjwal",
    USER_LNAME: "Ayyangar",
    USER_PWD: "uAyyangar",
    EMAIL: "ayyangar@umd.edu",
    PHONE: "206-591-8216",
    ROLE_ID: 3,
    SECURITY_PWD: "security"
}

ujjwal = users_dac.create_user(ujjwal_data)
# db.session.add(ujjwal)
# db.session.commit()

# Modules

# Math module
math_data = {
    MODULE_NAME: "Math"
}
math = mod_dac.create_module(math_data)
db.session.add(math)
db.session.commit()

# English module
eng_data = {
    MODULE_NAME: "English"
}
eng = mod_dac.create_module(eng_data)
db.session.add(eng)
db.session.commit()
# Assigning Tutors to Modules
# Kuntal = Math
assign_kuntal = mod_dac.assign_tutor_module(5, 1)
db.session.add(assign_kuntal)
db.session.commit()
# Annu = English
assign_annu = mod_dac.assign_tutor_module(4, 2)
db.session.add(assign_annu)
db.session.commit()

"""
# Creating Exams. 2 in English. 2 in Maths

# Math Exams

# Algebra exam

# algebra exam questions
"""
algebra_ques_1 = {
    EXAM_ID: 1,
    QUESTION: "What is the value of a in, a + 5 = 7 ?",
    QUESTION_ANS: "-2",
    QUESTION_OPTIONS: ["1", "5", "-2", "-8"],
}

algebra_ques_2 = {
    EXAM_ID: 1,
    QUESTION: "What is the value of x in, a x 9 = 81 ?",
    QUESTION_ANS: "9",
    QUESTION_OPTIONS: ["1", "9", "-2", "-8"],
}

algebra_data = {
    EXAM_NAME: "Algebra",
    MODULE_ID: 1,
    QUESTIONS: [algebra_ques_1, algebra_ques_2]
}

algebra_exam = exams_dac.create_exam(algebra_data)
db.session.add(algebra_exam)
db.session.commit()

# Geometry exam


# geometry exam questions
geom_ques_1 = {
    EXAM_ID: 2,
    QUESTION: "How many sides are there in a Circle ?",
    QUESTION_ANS: "0",
    QUESTION_OPTIONS: ["0", "4", "12", "3"],
}

geom_ques_2 = {
    EXAM_ID: 2,
    QUESTION: "What is the area of a rectangle ?",
    QUESTION_ANS: "L X B",
    QUESTION_OPTIONS: ["S X S", "L X B", "L X B X H", "(1/2) X B X H"],
}

geometry_data = {
    EXAM_NAME: "Geometry",
    MODULE_ID: 1,
    QUESTIONS: [geom_ques_1, geom_ques_2]
}

geo_exam = exams_dac.create_exam(geometry_data)
db.session.add(geo_exam)
db.session.commit()
"""

# English exams

# Vocab1

vocab1_ques_1 = {
    EXAM_ID: 3,
    QUESTION: "A certain bookstore sells only paperbacks and hardbacks."
              "Each of the 200 paperbacks in stock sells for a price between $8"
              "and $12, and each of the 100 hardbacks in stock sells for a price between $14"
              "and $18. Quantity A : The average price of the books in stock at the bookstore."
              "Quantity B: $9.99",
    QUESTION_ANS: "Quantity A is greater",
    QUESTION_OPTIONS: ["Quantity A is greater", "Quantity B is greater", "The two quantitities are equal", "The relationship cannot be determined from the given information"],
}

vocab1_ques_2 = {
    EXAM_ID: 3,
    QUESTION: "What is the meaning of erudite?",
    QUESTION_ANS: "having or showing great knowledge",
    QUESTION_OPTIONS: ["having or showing great knowledge", "difficult", "hard working", "sleeping"],
}

vocab1_data = {
    EXAM_NAME: "Vocab - 1",
    MODULE_ID: 2,
    QUESTIONS: [vocab1_ques_1, vocab1_ques_2]
}
vocab1_exam = exams_dac.create_exam(vocab1_data)
db.session.add(vocab1_exam)
db.session.commit()

# Vocab2

vocab2_ques_1 = {
    EXAM_ID: 4,
    QUESTION: "What is the meaning of assuage?",
    QUESTION_ANS: "to make something less intense",
    QUESTION_OPTIONS: ["to play", "to make something less intense", "to persuade", "to run"],
}

vocab2_ques_2 = {
    EXAM_ID: 4,
    QUESTION: "What is the meaning of prodigal?",
    QUESTION_ANS: "wastefully extravagant",
    QUESTION_OPTIONS: ["Hero", "foolish", "Villain", "wastefully extravagant"],
}

vocab2_data = {
    EXAM_NAME: "Vocab -2",
    MODULE_ID: 2,
    QUESTIONS: [vocab2_ques_1, vocab2_ques_2]
}
vocab2_exam = exams_dac.create_exam(vocab2_data)
db.session.add(vocab2_exam)
db.session.commit()

# Making Nithin submit Exam 1
answers = []
answers.append(
    {
        QUESTION_ID: 1,
        ANSWER: "-2"
    })

answers.append(
    {
        QUESTION_ID: 2,
        ANSWER: "9"
    })

exam = exams_dac.get_exam(1)
grade = auto_grade(exam, answers)
nithin_ans_sheet = exams_dac.create_ans_sheet({
    STUDENT_ID: 2,
    EXAM_ID: 1
})
db.session.add(nithin_ans_sheet)
db.session.commit()

for ans in answers:
    new_ans = exams_dac.create_ans({
        STUDENT_ID: 2,
        QUESTION_ID: ans[QUESTION_ID],
        ANSWER: ans[ANSWER]
    }, sheet=nithin_ans_sheet)
    db.session.add(new_ans)
    db.session.commit()

nithin_report = grades_dac.create_report({
    STUDENT_ID: 2,
    EXAM_ID: 1,
    SHEET_ID: 1,
    GRADE: grade
})
db.session.add(nithin_report)
db.session.commit()

# Creating a sample discussion
disc_data = {
    DISCUSS_TITLE: "Welcome",
    DISCUSS_MAIN: "Welcome to GetSatPro! Hope you have a great time learning.",
    USER_ID: 6,
    MODULE_ID: 1
}
new_discussion = discuss_dac.create_discussion(disc_data)
db.session.add(new_discussion)
db.session.commit()

# Creating a reply to that discussion
reply_data = {
    USER_ID: "2",
    DISCUSS_ID: 1,
    DISCUSS_CONTENT: "Thanks!"
}
new_reply = discuss_dac.create_discus_thread(reply_data)
db.session.add(new_reply)
db.session.commit()
"""
