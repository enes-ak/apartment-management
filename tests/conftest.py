import pytest
from config import Config
from app import create_app
from database import db as _db


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True


@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        # init_db already created tables and default data.
        # Update the seeded data to match test expectations.
        from models import Daire, AidatAyari, Ayar
        from datetime import date

        # Update sakin_adi for all daires
        for daire in Daire.query.all():
            daire.sakin_adi = f'Sakin {daire.daire_no}'

        # Update aidat miktar
        ayar = AidatAyari.query.first()
        ayar.miktar = 500
        ayar.gecerlilik_tarihi = date(2026, 1, 1)

        # Update ayarlar
        Ayar.kaydet('apartman_adi', 'Test Apartmani')
        Ayar.kaydet('mesaj_sablonu', '{apartman_adi} - {ay_yil}\n{odemeyenler}')

        _db.session.commit()

        yield app

        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(app):
    with app.app_context():
        yield _db.session
