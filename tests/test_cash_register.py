from models import Payment, Expense, ExpenseCategory, CashRegister, Apartment, DuesConfig
from database import db as _db


def _create_payment(db_session, unit_no, year, month, is_paid=True):
    apartment = Apartment.query.filter_by(unit_no=unit_no).first()
    payment = Payment(apartment_id=apartment.id, year=year, month=month, is_paid=is_paid)
    _db.session.add(payment)
    _db.session.commit()


def _create_expense(db_session, category_name, year, month, amount):
    category = ExpenseCategory.query.filter_by(category_name=category_name).first()
    expense = Expense(category_id=category.id, year=year, month=month, amount=amount, description='')
    _db.session.add(expense)
    _db.session.commit()


def test_calculate_cash(db_session):
    for i in range(1, 4):
        _create_payment(db_session, i, 2026, 4, True)
    _create_expense(db_session, 'Elektrik', 2026, 4, 800)
    from services.cash_service import calculate_cash
    cash = calculate_cash(2026, 4)
    assert cash.total_income == 1500  # 3 * 500
    assert cash.total_expense == 800
    assert cash.balance == 700


def test_cash_carryover(db_session):
    previous = CashRegister(year=2026, month=3, total_income=6000, total_expense=3000, carryover=0, balance=3000)
    _db.session.add(previous)
    _db.session.commit()
    for i in range(1, 4):
        _create_payment(db_session, i, 2026, 4, True)
    _create_expense(db_session, 'Su', 2026, 4, 500)
    from services.cash_service import calculate_cash
    cash = calculate_cash(2026, 4)
    assert cash.carryover == 3000
    assert cash.balance == 4000  # 3000 + 1500 - 500


def test_cash_register_page(client):
    response = client.get('/kasa/')
    assert response.status_code == 200
    assert 'Kasa'.encode() in response.data
