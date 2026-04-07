from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Kasa, Odeme, Gider, GiderKalemi, Daire, AidatAyari
from database import db
from services.kasa_servisi import kasa_hesapla

bp = Blueprint('kasa', __name__, url_prefix='/kasa')


@bp.route('/')
def index():
    now = datetime.now()
    yil = request.args.get('yil', now.year, type=int)

    aidat = AidatAyari.guncel_miktar()
    toplam_daire = Daire.query.count()

    # Toplam gelir: yil icerisinde odenen tum aidatlar
    odenen_toplam = Odeme.query.filter_by(yil=yil, odendi=True).count()
    toplam_gelir = odenen_toplam * aidat

    # Toplam gider: yil icerisindeki tum giderler
    giderler = Gider.query.filter_by(yil=yil).all()
    toplam_gider = sum(g.tutar for g in giderler)

    # Bakiye
    bakiye = toplam_gelir - toplam_gider

    # Gider dagilimi (kalem bazli)
    gider_dagilimi = {}
    for g in giderler:
        kalem_adi = g.kalem.kalem_adi
        gider_dagilimi[kalem_adi] = gider_dagilimi.get(kalem_adi, 0) + g.tutar

    # Tahsilat orani
    beklenen_gelir = toplam_daire * 12 * aidat
    tahsilat_orani = (odenen_toplam / (toplam_daire * 12) * 100) if toplam_daire > 0 else 0

    return render_template('kasa.html',
                           yil=yil,
                           aidat=aidat,
                           toplam_daire=toplam_daire,
                           odenen_toplam=odenen_toplam,
                           toplam_gelir=toplam_gelir,
                           toplam_gider=toplam_gider,
                           bakiye=bakiye,
                           beklenen_gelir=beklenen_gelir,
                           tahsilat_orani=tahsilat_orani,
                           gider_dagilimi=gider_dagilimi)
