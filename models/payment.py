from database import db


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartments.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    payment_date = db.Column(db.DateTime, nullable=True)

    __table_args__ = (db.UniqueConstraint('apartment_id', 'year', 'month', name='uq_apartment_year_month'),)

    def __repr__(self):
        return f'<Payment Apartment:{self.apartment_id} {self.year}/{self.month}>'
