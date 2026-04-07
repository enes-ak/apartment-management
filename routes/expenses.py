from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from models import ExpenseCategory, Expense, Log
from services.cash_service import calculate_cash

bp = Blueprint('expenses', __name__, url_prefix='/giderler')

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan',
    5: 'Mayis', 6: 'Haziran', 7: 'Temmuz', 8: 'Agustos',
    9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}


@bp.route('/')
def index():
    now = datetime.now()
    year = request.args.get('yil', now.year, type=int)
    month = request.args.get('ay', now.month, type=int)
    categories = ExpenseCategory.query.filter_by(is_active=True).all()
    expenses = Expense.query.filter_by(year=year, month=month).all()
    total = sum(e.amount for e in expenses)
    return render_template('giderler.html', categories=categories, expenses=expenses,
                           year=year, month=month, total=total, MONTH_NAMES=AY_ISIMLERI)


@bp.route('/ekle', methods=['POST'])
def add():
    category_id = request.form.get('kalem_id', type=int)
    year = request.form.get('yil', type=int)
    month = request.form.get('ay', type=int)
    amount = request.form.get('tutar', type=float)
    description = request.form.get('aciklama', '')
    expense = Expense(category_id=category_id, year=year, month=month, amount=amount, description=description)
    db.session.add(expense)
    db.session.commit()
    calculate_cash(year, month)
    Log.record(f'Gider eklendi: {expense.category.category_name} - {amount:.2f} TL ({AY_ISIMLERI[month]} {year})')
    flash('Gider eklendi.', 'success')
    return redirect(url_for('expenses.index', yil=year, ay=month))


@bp.route('/sil/<int:gider_id>', methods=['POST'])
def delete(gider_id):
    expense = Expense.query.get_or_404(gider_id)
    year, month = expense.year, expense.month
    category_name = expense.category.category_name
    amount = expense.amount
    db.session.delete(expense)
    db.session.commit()
    calculate_cash(year, month)
    Log.record(f'Gider silindi: {category_name} - {amount:.2f} TL ({AY_ISIMLERI[month]} {year})')
    flash('Gider silindi.', 'success')
    return redirect(url_for('expenses.index', yil=year, ay=month))
