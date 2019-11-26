# The data access layer

# Some of these methods could have been written in models
# but I wanted these separate. For better code organization.
from app.models import *
from app import db, flask_bcrypt
import sqlalchemy
from flask_login import current_user
from app.constants import *
from random import randint

from app.dac import modules as mod_dac
from app.dac import general as gen_dac


def get_all_sets(data):
    if MODULE_ID in data:
        module = mod_dac.get_module(data[MODULE_ID])
        sets = module.Sets.all()
    else:
        sets = FlashcardSet.query.all()

    if sets:
        return sets
    else:
        return None


# (stud_id,fc_id): is the key!
def get_flashcard_set(data):
    try:
        return FlashcardSet.query.filter_by(
            Set_ID=data[FLASHCARD_SET_ID]
        ).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def get_flashcard(data):
    try:
        return Flashcard.query.filter_by(
            FC_ID=data[FLASHCARD_ID]
        ).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def get_fc_pref_all(data):
    try:

        all_pref_cards = db.session.query(FC_Preference).join(Flashcard).filter(
            FC_Preference.FC_ID == Flashcard.FC_ID).filter(FC_Preference.Student_ID == data[STUDENT_ID]).filter(
            Flashcard.Set_ID == data[FLASHCARD_SET_ID])

        return all_pref_cards
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def get_progress(data):
    all_pref_cards = get_fc_pref_all({
        STUDENT_ID: data[STUDENT_ID],
        FLASHCARD_SET_ID: data[FLASHCARD_SET_ID]
    }).all()

    total = 0
    easy = 0
    for pref_card in all_pref_cards:
        if pref_card.Difficulty == 1:
            easy += 1
        total += 1

    prog = round((float(easy) / float(total)) * 100, 2)
    return prog


def get_fcpref(data):
    try:
        return FC_Preference.query.filter_by(
            Student_ID=data[STUDENT_ID],
            FC_ID=data[FLASHCARD_ID],
        ).one()
    except sqlalchemy.orm.exc.NoResultFound:
        new_fc_pref = FC_Preference(
            Student_ID=data[STUDENT_ID],
            FC_ID=data[FLASHCARD_ID]
        )
        return gen_dac.insert(new_fc_pref)


# move_down algorithm
def move_down(pref_card, pref):
    if pref == 1:  # Easy
        pref_card.Count -= 2
    else:
        pref_card.Count -= 1

    if pref_card.Count < 0:
        pref_card.Difficulty = max(1, pref_card.Difficulty - 1)
        pref_card.Count = 3 + pref_card.Count

    return pref_card


# move_up algorithm
def move_up(pref_card, pref):
    pref_card.Difficulty = pref
    pref_card.Count = 3
    return pref_card


# setting preferences
def set_pref(data, pref_card):
    fc_id = data[FLASHCARD_ID]

    pref = data[FLASHCARD_PREF]
    current_diff = pref_card.Difficulty

    if pref >= current_diff:
        pref_card = move_up(pref_card, pref)
    else:
        pref_card = move_down(pref_card, pref)

    # committing the changed pref_card
    db.session.commit()

    set_id = Flashcard.query.filter_by(FC_ID=fc_id).one().Set_ID

    next_card = get_next_flashcard(set_id, pref_card.Student_ID)
    next_card = Flashcard.query.filter_by(FC_ID=next_card.FC_ID).one()
    return next_card


def fc_pref_init(fc_id, stud_id):
    new_fc_pref = FC_Preference(
        Student_ID=stud_id,
        FC_ID=fc_id
    )
    return gen_dac.insert(new_fc_pref)


# Probabilistic fetch
def prob_fetch():
    # For probabilistic fetch
    score = 0
    # prob_arr = [20, 30, 50]
    # cum_arr = [20, 50, 100]
    easy, med, diff = [0, 0, 0]
    for trial in range(10):
        random_num = randint(0, 100)

        if 0 <= random_num <= 20:
            easy += 1
        elif 20 < random_num <= 50:
            med += 1
        else:
            diff += 1

    if diff > med and diff > easy:
        return 3
    elif easy > med and easy > diff:
        return 1
    elif med > easy and med > diff:
        return 2


# Get next flash card
def get_next_flashcard(set_id, stud_id):
    all_pref_cards = get_fc_pref_all({
        STUDENT_ID: stud_id,
        FLASHCARD_SET_ID: set_id
    }).all()

    pref_to_choose = prob_fetch()

    pref_cards = []
    for pref_card in all_pref_cards:
        if pref_card.Difficulty == pref_to_choose:
            pref_cards.append(pref_card)

    rest_cards = all_pref_cards
    # print(pref_cards)
    # print(rest_cards)
    if len(pref_cards) > 0:
        return pref_cards[randint(0, len(pref_cards) - 1)]
    else:
        return rest_cards[randint(0, len(rest_cards) - 1)]
    """

    print(cards)
    print(1 / 0)
    card = cards[randint(0, len(cards) - 1)]
    return card
    """


def reset_flashcard_set(data):
    try:
        pref_cards = get_fc_pref_all(data).all()
        for pref_card in pref_cards:
            pref_card.Difficulty = 2
            db.session.commit()

        return True
    except Exception as e:
        print(e)
        return False
