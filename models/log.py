from datetime import datetime
from database import db


class Log(db.Model):
    __tablename__ = 'loglar'

    id = db.Column(db.Integer, primary_key=True)
    tarih = db.Column(db.DateTime, default=datetime.now, nullable=False)
    eylem = db.Column(db.Text, nullable=False)

    @staticmethod
    def kaydet(eylem):
        db.session.add(Log(eylem=eylem))
        db.session.commit()

    def __repr__(self):
        return f'<Log {self.tarih} - {self.eylem}>'
