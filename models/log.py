from datetime import datetime
from database import db


class Log(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now, nullable=False)
    action = db.Column(db.Text, nullable=False)

    @staticmethod
    def record(action):
        db.session.add(Log(action=action))
        db.session.commit()

    def __repr__(self):
        return f'<Log {self.timestamp} - {self.action}>'
