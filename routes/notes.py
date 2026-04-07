from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from models import MonthlyNote, Log

bp = Blueprint('notes', __name__, url_prefix='/notlar')

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan',
    5: 'Mayis', 6: 'Haziran', 7: 'Temmuz', 8: 'Agustos',
    9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}


@bp.route('/')
def index():
    now = datetime.now()
    year = request.args.get('yil', now.year, type=int)
    selected_month = request.args.get('ay', now.month, type=int)

    notes = []
    for month in range(1, 13):
        record = MonthlyNote.query.filter_by(year=year, month=month).first()
        notes.append({
            'month': month,
            'month_name': AY_ISIMLERI[month],
            'content': record.content if record else '',
            'has_content': record is not None and record.content.strip() != '',
            'date': record.updated_at if record else None,
        })

    selected = notes[selected_month - 1]

    return render_template('notes.html', year=year, notes=notes,
                           selected=selected, selected_month=selected_month)


@bp.route('/kaydet', methods=['POST'])
def save():
    year = request.form.get('yil', type=int)
    month = request.form.get('ay', type=int)
    content = request.form.get('icerik', '').strip()

    record = MonthlyNote.query.filter_by(year=year, month=month).first()
    if record:
        record.content = content
        record.updated_at = datetime.now()
    else:
        record = MonthlyNote(year=year, month=month, content=content, updated_at=datetime.now())
        db.session.add(record)
    db.session.commit()
    Log.record(f'{AY_ISIMLERI[month]} {year} notu guncellendi')
    flash(f'{AY_ISIMLERI[month]} {year} notu kaydedildi.', 'success')
    return redirect(url_for('notes.index', yil=year, ay=month))


@bp.route('/sil', methods=['POST'])
def delete():
    year = request.form.get('yil', type=int)
    month = request.form.get('ay', type=int)

    record = MonthlyNote.query.filter_by(year=year, month=month).first()
    if record:
        db.session.delete(record)
        db.session.commit()
        Log.record(f'{AY_ISIMLERI[month]} {year} notu silindi')
        flash(f'{AY_ISIMLERI[month]} {year} notu silindi.', 'success')
    return redirect(url_for('notes.index', yil=year, ay=month))
