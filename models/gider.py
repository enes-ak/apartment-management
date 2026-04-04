from database import db


class GiderKalemi(db.Model):
    __tablename__ = 'gider_kalemleri'

    id = db.Column(db.Integer, primary_key=True)
    kalem_adi = db.Column(db.Text, nullable=False)
    aktif = db.Column(db.Boolean, default=True)

    giderler = db.relationship('Gider', backref='kalem', lazy=True)

    def __repr__(self):
        return f'<GiderKalemi {self.kalem_adi}>'


class Gider(db.Model):
    __tablename__ = 'giderler'

    id = db.Column(db.Integer, primary_key=True)
    kalem_id = db.Column(db.Integer, db.ForeignKey('gider_kalemleri.id'), nullable=False)
    yil = db.Column(db.Integer, nullable=False)
    ay = db.Column(db.Integer, nullable=False)
    tutar = db.Column(db.Float, nullable=False)
    aciklama = db.Column(db.Text, default='')

    def __repr__(self):
        return f'<Gider {self.kalem.kalem_adi if self.kalem else "?"} {self.tutar} TL>'
