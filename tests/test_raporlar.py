import os
from models import Daire, Odeme, Gider, GiderKalemi, Kasa
from database import db as _db


def _hazirlik(db_session):
    for i in range(1, 7):
        daire = Daire.query.filter_by(daire_no=i).first()
        _db.session.add(Odeme(daire_id=daire.id, yil=2026, ay=4, odendi=True))
    kalem = GiderKalemi.query.filter_by(kalem_adi='Elektrik').first()
    _db.session.add(Gider(kalem_id=kalem.id, yil=2026, ay=4, tutar=1200, aciklama=''))
    kalem_su = GiderKalemi.query.filter_by(kalem_adi='Su').first()
    _db.session.add(Gider(kalem_id=kalem_su.id, yil=2026, ay=4, tutar=400, aciklama=''))
    _db.session.add(Kasa(yil=2026, ay=4, toplam_gelir=3000, toplam_gider=1600, devir=500, bakiye=1900))
    _db.session.commit()


def test_raporlar_sayfasi(client):
    response = client.get('/raporlar/')
    assert response.status_code == 200


def test_rapor_excel_aylik_ozet(client, db_session):
    _hazirlik(db_session)
    response = client.get('/raporlar/olustur?tur=aylik_ozet&yil=2026&ay=4&format=excel')
    assert response.status_code == 200
    assert response.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


def test_rapor_pdf_aylik_ozet(client, db_session):
    _hazirlik(db_session)
    response = client.get('/raporlar/olustur?tur=aylik_ozet&yil=2026&ay=4&format=pdf')
    assert response.status_code == 200
    assert response.content_type == 'application/pdf'


def test_rapor_excel_odeme_durumu(client, db_session):
    _hazirlik(db_session)
    response = client.get('/raporlar/olustur?tur=odeme_durumu&yil=2026&ay=4&format=excel')
    assert response.status_code == 200


def test_rapor_excel_gider_detay(client, db_session):
    _hazirlik(db_session)
    response = client.get('/raporlar/olustur?tur=gider_detay&yil=2026&ay=4&format=excel')
    assert response.status_code == 200


def test_rapor_excel_yillik_ozet(client, db_session):
    _hazirlik(db_session)
    response = client.get('/raporlar/olustur?tur=yillik_ozet&yil=2026&format=excel')
    assert response.status_code == 200
