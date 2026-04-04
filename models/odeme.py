from database import db


class Odeme(db.Model):
    __tablename__ = 'odemeler'

    id = db.Column(db.Integer, primary_key=True)
    daire_id = db.Column(db.Integer, db.ForeignKey('daireler.id'), nullable=False)
    yil = db.Column(db.Integer, nullable=False)
    ay = db.Column(db.Integer, nullable=False)
    odendi = db.Column(db.Boolean, default=False)
    odeme_tarihi = db.Column(db.DateTime, nullable=True)

    __table_args__ = (db.UniqueConstraint('daire_id', 'yil', 'ay', name='uq_daire_yil_ay'),)

    def __repr__(self):
        return f'<Odeme Daire:{self.daire_id} {self.yil}/{self.ay}>'
