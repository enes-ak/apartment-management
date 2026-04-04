from flask import Blueprint, render_template

bp = Blueprint('ana_sayfa', __name__)


@bp.route('/')
def index():
    return render_template('ana_sayfa.html')
