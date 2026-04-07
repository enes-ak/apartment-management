from unittest.mock import patch, MagicMock
from models import Notification, Setting
from database import db as _db


def test_notification_record_create(db_session):
    n = Notification(year=2026, month=4, is_sent=True)
    _db.session.add(n)
    _db.session.commit()
    assert Notification.query.filter_by(year=2026, month=4).first().is_sent is True


def test_mail_check_first_monday(app):
    from services.mail_service import is_first_monday
    from datetime import date
    assert is_first_monday(date(2026, 4, 6)) is True
    assert is_first_monday(date(2026, 4, 13)) is False
    assert is_first_monday(date(2026, 4, 7)) is False


@patch('services.mail_service.smtplib')
def test_send_email(mock_smtp, db_session):
    Setting.save('mail_adresi', 'test@test.com')
    Setting.save('smtp_sunucu', 'smtp.test.com')
    Setting.save('smtp_port', '587')
    Setting.save('smtp_sifre', 'sifre123')
    from services.mail_service import send_email
    mock_server = MagicMock()
    mock_smtp.SMTP.return_value.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp.SMTP.return_value.__exit__ = MagicMock(return_value=False)
    result = send_email('Test Konu', 'Test icerik')
    assert result is True
