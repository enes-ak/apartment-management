from flask import Blueprint, render_template

bp = Blueprint('odemeler', __name__, url_prefix='/odemeler')


@bp.route('/')
def index():
    return render_template('odemeler.html')
