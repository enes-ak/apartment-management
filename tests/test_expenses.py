from models import Expense, ExpenseCategory


def test_expenses_page_load(client):
    response = client.get('/giderler/')
    assert response.status_code == 200
    assert 'Giderler'.encode() in response.data


def test_expense_add(client, db_session):
    category = ExpenseCategory.query.filter_by(category_name='Elektrik').first()
    response = client.post('/giderler/ekle', data={
        'kalem_id': category.id,
        'yil': 2026,
        'ay': 4,
        'tutar': '1500.50',
        'aciklama': 'Nisan elektrik faturasi',
    }, follow_redirects=True)
    assert response.status_code == 200
    expense = Expense.query.filter_by(category_id=category.id, year=2026, month=4).first()
    assert expense is not None
    assert expense.amount == 1500.50


def test_expense_delete(client, db_session):
    category = ExpenseCategory.query.filter_by(category_name='Su').first()
    from database import db
    expense = Expense(category_id=category.id, year=2026, month=4, amount=300, description='')
    db.session.add(expense)
    db.session.commit()
    expense_id = expense.id
    response = client.post(f'/giderler/sil/{expense_id}', follow_redirects=True)
    assert response.status_code == 200
    assert Expense.query.get(expense_id) is None
