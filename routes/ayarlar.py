from flask import Blueprint, render_template

bp = Blueprint('ayarlar', __name__, url_prefix='/ayarlar')


@bp.route('/')
def index():
    return render_template('ayarlar.html')
