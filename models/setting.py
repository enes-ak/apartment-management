from database import db


class Setting(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Text, unique=True, nullable=False)
    value = db.Column(db.Text, default='')

    @staticmethod
    def get(key, default=''):
        setting = Setting.query.filter_by(key=key).first()
        return setting.value if setting else default

    @staticmethod
    def save(key, value):
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value)
            db.session.add(setting)
        db.session.commit()


class DuesConfig(db.Model):
    __tablename__ = 'dues_config'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    effective_date = db.Column(db.Date, nullable=False)

    @staticmethod
    def current_amount():
        from datetime import date
        config = DuesConfig.query.filter(
            DuesConfig.effective_date <= date.today()
        ).order_by(DuesConfig.effective_date.desc(), DuesConfig.id.desc()).first()
        return config.amount if config else 0


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    is_sent = db.Column(db.Boolean, default=False)
    sent_date = db.Column(db.DateTime, nullable=True)

    __table_args__ = (db.UniqueConstraint('year', 'month', name='uq_notification_year_month'),)
