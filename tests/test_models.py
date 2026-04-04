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


def test_ayarlar_sayfasi_yukle(client):
    response = client.get('/ayarlar/')
    assert response.status_code == 200
    assert 'Ayarlar'.encode() in response.data


def test_ayarlar_apartman_adi_guncelle(client):
    response = client.post('/ayarlar/genel', data={
        'apartman_adi': 'Gul Apartmani',
        'mail_adresi': 'test@test.com',
        'smtp_sunucu': 'smtp.gmail.com',
        'smtp_port': '587',
        'smtp_sifre': '',
    }, follow_redirects=True)
    assert response.status_code == 200
    from models import Ayar
    assert Ayar.getir('apartman_adi') == 'Gul Apartmani'


def test_aidat_guncelle(client):
    response = client.post('/ayarlar/aidat', data={
        'miktar': '750',
    }, follow_redirects=True)
    assert response.status_code == 200
    from models import AidatAyari
    assert AidatAyari.guncel_miktar() == 750


def test_daire_guncelle(client):
    from models import Daire
    response = client.post('/ayarlar/daire/1', data={
        'sakin_adi': 'Ahmet Yilmaz',
        'telefon': '5551234567',
    }, follow_redirects=True)
    assert response.status_code == 200


def test_gider_kalemi_ekle(client):
    response = client.post('/ayarlar/gider-kalemi', data={
        'kalem_adi': 'Dogalgaz',
    }, follow_redirects=True)
    assert response.status_code == 200
    from models import GiderKalemi
    assert GiderKalemi.query.filter_by(kalem_adi='Dogalgaz').first() is not None


def test_gider_kalemi_pasif_yap(client):
    from models import GiderKalemi
    kalem = GiderKalemi.query.first()
    response = client.post(f'/ayarlar/gider-kalemi/{kalem.id}/toggle', follow_redirects=True)
    assert response.status_code == 200
