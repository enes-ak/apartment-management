from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import CashRegister, Payment, Expense, ExpenseCategory, Apartment, DuesConfig
from database import db
from services.cash_service import calculate_cash

bp = Blueprint('cash_register', __name__, url_prefix='/kasa')


@bp.route('/')
def index():
    now = datetime.now()
    year = request.args.get('yil', now.year, type=int)

    dues = DuesConfig.current_amount()
    total_apartments = Apartment.query.count()

    # Total income: all paid dues in the year
    total_paid = Payment.query.filter_by(year=year, is_paid=True).count()
    total_income = total_paid * dues

    # Total expense: all expenses in the year
    expenses = Expense.query.filter_by(year=year).all()
    total_expense = sum(e.amount for e in expenses)

    # Balance
    balance = total_income - total_expense

    # Expense breakdown (by category)
    expense_breakdown = {}
    for e in expenses:
        category_name = e.category.category_name
        expense_breakdown[category_name] = expense_breakdown.get(category_name, 0) + e.amount

    # Collection rate
    expected_income = total_apartments * 12 * dues
    collection_rate = (total_paid / (total_apartments * 12) * 100) if total_apartments > 0 else 0

    return render_template('cash_register.html',
                           year=year,
                           dues=dues,
                           total_apartments=total_apartments,
                           total_paid=total_paid,
                           total_income=total_income,
                           total_expense=total_expense,
                           balance=balance,
                           expected_income=expected_income,
                           collection_rate=collection_rate,
                           expense_distribution=expense_breakdown)
