from flask import Blueprint, render_template, request
from models import Log

bp = Blueprint('logs', __name__, url_prefix='/loglar')


@bp.route('/')
def index():
    page = request.args.get('sayfa', 1, type=int)
    search = request.args.get('q', '').strip()
    per_page = 50

    query_obj = Log.query
    if search:
        query_obj = query_obj.filter(Log.action.ilike(f'%{search}%'))
    logs = query_obj.order_by(Log.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('logs.html', logs=logs, search=search)
