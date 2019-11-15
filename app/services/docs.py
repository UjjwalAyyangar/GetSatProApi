from flask import Blueprint, jsonify
from flask import abort, request, render_template
from app.system import *
from app.dac import *
from flask_login import current_user, logout_user, login_user
from app import db, flask_bcrypt, jwt, login
from app import app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity
)

mod = Blueprint('docs', __name__)


@mod.route('/')
@mod.route('/doc')
@mod.route('/index')
def doc():
    return render_template('doc.html')
