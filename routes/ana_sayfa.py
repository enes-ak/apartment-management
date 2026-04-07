from datetime import datetime
from flask import Blueprint, render_template
from models import Daire, Odeme, Gider, AidatAyari

bp = Blueprint('ana_sayfa', __name__)


@bp.route('/')
def index():
    now = datetime.now()
    yil = now.year
    aidat = AidatAyari.guncel_miktar()
    toplam_daire = Daire.query.count()

    # Yillik toplam gelir
    odenen_toplam = Odeme.query.filter_by(yil=yil, odendi=True).count()
    toplam_gelir = odenen_toplam * aidat

    # Yillik toplam gider
    giderler = Gider.query.filter_by(yil=yil).all()
    toplam_gider = sum(g.tutar for g in giderler)

    # Bakiye
    bakiye = toplam_gelir - toplam_gider

    # Yillik tahsilat orani (12 ay uzerinden)
    beklenen_yillik = toplam_daire * 12 * aidat
    tahsilat_yillik = (odenen_toplam / (toplam_daire * 12) * 100) if toplam_daire > 0 else 0

    # Guncel tahsilat orani (sadece 1..bulunulan ay arasindaki odemeler)
    odenen_guncel = Odeme.query.filter(
        Odeme.yil == yil, Odeme.odendi == True, Odeme.ay <= now.month
    ).count()
    beklenen_guncel = toplam_daire * now.month * aidat
    tahsilat_guncel = (odenen_guncel / (toplam_daire * now.month) * 100) if toplam_daire > 0 else 0

    # Bulundugumuz aya kadar gecikmis odemeler (odenmemis daireler)
    # Her ay icin her daire kontrol et, odenmemis = gecikmis
    gecikmis_daireler = {}  # daire_id -> gecikmis ay sayisi
    for ay in range(1, now.month + 1):
        odenen_idler = {o.daire_id for o in Odeme.query.filter_by(yil=yil, ay=ay, odendi=True).all()}
        for daire in Daire.query.all():
            if daire.id not in odenen_idler:
                gecikmis_daireler[daire.id] = gecikmis_daireler.get(daire.id, 0) + 1

    # Gecikmis olan daireleri listele
    odemeyenler = []
    for daire_id, gecikmis_ay in sorted(gecikmis_daireler.items()):
        daire = Daire.query.get(daire_id)
        odemeyenler.append({'daire': daire, 'gecikmis_ay': gecikmis_ay})

    return render_template('ana_sayfa.html',
                           yil=yil,
                           aidat=aidat,
                           toplam_daire=toplam_daire,
                           toplam_gelir=toplam_gelir,
                           toplam_gider=toplam_gider,
                           bakiye=bakiye,
                           beklenen_yillik=beklenen_yillik,
                           tahsilat_yillik=tahsilat_yillik,
                           beklenen_guncel=beklenen_guncel,
                           tahsilat_guncel=tahsilat_guncel,
                           ay_sayisi=now.month,
                           odenen_toplam=odenen_toplam,
                           odemeyenler=odemeyenler)
