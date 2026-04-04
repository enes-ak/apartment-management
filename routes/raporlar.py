from flask import Blueprint, render_template

bp = Blueprint('raporlar', __name__, url_prefix='/raporlar')


@bp.route('/')
def index():
    return render_template('raporlar.html')
