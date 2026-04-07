from database import db


class ExpenseCategory(db.Model):
    __tablename__ = 'expense_categories'

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    expenses = db.relationship('Expense', backref='category', lazy=True)

    def __repr__(self):
        return f'<ExpenseCategory {self.category_name}>'


class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, default='')

    def __repr__(self):
        return f'<Expense {self.category.category_name if self.category else "?"} {self.amount} TL>'
