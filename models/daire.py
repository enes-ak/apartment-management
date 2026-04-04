from database import db


class Daire(db.Model):
    __tablename__ = 'daireler'

    id = db.Column(db.Integer, primary_key=True)
    daire_no = db.Column(db.Integer, nullable=False, unique=True)
    kat = db.Column(db.Integer, nullable=False)
    sakin_adi = db.Column(db.Text, default='')
    telefon = db.Column(db.Text, default='')

    odemeler = db.relationship('Odeme', backref='daire', lazy=True)

    def __repr__(self):
        return f'<Daire {self.daire_no}>'
