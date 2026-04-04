from flask import Blueprint, render_template

bp = Blueprint('kasa', __name__, url_prefix='/kasa')


@bp.route('/')
def index():
    return render_template('kasa.html')
