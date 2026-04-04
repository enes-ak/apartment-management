from datetime import datetime
from flask import Blueprint, render_template, request
from database import db
from models import Daire, Odeme, AidatAyari

bp = Blueprint('odemeler', __name__, url_prefix='/odemeler')

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan',
    5: 'Mayis', 6: 'Haziran', 7: 'Temmuz', 8: 'Agustos',
    9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}

@bp.route('/')
def index():
    now = datetime.now()
    yil = request.args.get('yil', now.year, type=int)
    ay = request.args.get('ay', now.month, type=int)
    daireler = Daire.query.order_by(Daire.daire_no).all()
    aidat = AidatAyari.guncel_miktar()
    odeme_durumlari = {}
    for daire in daireler:
        odeme = Odeme.query.filter_by(daire_id=daire.id, yil=yil, ay=ay).first()
        odeme_durumlari[daire.id] = odeme
    toplam_daire = len(daireler)
    odenen = sum(1 for o in odeme_durumlari.values() if o and o.odendi)
    odenmeyen = toplam_daire - odenen
    return render_template('odemeler.html', daireler=daireler, odeme_durumlari=odeme_durumlari,
                           yil=yil, ay=ay, aidat=aidat, ay_isimleri=AY_ISIMLERI,
                           toplam_daire=toplam_daire, odenen=odenen, odenmeyen=odenmeyen)

@bp.route('/toggle/<int:daire_id>/<int:yil>/<int:ay>', methods=['POST'])
def toggle(daire_id, yil, ay):
    odeme = Odeme.query.filter_by(daire_id=daire_id, yil=yil, ay=ay).first()
    if odeme is None:
        odeme = Odeme(daire_id=daire_id, yil=yil, ay=ay, odendi=True, odeme_tarihi=datetime.now())
        db.session.add(odeme)
    else:
        odeme.odendi = not odeme.odendi
        odeme.odeme_tarihi = datetime.now() if odeme.odendi else None
    db.session.commit()
    daire = Daire.query.get(daire_id)
    return render_template('parcalar/odeme_satir.html', daire=daire, odeme=odeme, yil=yil, ay=ay)

@bp.route('/daire/<int:daire_id>')
def daire_detay(daire_id):
    daire = Daire.query.get_or_404(daire_id)
    odemeler = Odeme.query.filter_by(daire_id=daire_id).order_by(Odeme.yil.desc(), Odeme.ay.desc()).all()
    aidat = AidatAyari.guncel_miktar()
    odenmeyen_sayisi = sum(1 for o in odemeler if not o.odendi)
    return render_template('daire_detay.html', daire=daire, odemeler=odemeler, aidat=aidat,
                           odenmeyen_sayisi=odenmeyen_sayisi, ay_isimleri=AY_ISIMLERI)
