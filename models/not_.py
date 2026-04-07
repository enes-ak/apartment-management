from datetime import datetime
from database import db


class AylikNot(db.Model):
    __tablename__ = 'aylik_notlar'

    id = db.Column(db.Integer, primary_key=True)
    yil = db.Column(db.Integer, nullable=False)
    ay = db.Column(db.Integer, nullable=False)
    icerik = db.Column(db.Text, default='')
    guncelleme_tarihi = db.Column(db.DateTime, nullable=True)

    __table_args__ = (db.UniqueConstraint('yil', 'ay', name='uq_not_yil_ay'),)

    def __repr__(self):
        return f'<AylikNot {self.yil}/{self.ay}>'
