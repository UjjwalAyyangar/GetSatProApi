from flask import Blueprint, jsonify
from flask import abort, request
from app.system import *
from app.dac import *
from flask_login import current_user, logout_user, login_user
from app import app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity
)

mod = Blueprint('flashcards', __name__, url_prefix='/api')


# Flashcards
@mod.route('/view_flashcard')
@jwt_required
@authenticated
def api_view_flashcards():
    data = request.get_json()
    fset = get_flashcard_set(data)

    if fset:
        flashcards = fset.Flashcards.all()
        card_list = []
        for card in flashcards:
            temp_data = {
                "fc_id": card.FC_ID
            }
            temp_card = get_flashcard(temp_data)
            if temp_card:
                card_data = {
                    "set_id": data["set_id"],
                    "question": temp_card.Question,
                    "answer": temp_card.Answer,
                }

                pref = get_fcpref({
                    "stud_id": current_user.User_ID,
                    "fc_id": card.FC_ID
                })

                card_data["difficulty"] = get_difficulty(pref.Difficulty)

                card_list.append(card_data)
            else:
                continue

        res = Response(
            200,
            "Fetched flashcard sets successfully"
        )

        ret = res.content()
        ret["flashcards"] = card_list.append()

        return ret, 200
    else:
        return ErrorResponse(400).content(), 400


@mod.route('/set_pref')
@jwt_required
@authenticated
def api_set_pref():
    data = request.get_json()
    fc_pref = get_fcpref({
        "stud_id": current_user.User_ID,
        "FC_ID": data["fc_id"]
    })

    if fc_pref:
        fc_pref.difficulty = data["diff"]
        db.session.commit()
        return Response(
            200,
            "Preference set succesfully"
        ).content(), 200

    else:
        return ErrorResponse(400).content(), 400
