from models import Daire, AidatAyari, GiderKalemi, Ayar
from datetime import date


def test_daire_sayisi(db_session):
    assert Daire.query.count() == 12


def test_daire_no_sirali(db_session):
    daireler = Daire.query.order_by(Daire.daire_no).all()
    assert [d.daire_no for d in daireler] == list(range(1, 13))


def test_aidat_guncel_miktar(db_session):
    assert AidatAyari.guncel_miktar() == 500


def test_aidat_zam(db_session):
    from database import db
    db.session.add(AidatAyari(miktar=750, gecerlilik_tarihi=date(2026, 4, 1)))
    db.session.commit()
    assert AidatAyari.guncel_miktar() == 750


def test_gider_kalemleri(db_session):
    aktif = GiderKalemi.query.filter_by(aktif=True).all()
    assert len(aktif) == 4
    isimler = {k.kalem_adi for k in aktif}
    assert 'Elektrik' in isimler
    assert 'Su' in isimler


def test_ayar_getir_kaydet(db_session):
    assert Ayar.getir('apartman_adi') == 'Test Apartmani'
    Ayar.kaydet('apartman_adi', 'Yeni Apartman')
    assert Ayar.getir('apartman_adi') == 'Yeni Apartman'


def test_ayar_getir_varsayilan(db_session):
    assert Ayar.getir('yok_boyle_bir_sey', 'fallback') == 'fallback'
