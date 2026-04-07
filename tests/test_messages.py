from models import Apartment, Payment
from database import db as _db


def test_messages_page_load(client):
    response = client.get('/mesajlar/')
    assert response.status_code == 200
    assert 'Mesaj Hazirla'.encode() in response.data


def test_message_create_all_unpaid(client, db_session):
    response = client.get('/mesajlar/olustur?yil=2026&ay=4')
    assert response.status_code == 200
    assert 'Daire 1'.encode() in response.data


def test_message_create_partial_payment(client, db_session):
    apartment = Apartment.query.filter_by(unit_no=1).first()
    _db.session.add(Payment(apartment_id=apartment.id, year=2026, month=4, is_paid=True))
    _db.session.commit()
    response = client.get('/mesajlar/olustur?yil=2026&ay=4')
    assert response.status_code == 200
    assert b'Daire 1\n' not in response.data
    assert 'Daire 2'.encode() in response.data
