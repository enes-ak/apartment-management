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
        from models import Apartment, DuesConfig, Setting
        from datetime import date

        # Update resident_name for all apartments
        for apartment in Apartment.query.all():
            apartment.resident_name = f'Sakin {apartment.unit_no}'

        # Update dues amount
        config = DuesConfig.query.first()
        config.amount = 500
        config.effective_date = date(2026, 1, 1)

        # Update settings
        Setting.save('apartman_adi', 'Test Apartmani')
        Setting.save('mesaj_sablonu', '{apartman_adi} - {ay_yil}\n{odemeyenler}')

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
