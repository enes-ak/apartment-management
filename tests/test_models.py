from models import Apartment, DuesConfig, ExpenseCategory, Setting
from datetime import date


def test_apartment_count(db_session):
    assert Apartment.query.count() == 12


def test_apartment_unit_no_ordered(db_session):
    apartments = Apartment.query.order_by(Apartment.unit_no).all()
    assert [a.unit_no for a in apartments] == list(range(1, 13))


def test_dues_current_amount(db_session):
    assert DuesConfig.current_amount() == 500


def test_dues_increase(db_session):
    from database import db
    db.session.add(DuesConfig(amount=750, effective_date=date(2026, 4, 1)))
    db.session.commit()
    assert DuesConfig.current_amount() == 750


def test_expense_categories(db_session):
    active = ExpenseCategory.query.filter_by(is_active=True).all()
    assert len(active) == 4
    names = {k.category_name for k in active}
    assert 'Elektrik' in names
    assert 'Su' in names


def test_setting_get_save(db_session):
    assert Setting.get('apartman_adi') == 'Test Apartmani'
    Setting.save('apartman_adi', 'Yeni Apartman')
    assert Setting.get('apartman_adi') == 'Yeni Apartman'


def test_setting_get_default(db_session):
    assert Setting.get('yok_boyle_bir_sey', 'fallback') == 'fallback'


def test_settings_page_load(client):
    response = client.get('/ayarlar/')
    assert response.status_code == 200
    assert 'Ayarlar'.encode() in response.data


def test_settings_update_apartment_name(client):
    response = client.post('/ayarlar/genel', data={
        'apartman_adi': 'Gul Apartmani',
        'mail_adresi': 'test@test.com',
        'smtp_sunucu': 'smtp.gmail.com',
        'smtp_port': '587',
        'smtp_sifre': '',
    }, follow_redirects=True)
    assert response.status_code == 200
    from models import Setting
    assert Setting.get('apartman_adi') == 'Gul Apartmani'


def test_dues_update(client):
    response = client.post('/ayarlar/aidat', data={
        'miktar': '750',
    }, follow_redirects=True)
    assert response.status_code == 200
    from models import DuesConfig
    assert DuesConfig.current_amount() == 750


def test_apartment_update(client):
    from models import Apartment
    response = client.post('/ayarlar/daire/1', data={
        'sakin_adi': 'Ahmet Yilmaz',
        'telefon': '5551234567',
    }, follow_redirects=True)
    assert response.status_code == 200


def test_expense_category_add(client):
    response = client.post('/ayarlar/gider-kalemi', data={
        'kalem_adi': 'Dogalgaz',
    }, follow_redirects=True)
    assert response.status_code == 200
    from models import ExpenseCategory
    assert ExpenseCategory.query.filter_by(category_name='Dogalgaz').first() is not None


def test_expense_category_toggle(client):
    from models import ExpenseCategory
    category = ExpenseCategory.query.first()
    response = client.post(f'/ayarlar/gider-kalemi/{category.id}/toggle', follow_redirects=True)
    assert response.status_code == 200
