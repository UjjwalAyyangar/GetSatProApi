import csv

from app.dac import flashcards as fs_dac
from app.dac import general as gen_dac
from app.models import Flashcard, FlashcardSet
from app import db


def insert_flashcard(question, answer, set_id):
    new_card = Flashcard(
        Set_ID=set_id,
        Question=question,
        Answer=answer
    )
    db.session.add(new_card)
    db.session.commit()


def english_cards(fname, set_name):
    new_set = FlashcardSet(
        Set_Name=set_name,
        Module_ID=2,
    )

    db.session.add(new_set)
    db.session.commit()

    with open(fname, 'r', encoding='UTF8') as f:
        readCsv = csv.reader(f, delimiter=',')
        next(readCsv)
        next(readCsv)
        rows = []
        for row in readCsv:
            print(row)

            if len(row) == 0:
                continue

            question = row[0]
            if question == "Front of Card":
                continue

            answer = row[1] + "\n" + row[2]
            insert_flashcard(question, answer, new_set.Set_ID)


def math_cards(fname, set_name):
    new_set = FlashcardSet(
        Set_Name=set_name,
        Module_ID=1,
    )

    db.session.add(new_set)
    db.session.commit()

    with open(fname, 'r', encoding='UTF8') as f:
        readCsv = csv.reader(f, delimiter=',')
        next(readCsv)
        next(readCsv)
        rows = []
        for row in readCsv[1:]:
            if len(row) == 0:
                continue

            question = row[0]
            if question == "Front of Card":
                continue

            answer = row[1]
            insert_flashcard(question, answer, new_set.Set_ID)


def insert_english_cards():
    files = ["af_sheet1.csv", "gl_sheet1.csv", "mr_sheet1.csv", "sz_sheet1.csv"]
    for f in files:
        set_name = f[:2].upper() + "- Set"
        english_cards(f, set_name)


def insert_math_cards():
    files = ["foundation_sheet1.csv", "geo_sheet1.csv", "trigno_sheet1.csv"]
    for f in files:
        set_name = f[:-11].upper() + "- Set"
        math_cards(f, set_name)


# English

insert_english_cards()
