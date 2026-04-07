import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date, datetime
from models import Setting, Notification, Payment, Apartment
from database import db


def is_first_monday(today=None):
    if today is None:
        today = date.today()
    return today.weekday() == 0 and today.day <= 7


def send_email(subject, body):
    email_address = Setting.getir('mail_adresi')
    smtp_server = Setting.getir('smtp_sunucu', 'smtp.gmail.com')
    smtp_port = int(Setting.getir('smtp_port', '587'))
    smtp_password = Setting.getir('smtp_sifre')
    if not email_address or not smtp_password:
        return False
    message = MIMEMultipart()
    message['From'] = email_address
    message['To'] = email_address
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain', 'utf-8'))
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_address, smtp_password)
            server.send_message(message)
        return True
    except Exception:
        return False


def check_dues_reminder():
    today = date.today()
    if not is_first_monday(today):
        return
    year, month = today.year, today.month
    notification = Notification.query.filter_by(yil=year, ay=month).first()
    if notification and notification.gonderildi:
        return
    total_apartments = Apartment.query.count()
    paid = Payment.query.filter_by(year=year, month=month, is_paid=True).count()
    unpaid = total_apartments - paid
    building_name = Setting.getir('apartman_adi', 'Apartman')
    subject = f'{building_name} - Aidat Hatirlatmasi'
    body = (
        f'Aidat toplama zamani geldi!\n\n'
        f'Toplam daire: {total_apartments}\n'
        f'Odenen: {paid}\n'
        f'Odenmeyen: {unpaid}\n\n'
        f'Uygulamayi acarak detaylari gorebilirsiniz.'
    )
    result = send_email(subject, body)
    if notification is None:
        notification = Notification(yil=year, ay=month)
        db.session.add(notification)
    notification.gonderildi = result
    if result:
        notification.gonderim_tarihi = datetime.now()
    db.session.commit()
