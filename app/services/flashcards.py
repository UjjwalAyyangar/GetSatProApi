from flask import Blueprint, jsonify
from flask import abort, request
from app.system import *
from app.constants import *

from app.dac import flashcards as fc_dac

from flask_login import current_user
from app import app
from flask_jwt_extended import (
    jwt_required,

)
from flask_cors import cross_origin

mod = Blueprint('flashcards', __name__, url_prefix='/api')


# Flashcard
@mod.route('/view_flashcard_sets', methods=["GET", "POST"])
@cross_origin(origins=['https://get-sat-pro-client.herokuapp.com', 'localhost'],
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@authenticated
def api_view_sets():
    data = request.get_json()
    sets = fc_dac.get_all_sets(data)
    if not sets:
        return ErrorResponse(404), 404

    set_arr = []
    for fc_set in sets:
        temp = {
            FLASHCARD_SET_ID: fc_set.Set_ID,
            FLASHCARD_SET_NAME: fc_set.Set_Name,
            MODULE_ID: fc_set.Module_ID,
        }
        set_arr.append(temp)

    res = Response(200, "Successfully fetched all the sets").content()
    res[FLASHCARD_SET_LIST] = set_arr

    return res, 200


@mod.route('/view_flashcard_set', methods=["POST"])
@cross_origin(origins=['https://get-sat-pro-client.herokuapp.com', 'localhost'],
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@authenticated
def api_view_set():
    # Gives you the first card from the set
    data = request.get_json()
    set_id = data[FLASHCARD_SET_ID]
    fc_set = fc_dac.get_flashcard_set({
        FLASHCARD_SET_ID: set_id
    })

    print(fc_set)

    if not fc_set:
        return ErrorResponse(404).content(), 400

    first_card = fc_set.Flashcards.first()
    card_data = {
        FLASHCARD_SET_ID: first_card.Set_ID,
        FLASHCARD_QUESTION: first_card.Question,
        FLASHCARD_ANSWER: first_card.Answer,
        FLASHCARD_ID: first_card.FC_ID
    }

    res = Response(200, "Successfully fetched the first card").content()
    res[FLASHCARD_DATA] = card_data

    if is_User("Student") == 200:
        res[FLASHCARD_PROGRESS] = fc_dac.get_progress({
            STUDENT_ID: current_user.User_ID,
            FLASHCARD_SET_ID: set_id
        })

    return res, 200


@mod.route('/set_pref', methods=["POST"])
@cross_origin(origins=['https://get-sat-pro-client.herokuapp.com', 'localhost'],
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@is_student
def api_set_pref():
    data = request.get_json()
    fc_pref = fc_dac.get_fcpref({
        STUDENT_ID: current_user.User_ID,
        FLASHCARD_ID: data[FLASHCARD_ID]
    })

    if fc_pref:
        next_card = fc_dac.set_pref({
            FLASHCARD_ID: data[FLASHCARD_ID],
            FLASHCARD_PREF: data[FLASHCARD_PREF]
        }, fc_pref)

        if not next_card:
            return None

        next_card_data = {
            FLASHCARD_SET_ID: next_card.Set_ID,
            FLASHCARD_QUESTION: next_card.Question,
            FLASHCARD_ANSWER: next_card.Answer,
            FLASHCARD_ID: next_card.FC_ID
        }

        ret = Response(
            200,
            "Preference set succesfully"
        ).content()

        ret[FLASHCARD_DATA] = next_card_data
        ret[FLASHCARD_PROGRESS] = fc_dac.get_progress({
            STUDENT_ID: current_user.User_ID,
            FLASHCARD_SET_ID: next_card.Set_ID
        })

        return ret, 200
    else:
        return ErrorResponse(400).content(), 400
