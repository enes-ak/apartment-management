from database import db


class Rehber(db.Model):
    __tablename__ = 'rehber'

    id = db.Column(db.Integer, primary_key=True)
    kategori = db.Column(db.String(20), nullable=False)  # gorevli / bilgi
    baslik = db.Column(db.String(100), nullable=False)
    deger = db.Column(db.String(300), default='')
    telefon = db.Column(db.String(20), default='')
    iban = db.Column(db.String(40), default='')
    sira = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Rehber {self.kategori}: {self.baslik}>'
