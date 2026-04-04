from database import db


class Kasa(db.Model):
    __tablename__ = 'kasa'

    id = db.Column(db.Integer, primary_key=True)
    yil = db.Column(db.Integer, nullable=False)
    ay = db.Column(db.Integer, nullable=False)
    toplam_gelir = db.Column(db.Float, default=0)
    toplam_gider = db.Column(db.Float, default=0)
    devir = db.Column(db.Float, default=0)
    bakiye = db.Column(db.Float, default=0)

    __table_args__ = (db.UniqueConstraint('yil', 'ay', name='uq_kasa_yil_ay'),)

    def __repr__(self):
        return f'<Kasa {self.yil}/{self.ay} Bakiye:{self.bakiye}>'
