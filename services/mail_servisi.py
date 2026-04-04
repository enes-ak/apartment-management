import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date, datetime
from models import Ayar, Bildirim, Odeme, Daire
from database import db


def ilk_pazartesi_mi(tarih=None):
    if tarih is None:
        tarih = date.today()
    return tarih.weekday() == 0 and tarih.day <= 7


def mail_gonder(konu, icerik):
    mail_adresi = Ayar.getir('mail_adresi')
    smtp_sunucu = Ayar.getir('smtp_sunucu', 'smtp.gmail.com')
    smtp_port = int(Ayar.getir('smtp_port', '587'))
    smtp_sifre = Ayar.getir('smtp_sifre')
    if not mail_adresi or not smtp_sifre:
        return False
    mesaj = MIMEMultipart()
    mesaj['From'] = mail_adresi
    mesaj['To'] = mail_adresi
    mesaj['Subject'] = konu
    mesaj.attach(MIMEText(icerik, 'plain', 'utf-8'))
    try:
        with smtplib.SMTP(smtp_sunucu, smtp_port) as server:
            server.starttls()
            server.login(mail_adresi, smtp_sifre)
            server.send_message(mesaj)
        return True
    except Exception:
        return False


def aidat_hatirlatma_kontrol():
    bugun = date.today()
    if not ilk_pazartesi_mi(bugun):
        return
    yil, ay = bugun.year, bugun.month
    bildirim = Bildirim.query.filter_by(yil=yil, ay=ay).first()
    if bildirim and bildirim.gonderildi:
        return
    toplam_daire = Daire.query.count()
    odenen = Odeme.query.filter_by(yil=yil, ay=ay, odendi=True).count()
    odenmeyen = toplam_daire - odenen
    apartman_adi = Ayar.getir('apartman_adi', 'Apartman')
    konu = f'{apartman_adi} - Aidat Hatirlatmasi'
    icerik = (
        f'Aidat toplama zamani geldi!\n\n'
        f'Toplam daire: {toplam_daire}\n'
        f'Odenen: {odenen}\n'
        f'Odenmeyen: {odenmeyen}\n\n'
        f'Uygulamayi acarak detaylari gorebilirsiniz.'
    )
    sonuc = mail_gonder(konu, icerik)
    if bildirim is None:
        bildirim = Bildirim(yil=yil, ay=ay)
        db.session.add(bildirim)
    bildirim.gonderildi = sonuc
    if sonuc:
        bildirim.gonderim_tarihi = datetime.now()
    db.session.commit()
