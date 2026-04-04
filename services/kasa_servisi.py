from database import db
from models import Kasa, Odeme, Gider, AidatAyari


def kasa_hesapla(yil, ay):
    aidat = AidatAyari.guncel_miktar()
    odenen_sayisi = Odeme.query.filter_by(yil=yil, ay=ay, odendi=True).count()
    toplam_gelir = odenen_sayisi * aidat
    giderler = Gider.query.filter_by(yil=yil, ay=ay).all()
    toplam_gider = sum(g.tutar for g in giderler)
    devir = 0
    if ay == 1:
        onceki = Kasa.query.filter_by(yil=yil - 1, ay=12).first()
    else:
        onceki = Kasa.query.filter_by(yil=yil, ay=ay - 1).first()
    if onceki:
        devir = onceki.bakiye
    bakiye = devir + toplam_gelir - toplam_gider
    kasa = Kasa.query.filter_by(yil=yil, ay=ay).first()
    if kasa is None:
        kasa = Kasa(yil=yil, ay=ay)
        db.session.add(kasa)
    kasa.toplam_gelir = toplam_gelir
    kasa.toplam_gider = toplam_gider
    kasa.devir = devir
    kasa.bakiye = bakiye
    db.session.commit()
    return kasa


def yillik_kasa(yil):
    kayitlar = []
    for ay in range(1, 13):
        kasa = Kasa.query.filter_by(yil=yil, ay=ay).first()
        kayitlar.append(kasa)
    return kayitlar
