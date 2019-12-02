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
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@authenticated
def api_view_sets():
    """ API endpoint for viewing flashcard sets available in the system
    :return: JSON response containing details about existing flashcard sets
    """
    data = request.get_json()

    # getting al the the flashcards sets objects from the database
    sets = fc_dac.get_all_sets(data)
    if not sets:
        return ErrorResponse(404), 404

    set_arr = []
    for fc_set in sets:
        # constructing json response for each flashcard set
        temp = {
            FLASHCARD_SET_ID: fc_set.Set_ID,
            FLASHCARD_SET_NAME: fc_set.Set_Name,
            MODULE_ID: fc_set.Module_ID,
        }

        # checking if the current user is a "Student"
        if is_User("Student") == 200:
            # adding flashcard progress to the response object
            temp[FLASHCARD_PROGRESS] = fc_dac.get_progress({
                STUDENT_ID: current_user.User_ID,
                FLASHCARD_SET_ID: fc_set.Set_ID
            })

        set_arr.append(temp)

    res = Response(200, "Successfully fetched all the sets").content()
    res[FLASHCARD_SET_LIST] = set_arr

    # returning the json response object to the client
    return res, 200


@mod.route('/view_flashcard_set', methods=["POST"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@authenticated
def api_view_set():
    """ API endpoint for viewing a flash card set (it's first card)

    :return: A JSON response object containing details about a random flashcard from a flashcard set
    """
    # Gives you the first card from the set
    data = request.get_json()
    set_id = data[FLASHCARD_SET_ID]

    # getting the flashcard set object from the database
    fc_set = fc_dac.get_flashcard_set({
        FLASHCARD_SET_ID: set_id
    })

    if not fc_set:
        return ErrorResponse(404).content(), 400

    # getting the first flashcard from the flashcard set from the database
    first_card = fc_set.Flashcards.first()

    # constructing json response of the flashcard
    card_data = {
        FLASHCARD_SET_ID: first_card.Set_ID,
        FLASHCARD_QUESTION: first_card.Question,
        FLASHCARD_ANSWER: first_card.Answer,
        FLASHCARD_ID: first_card.FC_ID
    }

    res = Response(200, "Successfully fetched the first card").content()
    res[FLASHCARD_DATA] = card_data

    # checking if the current user is a "Student"
    if is_User("Student") == 200:
        # returning progress of the user in the set
        res[FLASHCARD_PROGRESS] = fc_dac.get_progress({
            STUDENT_ID: current_user.User_ID,
            FLASHCARD_SET_ID: set_id
        })

    # returning the response json the client
    return res, 200


@mod.route('/set_pref', methods=["POST"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@is_student
def api_set_pref():
    """ API endpoint to set the preference of a flashcard

    :return: response JSON containing details about a next random flashcard from
    the set(according to the mentioned probabilities) after setting the preference of the specified flashcard
    """
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


@mod.route('/reset_flashcard_set', methods=["POST"])
@cross_origin(origins="*",
              headers=['Content- Type', 'Authorization'], supports_credentials=True)
@jwt_required
@is_student
def api_reset_set():
    """ API endpoint used to reset the progress of a student in a flashcard set

    :return: JSON response indicating if the reset was successful or not
    """
    data = request.get_json()
    data[STUDENT_ID] = current_user.User_ID

    # resetting the progress of the student's flashcard set
    reset = fc_dac.reset_flashcard_set(data)

    if not reset:
        return ErrorResponse(404).content(), 200

    # sending response json to student
    return Response(200, "All flashcards of this set have been reset").content(), 200
