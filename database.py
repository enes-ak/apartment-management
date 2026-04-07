from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Create tables and seed default data."""
    with app.app_context():
        from models import Apartment, DuesConfig, ExpenseCategory, Setting
        db.create_all()

        # Create 12 apartments if none exist
        if Apartment.query.count() == 0:
            for i in range(1, 13):
                apartment = Apartment(unit_no=i, floor=(i - 1) // 2 + 1, resident_name='', phone='')
                db.session.add(apartment)

        # Default dues config
        if DuesConfig.query.count() == 0:
            from datetime import date
            config = DuesConfig(amount=0, effective_date=date.today())
            db.session.add(config)

        # Default expense categories
        if ExpenseCategory.query.count() == 0:
            for name in ['Elektrik', 'Su', 'Temizlik', 'Asansor Bakim']:
                db.session.add(ExpenseCategory(category_name=name, is_active=True))

        # Default settings
        default_settings = {
            'apartman_adi': 'Apartman',
            'mail_adresi': '',
            'smtp_sunucu': 'smtp.gmail.com',
            'smtp_port': '587',
            'smtp_sifre': '',
            'mesaj_sablonu': (
                '{apartman_adi} - {ay_yil} Aidat Bildirimi\n\n'
                'Sayin Komsularimiz,\n\n'
                '{ay_yil} aidatlari icin odeme zamani gelmistir.\n'
                'Aidat tutari: {miktar} TL\n\n'
                'Henuz odeme yapmayan daireler:\n{odemeyenler}\n\n'
                'Odemenizi en kisa surede yapmanizi rica ederiz.\n\n'
                'Tesekkurler,\nApartman Yonetimi'
            ),
        }
        for key, value in default_settings.items():
            if not Setting.query.filter_by(key=key).first():
                db.session.add(Setting(key=key, value=value))

        db.session.commit()
