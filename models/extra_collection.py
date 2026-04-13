from database import db


class ExtraCollection(db.Model):
    __tablename__ = 'extra_collections'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    per_unit_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)

    payments = db.relationship('ExtraPayment', backref='collection', lazy=True,
                               cascade='all, delete-orphan')


class ExtraPayment(db.Model):
    __tablename__ = 'extra_payments'

    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('extra_collections.id'), nullable=False)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartments.id'), nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    payment_date = db.Column(db.DateTime, nullable=True)

    apartment = db.relationship('Apartment', lazy=True)

    __table_args__ = (db.UniqueConstraint('collection_id', 'apartment_id',
                                          name='uq_extra_collection_apartment'),)
