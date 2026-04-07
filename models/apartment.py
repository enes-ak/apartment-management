from database import db


class Apartment(db.Model):
    __tablename__ = 'apartments'

    id = db.Column(db.Integer, primary_key=True)
    unit_no = db.Column(db.Integer, nullable=False, unique=True)
    floor = db.Column(db.Integer, nullable=False)
    resident_name = db.Column(db.Text, default='')
    phone = db.Column(db.Text, default='')

    payments = db.relationship('Payment', backref='apartment', lazy=True)

    def __repr__(self):
        return f'<Apartment {self.unit_no}>'
