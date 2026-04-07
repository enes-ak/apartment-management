from datetime import datetime
from flask import Blueprint, render_template, request
from models import Apartment, Payment, Setting, DuesConfig

bp = Blueprint('messages', __name__, url_prefix='/mesajlar')

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan',
    5: 'Mayis', 6: 'Haziran', 7: 'Temmuz', 8: 'Agustos',
    9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}

@bp.route('/')
def index():
    now = datetime.now()
    return render_template('messages.html', year=now.year, month=now.month, MONTH_NAMES=AY_ISIMLERI)

@bp.route('/olustur')
def generate():
    year = request.args.get('yil', type=int)
    month = request.args.get('ay', type=int)
    msg_type = request.args.get('tur', 'odemeyenler')
    dues = DuesConfig.current_amount()
    building_name = Setting.get('apartman_adi', 'Apartman')
    template = Setting.get('mesaj_sablonu', '')
    month_year = f'{AY_ISIMLERI[month]} {year}'

    if msg_type == 'genel':
        # General reminder: list all apartments
        apartments = Apartment.query.order_by(Apartment.unit_no).all()
    else:
        # Only unpaid
        paid_ids = {p.apartment_id for p in Payment.query.filter_by(year=year, month=month, is_paid=True).all()}
        if paid_ids:
            apartments = Apartment.query.filter(~Apartment.id.in_(paid_ids)).order_by(Apartment.unit_no).all()
        else:
            apartments = Apartment.query.order_by(Apartment.unit_no).all()

    lines = []
    for apt in apartments:
        lines.append(f'- Daire {apt.unit_no}')
    defaulters_text = '\n'.join(lines) if lines else '- Herkes odemis!'

    message = template.format(
        apartman_adi=building_name,
        ay_yil=month_year,
        miktar=f'{dues:.2f}',
        odemeyenler=defaulters_text,
    )
    return render_template('partials/message_preview.html', message=message, apartments=apartments,
                           year=year, month=month, month_name=AY_ISIMLERI[month])
