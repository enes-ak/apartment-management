from flask import Blueprint, render_template, request
from models import Log

bp = Blueprint('loglar', __name__, url_prefix='/loglar')


@bp.route('/')
def index():
    sayfa = request.args.get('sayfa', 1, type=int)
    arama = request.args.get('q', '').strip()
    per_sayfa = 50

    sorgu = Log.query
    if arama:
        sorgu = sorgu.filter(Log.eylem.ilike(f'%{arama}%'))
    loglar = sorgu.order_by(Log.tarih.desc()).paginate(page=sayfa, per_page=per_sayfa, error_out=False)

    return render_template('loglar.html', loglar=loglar, arama=arama)
