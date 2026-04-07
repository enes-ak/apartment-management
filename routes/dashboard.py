from datetime import datetime
from flask import Blueprint, render_template
from models import Apartment, Payment, Expense, DuesConfig

bp = Blueprint('dashboard', __name__)


@bp.route('/')
def index():
    now = datetime.now()
    year = now.year
    dues = DuesConfig.current_amount()
    total_apartments = Apartment.query.count()

    # Yearly total income
    total_paid = Payment.query.filter_by(year=year, is_paid=True).count()
    total_income = total_paid * dues

    # Yearly total expense
    expenses = Expense.query.filter_by(year=year).all()
    total_expense = sum(e.amount for e in expenses)

    # Balance
    balance = total_income - total_expense

    # Yearly collection rate (over 12 months)
    expected_annual = total_apartments * 12 * dues
    collection_annual = (total_paid / (total_apartments * 12) * 100) if total_apartments > 0 else 0

    # Current collection rate (only months 1..current month)
    current_paid = Payment.query.filter(
        Payment.year == year, Payment.is_paid == True, Payment.month <= now.month
    ).count()
    expected_current = total_apartments * now.month * dues
    collection_current = (current_paid / (total_apartments * now.month) * 100) if total_apartments > 0 else 0

    # Overdue payments up to current month
    overdue_apartments = {}  # apartment_id -> overdue month count
    for month in range(1, now.month + 1):
        paid_ids = {p.apartment_id for p in Payment.query.filter_by(year=year, month=month, is_paid=True).all()}
        for apartment in Apartment.query.all():
            if apartment.id not in paid_ids:
                overdue_apartments[apartment.id] = overdue_apartments.get(apartment.id, 0) + 1

    # List overdue apartments
    defaulters = []
    for apartment_id, overdue_months in sorted(overdue_apartments.items()):
        apartment = Apartment.query.get(apartment_id)
        defaulters.append({'apartment': apartment, 'overdue_months': overdue_months})

    return render_template('ana_sayfa.html',
                           year=year,
                           dues=dues,
                           total_apartments=total_apartments,
                           total_income=total_income,
                           total_expense=total_expense,
                           balance=balance,
                           expected_annual=expected_annual,
                           collection_annual=collection_annual,
                           expected_current=expected_current,
                           collection_current=collection_current,
                           month_count=now.month,
                           total_paid=total_paid,
                           defaulters=defaulters)
