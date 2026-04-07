from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from models import Directory, Log

bp = Blueprint('directory', __name__, url_prefix='/rehber')


@bp.route('/')
def index():
    staff = Directory.query.filter_by(category='gorevli').order_by(Directory.sort_order, Directory.id).all()
    info = Directory.query.filter_by(category='bilgi').order_by(Directory.sort_order, Directory.id).all()
    subscriptions = Directory.query.filter_by(category='abonelik').order_by(Directory.sort_order, Directory.id).all()
    return render_template('directory.html', gorevliler=staff, bilgiler=info, abonelikler=subscriptions)


@bp.route('/ekle', methods=['POST'])
def add():
    category = request.form.get('kategori', 'gorevli')
    title = request.form.get('baslik', '').strip()
    value = request.form.get('deger', '').strip()
    phone = request.form.get('telefon', '').strip()
    iban = request.form.get('iban', '').strip()

    if not title:
        flash('Baslik bos olamaz.', 'danger')
        return redirect(url_for('directory.index'))

    entry = Directory(category=category, title=title, value=value, phone=phone, iban=iban)
    db.session.add(entry)
    db.session.commit()
    label = {'gorevli': 'Gorevli', 'bilgi': 'Bilgi', 'abonelik': 'Abonelik'}.get(category, 'Kayit')
    Log.record(f'{label} eklendi: {title}')
    flash(f'{title} eklendi.', 'success')
    return redirect(url_for('directory.index'))


@bp.route('/guncelle/<int:kayit_id>', methods=['POST'])
def update(kayit_id):
    entry = Directory.query.get_or_404(kayit_id)
    entry.title = request.form.get('baslik', '').strip() or entry.title
    entry.value = request.form.get('deger', '').strip()
    entry.phone = request.form.get('telefon', '').strip()
    entry.iban = request.form.get('iban', '').strip()
    db.session.commit()
    Log.record(f'Rehber guncellendi: {entry.title}')
    flash(f'{entry.title} guncellendi.', 'success')
    return redirect(url_for('directory.index'))


@bp.route('/sil/<int:kayit_id>', methods=['POST'])
def delete(kayit_id):
    entry = Directory.query.get_or_404(kayit_id)
    title = entry.title
    db.session.delete(entry)
    db.session.commit()
    Log.record(f'Rehber silindi: {title}')
    flash(f'{title} silindi.', 'success')
    return redirect(url_for('directory.index'))
