from models import Odeme, Gider, GiderKalemi, Kasa, Daire, AidatAyari
from database import db as _db


def _odeme_olustur(db_session, daire_no, yil, ay, odendi=True):
    daire = Daire.query.filter_by(daire_no=daire_no).first()
    odeme = Odeme(daire_id=daire.id, yil=yil, ay=ay, odendi=odendi)
    _db.session.add(odeme)
    _db.session.commit()


def _gider_olustur(db_session, kalem_adi, yil, ay, tutar):
    kalem = GiderKalemi.query.filter_by(kalem_adi=kalem_adi).first()
    gider = Gider(kalem_id=kalem.id, yil=yil, ay=ay, tutar=tutar, aciklama='')
    _db.session.add(gider)
    _db.session.commit()


def test_kasa_hesapla(db_session):
    for i in range(1, 4):
        _odeme_olustur(db_session, i, 2026, 4, True)
    _gider_olustur(db_session, 'Elektrik', 2026, 4, 800)
    from services.kasa_servisi import kasa_hesapla
    kasa = kasa_hesapla(2026, 4)
    assert kasa.toplam_gelir == 1500  # 3 * 500
    assert kasa.toplam_gider == 800
    assert kasa.bakiye == 700


def test_kasa_devir(db_session):
    onceki = Kasa(yil=2026, ay=3, toplam_gelir=6000, toplam_gider=3000, devir=0, bakiye=3000)
    _db.session.add(onceki)
    _db.session.commit()
    for i in range(1, 4):
        _odeme_olustur(db_session, i, 2026, 4, True)
    _gider_olustur(db_session, 'Su', 2026, 4, 500)
    from services.kasa_servisi import kasa_hesapla
    kasa = kasa_hesapla(2026, 4)
    assert kasa.devir == 3000
    assert kasa.bakiye == 4000  # 3000 + 1500 - 500


def test_kasa_sayfasi(client):
    response = client.get('/kasa/')
    assert response.status_code == 200
    assert 'Kasa'.encode() in response.data
