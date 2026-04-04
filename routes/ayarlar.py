from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from models import Ayar, AidatAyari, Daire, GiderKalemi

bp = Blueprint('ayarlar', __name__, url_prefix='/ayarlar')


@bp.route('/')
def index():
    apartman_adi = Ayar.getir('apartman_adi', '')
    mail_adresi = Ayar.getir('mail_adresi', '')
    smtp_sunucu = Ayar.getir('smtp_sunucu', 'smtp.gmail.com')
    smtp_port = Ayar.getir('smtp_port', '587')
    smtp_sifre = Ayar.getir('smtp_sifre', '')
    mesaj_sablonu = Ayar.getir('mesaj_sablonu', '')
    aidat = AidatAyari.guncel_miktar()
    daireler = Daire.query.order_by(Daire.daire_no).all()
    gider_kalemleri = GiderKalemi.query.all()
    return render_template('ayarlar.html',
                           apartman_adi=apartman_adi, mail_adresi=mail_adresi,
                           smtp_sunucu=smtp_sunucu, smtp_port=smtp_port,
                           smtp_sifre=smtp_sifre, mesaj_sablonu=mesaj_sablonu,
                           aidat=aidat, daireler=daireler, gider_kalemleri=gider_kalemleri)


@bp.route('/genel', methods=['POST'])
def genel_kaydet():
    Ayar.kaydet('apartman_adi', request.form.get('apartman_adi', ''))
    Ayar.kaydet('mail_adresi', request.form.get('mail_adresi', ''))
    Ayar.kaydet('smtp_sunucu', request.form.get('smtp_sunucu', ''))
    Ayar.kaydet('smtp_port', request.form.get('smtp_port', ''))
    Ayar.kaydet('smtp_sifre', request.form.get('smtp_sifre', ''))
    flash('Genel ayarlar kaydedildi.', 'success')
    return redirect(url_for('ayarlar.index'))


@bp.route('/aidat', methods=['POST'])
def aidat_kaydet():
    miktar = float(request.form.get('miktar', 0))
    yeni = AidatAyari(miktar=miktar, gecerlilik_tarihi=date.today())
    db.session.add(yeni)
    db.session.commit()
    flash(f'Aidat miktari {miktar:.2f} TL olarak guncellendi.', 'success')
    return redirect(url_for('ayarlar.index'))


@bp.route('/daire/<int:daire_id>', methods=['POST'])
def daire_kaydet(daire_id):
    daire = Daire.query.get_or_404(daire_id)
    daire.sakin_adi = request.form.get('sakin_adi', '')
    daire.telefon = request.form.get('telefon', '')
    db.session.commit()
    flash(f'Daire {daire.daire_no} bilgileri guncellendi.', 'success')
    return redirect(url_for('ayarlar.index'))


@bp.route('/gider-kalemi', methods=['POST'])
def gider_kalemi_ekle():
    kalem_adi = request.form.get('kalem_adi', '').strip()
    if kalem_adi:
        db.session.add(GiderKalemi(kalem_adi=kalem_adi, aktif=True))
        db.session.commit()
        flash(f'"{kalem_adi}" gider kalemi eklendi.', 'success')
    return redirect(url_for('ayarlar.index'))


@bp.route('/gider-kalemi/<int:kalem_id>/toggle', methods=['POST'])
def gider_kalemi_toggle(kalem_id):
    kalem = GiderKalemi.query.get_or_404(kalem_id)
    kalem.aktif = not kalem.aktif
    db.session.commit()
    durum = 'aktif' if kalem.aktif else 'pasif'
    flash(f'"{kalem.kalem_adi}" {durum} yapildi.', 'success')
    return redirect(url_for('ayarlar.index'))


@bp.route('/test-mail', methods=['POST'])
def test_mail():
    from services.mail_servisi import mail_gonder
    sonuc = mail_gonder('Test Mail - Apartman Yonetimi', 'Bu bir test mailidir. Mail ayarlariniz dogru calisiyor.')
    if sonuc:
        flash('Test maili basariyla gonderildi!', 'success')
    else:
        flash('Mail gonderilemedi. SMTP ayarlarinizi kontrol edin.', 'danger')
    return redirect(url_for('ayarlar.index'))


@bp.route('/mesaj-sablonu', methods=['POST'])
def mesaj_sablonu_kaydet():
    sablon = request.form.get('mesaj_sablonu', '')
    Ayar.kaydet('mesaj_sablonu', sablon)
    flash('Mesaj sablonu kaydedildi.', 'success')
    return redirect(url_for('ayarlar.index'))
