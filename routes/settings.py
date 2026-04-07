import os
import shutil
from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from database import db
from models import Setting, DuesConfig, Apartment, ExpenseCategory, Log

bp = Blueprint('settings', __name__, url_prefix='/ayarlar')


@bp.route('/')
def index():
    building_name = Setting.get('apartman_adi', '')
    message_template = Setting.get('mesaj_sablonu', '')
    dues = DuesConfig.current_amount()
    apartments = Apartment.query.order_by(Apartment.unit_no).all()
    expense_categories = ExpenseCategory.query.all()
    # List backup files
    backup_dir = os.path.join(current_app.root_path, 'yedekler')
    backups = []
    if os.path.exists(backup_dir):
        for f in sorted(os.listdir(backup_dir), reverse=True):
            if f.endswith('.db'):
                path = os.path.join(backup_dir, f)
                size = os.path.getsize(path) / 1024  # KB
                backups.append({'name': f, 'size': f'{size:.0f} KB'})

    return render_template('ayarlar.html',
                           building_name=building_name, message_template=message_template,
                           dues=dues, apartments=apartments, expense_categories=expense_categories,
                           backups=backups)


@bp.route('/genel', methods=['POST'])
def save_general():
    Setting.save('apartman_adi', request.form.get('apartman_adi', ''))
    Log.record('Genel ayarlar guncellendi')
    flash('Genel ayarlar kaydedildi.', 'success')
    return redirect(url_for('settings.index'))


@bp.route('/aidat', methods=['POST'])
def save_dues():
    amount = float(request.form.get('miktar', 0))
    new_config = DuesConfig(amount=amount, effective_date=date.today())
    db.session.add(new_config)
    db.session.commit()
    Log.record(f'Aidat miktari {amount:.2f} TL olarak guncellendi')
    flash(f'Aidat miktari {amount:.2f} TL olarak guncellendi.', 'success')
    return redirect(url_for('settings.index'))


@bp.route('/daire/<int:daire_id>', methods=['POST'])
def save_apartment(daire_id):
    apartment = Apartment.query.get_or_404(daire_id)
    apartment.resident_name = request.form.get('sakin_adi', '')
    apartment.phone = request.form.get('telefon', '')
    db.session.commit()
    Log.record(f'Daire {apartment.unit_no} bilgileri guncellendi')
    flash(f'Daire {apartment.unit_no} bilgileri guncellendi.', 'success')
    return redirect(url_for('settings.index'))


@bp.route('/gider-kalemi', methods=['POST'])
def add_expense_category():
    category_name = request.form.get('kalem_adi', '').strip()
    if category_name:
        db.session.add(ExpenseCategory(category_name=category_name, is_active=True))
        db.session.commit()
        Log.record(f'Gider kalemi eklendi: {category_name}')
        flash(f'"{category_name}" gider kalemi eklendi.', 'success')
    return redirect(url_for('settings.index'))


@bp.route('/gider-kalemi/<int:kalem_id>/toggle', methods=['POST'])
def toggle_expense_category(kalem_id):
    category = ExpenseCategory.query.get_or_404(kalem_id)
    category.is_active = not category.is_active
    db.session.commit()
    status = 'aktif' if category.is_active else 'pasif'
    Log.record(f'Gider kalemi "{category.category_name}" {status} yapildi')
    flash(f'"{category.category_name}" {status} yapildi.', 'success')
    return redirect(url_for('settings.index'))


@bp.route('/mesaj-sablonu', methods=['POST'])
def save_message_template():
    template = request.form.get('mesaj_sablonu', '')
    Setting.save('mesaj_sablonu', template)
    Log.record('Mesaj sablonu guncellendi')
    flash('Mesaj sablonu kaydedildi.', 'success')
    return redirect(url_for('settings.index'))


@bp.route('/yedekle', methods=['POST'])
def backup():
    db_path = os.path.join(current_app.root_path, 'apartman.db')
    backup_dir = os.path.join(current_app.root_path, 'yedekler')
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'apartman_{timestamp}.db'
    backup_path = os.path.join(backup_dir, backup_name)
    shutil.copy2(db_path, backup_path)
    Log.record(f'Veritabani yedeklendi: {backup_name}')
    flash(f'Yedek olusturuldu: {backup_name}', 'success')
    return redirect(url_for('settings.index'))


@bp.route('/yedek-indir/<dosya_adi>')
def download_backup(dosya_adi):
    backup_dir = os.path.join(current_app.root_path, 'yedekler')
    backup_path = os.path.join(backup_dir, dosya_adi)
    if os.path.exists(backup_path):
        return send_file(backup_path, as_attachment=True, download_name=dosya_adi)
    flash('Yedek dosyasi bulunamadi.', 'danger')
    return redirect(url_for('settings.index'))


@bp.route('/sifirla', methods=['POST'])
def reset():
    confirmation = request.form.get('onay', '')
    if confirmation != 'DELETE':
        flash('Sifirlama iptal edildi. Onay kelimesi yanlis.', 'danger')
        return redirect(url_for('settings.index'))

    from models import Payment, Expense, CashRegister, Notification
    Payment.query.delete()
    Expense.query.delete()
    CashRegister.query.delete()
    Notification.query.delete()
    db.session.commit()
    Log.record('TUM KAYITLAR SIFIRLANDI (odemeler, giderler, kasa, bildirimler)')
    flash('Tum odeme, gider, kasa ve bildirim kayitlari sifirlandi. Daire bilgileri ve ayarlar korundu.', 'success')
    return redirect(url_for('settings.index'))
