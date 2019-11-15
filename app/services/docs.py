from flask import Blueprint
from flask import render_template

from app import app

mod = Blueprint('docs', __name__)


@mod.route('/')
@mod.route('/doc')
@mod.route('/index')
def doc():
    return render_template('doc.html')
