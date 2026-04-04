from models import Daire, Odeme
from database import db as _db


def test_mesajlar_sayfasi_yukle(client):
    response = client.get('/mesajlar/')
    assert response.status_code == 200
    assert 'Mesaj Hazirla'.encode() in response.data


def test_mesaj_olustur_tum_odemeyenler(client, db_session):
    response = client.get('/mesajlar/olustur?yil=2026&ay=4')
    assert response.status_code == 200
    assert 'Daire 1'.encode() in response.data


def test_mesaj_olustur_kismi_odeme(client, db_session):
    daire = Daire.query.filter_by(daire_no=1).first()
    _db.session.add(Odeme(daire_id=daire.id, yil=2026, ay=4, odendi=True))
    _db.session.commit()
    response = client.get('/mesajlar/olustur?yil=2026&ay=4')
    assert response.status_code == 200
    assert 'Daire 1 -'.encode() not in response.data
    assert 'Daire 2 -'.encode() in response.data
