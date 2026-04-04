from flask import Blueprint, render_template

bp = Blueprint('giderler', __name__, url_prefix='/giderler')


@bp.route('/')
def index():
    return render_template('giderler.html')
