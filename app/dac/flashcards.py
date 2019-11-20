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

    next_card = get_next_flashcard(set_id)
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
def get_next_flashcard(set_id):
    fc_set = get_flashcard_set({
        FLASHCARD_SET_ID: set_id
    })
    if not fc_set:
        return None

    pref_to_choose = prob_fetch()

    cards = FC_Preference.query.filter_by(Difficulty=2).all()
    if len(cards) > 0:
        return cards[randint(0, len(cards) - 1)]
    else:
        return None
    """

    print(cards)
    print(1 / 0)
    card = cards[randint(0, len(cards) - 1)]
    return card
    """
