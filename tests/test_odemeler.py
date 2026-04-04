from models import Odeme, Daire


def test_odemeler_sayfasi_yukle(client):
    response = client.get('/odemeler/')
    assert response.status_code == 200
    assert 'Odeme Takibi'.encode() in response.data


def test_odemeler_ay_secimi(client):
    response = client.get('/odemeler/?yil=2026&ay=4')
    assert response.status_code == 200


def test_odeme_toggle_odendi(client, db_session):
    daire = Daire.query.filter_by(daire_no=1).first()
    response = client.post(f'/odemeler/toggle/{daire.id}/2026/4')
    assert response.status_code == 200
    odeme = Odeme.query.filter_by(daire_id=daire.id, yil=2026, ay=4).first()
    assert odeme is not None
    assert odeme.odendi is True


def test_odeme_toggle_geri_al(client, db_session):
    daire = Daire.query.filter_by(daire_no=1).first()
    client.post(f'/odemeler/toggle/{daire.id}/2026/4')
    client.post(f'/odemeler/toggle/{daire.id}/2026/4')
    odeme = Odeme.query.filter_by(daire_id=daire.id, yil=2026, ay=4).first()
    assert odeme.odendi is False


def test_daire_detay(client, db_session):
    daire = Daire.query.filter_by(daire_no=1).first()
    response = client.get(f'/odemeler/daire/{daire.id}')
    assert response.status_code == 200
