from datetime import datetime
from flask import Blueprint, render_template
from models import Daire, Odeme, Gider, Kasa, AidatAyari

bp = Blueprint('ana_sayfa', __name__)

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan',
    5: 'Mayis', 6: 'Haziran', 7: 'Temmuz', 8: 'Agustos',
    9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}

@bp.route('/')
def index():
    now = datetime.now()
    yil, ay = now.year, now.month
    aidat = AidatAyari.guncel_miktar()
    toplam_daire = Daire.query.count()
    odenen = Odeme.query.filter_by(yil=yil, ay=ay, odendi=True).count()
    odenmeyen = toplam_daire - odenen
    giderler = Gider.query.filter_by(yil=yil, ay=ay).all()
    toplam_gider = sum(g.tutar for g in giderler)
    kasa = Kasa.query.filter_by(yil=yil, ay=ay).first()
    odenen_daire_idler = {o.daire_id for o in Odeme.query.filter_by(yil=yil, ay=ay, odendi=True).all()}
    odemeyenler = Daire.query.filter(~Daire.id.in_(odenen_daire_idler)).order_by(Daire.daire_no).all() if odenen_daire_idler else Daire.query.order_by(Daire.daire_no).all()
    return render_template('ana_sayfa.html', yil=yil, ay=ay, ay_adi=AY_ISIMLERI[ay],
                           aidat=aidat, toplam_daire=toplam_daire, odenen=odenen,
                           odenmeyen=odenmeyen, toplam_gider=toplam_gider,
                           kasa=kasa, odemeyenler=odemeyenler)
