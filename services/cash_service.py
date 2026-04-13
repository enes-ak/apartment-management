from database import db
from models import CashRegister, Payment, Expense, DuesConfig, ExtraCollection, ExtraPayment


def calculate_cash(year, month):
    dues = DuesConfig.current_amount()
    paid_count = Payment.query.filter_by(year=year, month=month, is_paid=True).count()
    dues_income = paid_count * dues

    # Extra collection income for this month
    extra_income = 0
    collections = ExtraCollection.query.filter_by(year=year, month=month).all()
    for c in collections:
        paid = ExtraPayment.query.filter_by(collection_id=c.id, is_paid=True).count()
        extra_income += paid * c.per_unit_amount

    total_income = dues_income + extra_income
    expenses = Expense.query.filter_by(year=year, month=month).all()
    total_expense = sum(e.amount for e in expenses)
    carryover = 0
    if month == 1:
        prev = CashRegister.query.filter_by(year=year - 1, month=12).first()
    else:
        prev = CashRegister.query.filter_by(year=year, month=month - 1).first()
    if prev:
        carryover = prev.balance
    balance = carryover + total_income - total_expense
    cash = CashRegister.query.filter_by(year=year, month=month).first()
    if cash is None:
        cash = CashRegister(year=year, month=month)
        db.session.add(cash)
    cash.total_income = total_income
    cash.total_expense = total_expense
    cash.carryover = carryover
    cash.balance = balance
    db.session.commit()
    return cash


def yearly_cash(year):
    records = []
    for month in range(1, 13):
        cash = CashRegister.query.filter_by(year=year, month=month).first()
        records.append(cash)
    return records
