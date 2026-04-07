from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from models import Rehber, Log

bp = Blueprint('rehber', __name__, url_prefix='/rehber')


@bp.route('/')
def index():
    gorevliler = Rehber.query.filter_by(kategori='gorevli').order_by(Rehber.sira, Rehber.id).all()
    bilgiler = Rehber.query.filter_by(kategori='bilgi').order_by(Rehber.sira, Rehber.id).all()
    abonelikler = Rehber.query.filter_by(kategori='abonelik').order_by(Rehber.sira, Rehber.id).all()
    return render_template('rehber.html', gorevliler=gorevliler, bilgiler=bilgiler, abonelikler=abonelikler)


@bp.route('/ekle', methods=['POST'])
def ekle():
    kategori = request.form.get('kategori', 'gorevli')
    baslik = request.form.get('baslik', '').strip()
    deger = request.form.get('deger', '').strip()
    telefon = request.form.get('telefon', '').strip()
    iban = request.form.get('iban', '').strip()

    if not baslik:
        flash('Baslik bos olamaz.', 'danger')
        return redirect(url_for('rehber.index'))

    kayit = Rehber(kategori=kategori, baslik=baslik, deger=deger, telefon=telefon, iban=iban)
    db.session.add(kayit)
    db.session.commit()
    etiket = {'gorevli': 'Gorevli', 'bilgi': 'Bilgi', 'abonelik': 'Abonelik'}.get(kategori, 'Kayit')
    Log.kaydet(f'{etiket} eklendi: {baslik}')
    flash(f'{baslik} eklendi.', 'success')
    return redirect(url_for('rehber.index'))


@bp.route('/guncelle/<int:kayit_id>', methods=['POST'])
def guncelle(kayit_id):
    kayit = Rehber.query.get_or_404(kayit_id)
    kayit.baslik = request.form.get('baslik', '').strip() or kayit.baslik
    kayit.deger = request.form.get('deger', '').strip()
    kayit.telefon = request.form.get('telefon', '').strip()
    kayit.iban = request.form.get('iban', '').strip()
    db.session.commit()
    Log.kaydet(f'Rehber guncellendi: {kayit.baslik}')
    flash(f'{kayit.baslik} guncellendi.', 'success')
    return redirect(url_for('rehber.index'))


@bp.route('/sil/<int:kayit_id>', methods=['POST'])
def sil(kayit_id):
    kayit = Rehber.query.get_or_404(kayit_id)
    baslik = kayit.baslik
    db.session.delete(kayit)
    db.session.commit()
    Log.kaydet(f'Rehber silindi: {baslik}')
    flash(f'{baslik} silindi.', 'success')
    return redirect(url_for('rehber.index'))
