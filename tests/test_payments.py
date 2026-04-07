from models import Payment, Apartment


def test_payments_page_load(client):
    response = client.get('/odemeler/')
    assert response.status_code == 200
    assert 'Odeme Takibi'.encode() in response.data


def test_payments_month_selection(client):
    response = client.get('/odemeler/?yil=2026&ay=4')
    assert response.status_code == 200


def test_payment_toggle_paid(client, db_session):
    apartment = Apartment.query.filter_by(unit_no=1).first()
    response = client.post(f'/odemeler/toggle/{apartment.id}/2026/4')
    assert response.status_code == 200
    payment = Payment.query.filter_by(apartment_id=apartment.id, year=2026, month=4).first()
    assert payment is not None
    assert payment.is_paid is True


def test_payment_toggle_undo(client, db_session):
    apartment = Apartment.query.filter_by(unit_no=1).first()
    client.post(f'/odemeler/toggle/{apartment.id}/2026/4')
    client.post(f'/odemeler/toggle/{apartment.id}/2026/4')
    payment = Payment.query.filter_by(apartment_id=apartment.id, year=2026, month=4).first()
    assert payment.is_paid is False


def test_apartment_detail(client, db_session):
    apartment = Apartment.query.filter_by(unit_no=1).first()
    response = client.get(f'/odemeler/daire/{apartment.id}')
    assert response.status_code == 200
