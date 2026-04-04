from models import Gider, GiderKalemi


def test_giderler_sayfasi_yukle(client):
    response = client.get('/giderler/')
    assert response.status_code == 200
    assert 'Giderler'.encode() in response.data


def test_gider_ekle(client, db_session):
    kalem = GiderKalemi.query.filter_by(kalem_adi='Elektrik').first()
    response = client.post('/giderler/ekle', data={
        'kalem_id': kalem.id,
        'yil': 2026,
        'ay': 4,
        'tutar': '1500.50',
        'aciklama': 'Nisan elektrik faturasi',
    }, follow_redirects=True)
    assert response.status_code == 200
    gider = Gider.query.filter_by(kalem_id=kalem.id, yil=2026, ay=4).first()
    assert gider is not None
    assert gider.tutar == 1500.50


def test_gider_sil(client, db_session):
    kalem = GiderKalemi.query.filter_by(kalem_adi='Su').first()
    from database import db
    gider = Gider(kalem_id=kalem.id, yil=2026, ay=4, tutar=300, aciklama='')
    db.session.add(gider)
    db.session.commit()
    gider_id = gider.id
    response = client.post(f'/giderler/sil/{gider_id}', follow_redirects=True)
    assert response.status_code == 200
    assert Gider.query.get(gider_id) is None
