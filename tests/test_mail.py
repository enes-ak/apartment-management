from unittest.mock import patch, MagicMock
from models import Bildirim, Ayar
from database import db as _db


def test_bildirim_kaydi_olustur(db_session):
    b = Bildirim(yil=2026, ay=4, gonderildi=True)
    _db.session.add(b)
    _db.session.commit()
    assert Bildirim.query.filter_by(yil=2026, ay=4).first().gonderildi is True


def test_mail_kontrol_ilk_pazartesi(app):
    from services.mail_servisi import ilk_pazartesi_mi
    from datetime import date
    assert ilk_pazartesi_mi(date(2026, 4, 6)) is True
    assert ilk_pazartesi_mi(date(2026, 4, 13)) is False
    assert ilk_pazartesi_mi(date(2026, 4, 7)) is False


@patch('services.mail_servisi.smtplib')
def test_mail_gonder(mock_smtp, db_session):
    Ayar.kaydet('mail_adresi', 'test@test.com')
    Ayar.kaydet('smtp_sunucu', 'smtp.test.com')
    Ayar.kaydet('smtp_port', '587')
    Ayar.kaydet('smtp_sifre', 'sifre123')
    from services.mail_servisi import mail_gonder
    mock_server = MagicMock()
    mock_smtp.SMTP.return_value.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp.SMTP.return_value.__exit__ = MagicMock(return_value=False)
    sonuc = mail_gonder('Test Konu', 'Test icerik')
    assert sonuc is True


