import os
import shutil
from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from database import db
from models import Ayar, AidatAyari, Daire, GiderKalemi, Log

bp = Blueprint('ayarlar', __name__, url_prefix='/ayarlar')


@bp.route('/')
def index():
    apartman_adi = Ayar.getir('apartman_adi', '')
    mesaj_sablonu = Ayar.getir('mesaj_sablonu', '')
    aidat = AidatAyari.guncel_miktar()
    daireler = Daire.query.order_by(Daire.daire_no).all()
    gider_kalemleri = GiderKalemi.query.all()
    # Yedek dosyalari listele
    yedek_dir = os.path.join(current_app.root_path, 'yedekler')
    yedekler = []
    if os.path.exists(yedek_dir):
        for f in sorted(os.listdir(yedek_dir), reverse=True):
            if f.endswith('.db'):
                yol = os.path.join(yedek_dir, f)
                boyut = os.path.getsize(yol) / 1024  # KB
                yedekler.append({'adi': f, 'boyut': f'{boyut:.0f} KB'})

    return render_template('ayarlar.html',
                           apartman_adi=apartman_adi, mesaj_sablonu=mesaj_sablonu,
                           aidat=aidat, daireler=daireler, gider_kalemleri=gider_kalemleri,
                           yedekler=yedekler)


@bp.route('/genel', methods=['POST'])
def genel_kaydet():
    Ayar.kaydet('apartman_adi', request.form.get('apartman_adi', ''))
    Log.kaydet('Genel ayarlar guncellendi')
    flash('Genel ayarlar kaydedildi.', 'success')
    return redirect(url_for('ayarlar.index'))


@bp.route('/aidat', methods=['POST'])
def aidat_kaydet():
    miktar = float(request.form.get('miktar', 0))
    yeni = AidatAyari(miktar=miktar, gecerlilik_tarihi=date.today())
    db.session.add(yeni)
    db.session.commit()
    Log.kaydet(f'Aidat miktari {miktar:.2f} TL olarak guncellendi')
    flash(f'Aidat miktari {miktar:.2f} TL olarak guncellendi.', 'success')
    return redirect(url_for('ayarlar.index'))


@bp.route('/daire/<int:daire_id>', methods=['POST'])
def daire_kaydet(daire_id):
    daire = Daire.query.get_or_404(daire_id)
    daire.sakin_adi = request.form.get('sakin_adi', '')
    daire.telefon = request.form.get('telefon', '')
    db.session.commit()
    Log.kaydet(f'Daire {daire.daire_no} bilgileri guncellendi')
    flash(f'Daire {daire.daire_no} bilgileri guncellendi.', 'success')
    return redirect(url_for('ayarlar.index'))


@bp.route('/gider-kalemi', methods=['POST'])
def gider_kalemi_ekle():
    kalem_adi = request.form.get('kalem_adi', '').strip()
    if kalem_adi:
        db.session.add(GiderKalemi(kalem_adi=kalem_adi, aktif=True))
        db.session.commit()
        Log.kaydet(f'Gider kalemi eklendi: {kalem_adi}')
        flash(f'"{kalem_adi}" gider kalemi eklendi.', 'success')
    return redirect(url_for('ayarlar.index'))


@bp.route('/gider-kalemi/<int:kalem_id>/toggle', methods=['POST'])
def gider_kalemi_toggle(kalem_id):
    kalem = GiderKalemi.query.get_or_404(kalem_id)
    kalem.aktif = not kalem.aktif
    db.session.commit()
    durum = 'aktif' if kalem.aktif else 'pasif'
    Log.kaydet(f'Gider kalemi "{kalem.kalem_adi}" {durum} yapildi')
    flash(f'"{kalem.kalem_adi}" {durum} yapildi.', 'success')
    return redirect(url_for('ayarlar.index'))


@bp.route('/mesaj-sablonu', methods=['POST'])
def mesaj_sablonu_kaydet():
    sablon = request.form.get('mesaj_sablonu', '')
    Ayar.kaydet('mesaj_sablonu', sablon)
    Log.kaydet('Mesaj sablonu guncellendi')
    flash('Mesaj sablonu kaydedildi.', 'success')
    return redirect(url_for('ayarlar.index'))


@bp.route('/yedekle', methods=['POST'])
def yedekle():
    db_path = os.path.join(current_app.root_path, 'apartman.db')
    yedek_dir = os.path.join(current_app.root_path, 'yedekler')
    os.makedirs(yedek_dir, exist_ok=True)
    tarih = datetime.now().strftime('%Y%m%d_%H%M%S')
    yedek_adi = f'apartman_{tarih}.db'
    yedek_path = os.path.join(yedek_dir, yedek_adi)
    shutil.copy2(db_path, yedek_path)
    Log.kaydet(f'Veritabani yedeklendi: {yedek_adi}')
    flash(f'Yedek olusturuldu: {yedek_adi}', 'success')
    return redirect(url_for('ayarlar.index'))


@bp.route('/yedek-indir/<dosya_adi>')
def yedek_indir(dosya_adi):
    yedek_dir = os.path.join(current_app.root_path, 'yedekler')
    yedek_path = os.path.join(yedek_dir, dosya_adi)
    if os.path.exists(yedek_path):
        return send_file(yedek_path, as_attachment=True, download_name=dosya_adi)
    flash('Yedek dosyasi bulunamadi.', 'danger')
    return redirect(url_for('ayarlar.index'))


@bp.route('/sifirla', methods=['POST'])
def sifirla():
    onay = request.form.get('onay', '')
    if onay != 'DELETE':
        flash('Sifirlama iptal edildi. Onay kelimesi yanlis.', 'danger')
        return redirect(url_for('ayarlar.index'))

    from models import Odeme, Gider, Kasa, Bildirim
    Odeme.query.delete()
    Gider.query.delete()
    Kasa.query.delete()
    Bildirim.query.delete()
    db.session.commit()
    Log.kaydet('TUM KAYITLAR SIFIRLANDI (odemeler, giderler, kasa, bildirimler)')
    flash('Tum odeme, gider, kasa ve bildirim kayitlari sifirlandi. Daire bilgileri ve ayarlar korundu.', 'success')
    return redirect(url_for('ayarlar.index'))
