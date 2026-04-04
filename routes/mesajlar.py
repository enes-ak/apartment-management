from flask import Blueprint, render_template

bp = Blueprint('mesajlar', __name__, url_prefix='/mesajlar')


@bp.route('/')
def index():
    return render_template('mesajlar.html')
