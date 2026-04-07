import os
from models import Apartment, Payment, Expense, ExpenseCategory, CashRegister
from database import db as _db


def _setup(db_session):
    for i in range(1, 7):
        apartment = Apartment.query.filter_by(unit_no=i).first()
        _db.session.add(Payment(apartment_id=apartment.id, year=2026, month=4, is_paid=True))
    category = ExpenseCategory.query.filter_by(category_name='Elektrik').first()
    _db.session.add(Expense(category_id=category.id, year=2026, month=4, amount=1200, description=''))
    category_su = ExpenseCategory.query.filter_by(category_name='Su').first()
    _db.session.add(Expense(category_id=category_su.id, year=2026, month=4, amount=400, description=''))
    _db.session.add(CashRegister(year=2026, month=4, total_income=3000, total_expense=1600, carryover=500, balance=1900))
    _db.session.commit()


def test_reports_page(client):
    response = client.get('/raporlar/')
    assert response.status_code == 200


def test_report_excel_monthly_summary(client, db_session):
    _setup(db_session)
    response = client.get('/raporlar/olustur?tur=aylik_ozet&yil=2026&ay=4&format=excel')
    assert response.status_code == 200
    assert response.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


def test_report_pdf_monthly_summary(client, db_session):
    _setup(db_session)
    response = client.get('/raporlar/olustur?tur=aylik_ozet&yil=2026&ay=4&format=pdf')
    assert response.status_code == 200
    assert response.content_type == 'application/pdf'


def test_report_excel_payment_status(client, db_session):
    _setup(db_session)
    response = client.get('/raporlar/olustur?tur=odeme_durumu&yil=2026&ay=4&format=excel')
    assert response.status_code == 200


def test_report_excel_expense_detail(client, db_session):
    _setup(db_session)
    response = client.get('/raporlar/olustur?tur=gider_detay&yil=2026&ay=4&format=excel')
    assert response.status_code == 200


def test_report_excel_yearly_summary(client, db_session):
    _setup(db_session)
    response = client.get('/raporlar/olustur?tur=yillik_ozet&yil=2026&format=excel')
    assert response.status_code == 200
