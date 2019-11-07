from app.models import *


def parse_ans(Submission):
    data = {}
    for ans in Submission:
        data[ans["ques_id"]] = ans["ans"]

    return data

def auto_grade(Exam, Submission):
    questions = Exam.Questions.all()
    total = 0
    count = 0
    parsed_ans = parse_ans(Submission)
    for question in questions:
        q_id = question.Question_ID
        total+=1
        cor_ans = question.Correct_ans
        user_ans = parsed_ans[q_id]

        if user_ans == cor_ans:
            count+=1

    grade = (float(count)/float(total)) * 100

    return grade
