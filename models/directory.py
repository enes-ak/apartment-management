from database import db


class Directory(db.Model):
    __tablename__ = 'directory'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(20), nullable=False)  # gorevli / bilgi
    title = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(300), default='')
    phone = db.Column(db.String(20), default='')
    iban = db.Column(db.String(40), default='')
    sort_order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Directory {self.category}: {self.title}>'
