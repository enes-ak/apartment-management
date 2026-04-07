from datetime import datetime
from database import db


class MonthlyNote(db.Model):
    __tablename__ = 'monthly_notes'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, default='')
    updated_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (db.UniqueConstraint('year', 'month', name='uq_note_year_month'),)

    def __repr__(self):
        return f'<MonthlyNote {self.year}/{self.month}>'
