from database import db


class Ayar(db.Model):
    __tablename__ = 'ayarlar'

    id = db.Column(db.Integer, primary_key=True)
    anahtar = db.Column(db.Text, unique=True, nullable=False)
    deger = db.Column(db.Text, default='')

    @staticmethod
    def getir(anahtar, varsayilan=''):
        ayar = Ayar.query.filter_by(anahtar=anahtar).first()
        return ayar.deger if ayar else varsayilan

    @staticmethod
    def kaydet(anahtar, deger):
        ayar = Ayar.query.filter_by(anahtar=anahtar).first()
        if ayar:
            ayar.deger = deger
        else:
            ayar = Ayar(anahtar=anahtar, deger=deger)
            db.session.add(ayar)
        db.session.commit()


class AidatAyari(db.Model):
    __tablename__ = 'aidat_ayarlari'

    id = db.Column(db.Integer, primary_key=True)
    miktar = db.Column(db.Float, nullable=False)
    gecerlilik_tarihi = db.Column(db.Date, nullable=False)

    @staticmethod
    def guncel_miktar():
        from datetime import date
        ayar = AidatAyari.query.filter(
            AidatAyari.gecerlilik_tarihi <= date.today()
        ).order_by(AidatAyari.gecerlilik_tarihi.desc()).first()
        return ayar.miktar if ayar else 0


class Bildirim(db.Model):
    __tablename__ = 'bildirimler'

    id = db.Column(db.Integer, primary_key=True)
    yil = db.Column(db.Integer, nullable=False)
    ay = db.Column(db.Integer, nullable=False)
    gonderildi = db.Column(db.Boolean, default=False)
    gonderim_tarihi = db.Column(db.DateTime, nullable=True)

    __table_args__ = (db.UniqueConstraint('yil', 'ay', name='uq_bildirim_yil_ay'),)
