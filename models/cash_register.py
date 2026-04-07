from database import db


class CashRegister(db.Model):
    __tablename__ = 'cash_register'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    total_income = db.Column(db.Float, default=0)
    total_expense = db.Column(db.Float, default=0)
    carryover = db.Column(db.Float, default=0)
    balance = db.Column(db.Float, default=0)

    __table_args__ = (db.UniqueConstraint('year', 'month', name='uq_cash_year_month'),)

    def __repr__(self):
        return f'<CashRegister {self.year}/{self.month} Balance:{self.balance}>'
