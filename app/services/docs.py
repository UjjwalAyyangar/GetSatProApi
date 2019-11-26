from flask import Blueprint
from flask import render_template
from flask_cors import cross_origin

from app import app

mod = Blueprint('docs', __name__)


@mod.route('/')
@mod.route('/doc')
@mod.route('/index')
@cross_origin(origins="*", headers=['Content- Type', 'Authorization'], supports_credentials=True)
def doc():
    return render_template('doc.html')
