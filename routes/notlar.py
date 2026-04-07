from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from models import AylikNot, Log

bp = Blueprint('notlar', __name__, url_prefix='/notlar')

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan',
    5: 'Mayis', 6: 'Haziran', 7: 'Temmuz', 8: 'Agustos',
    9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}


@bp.route('/')
def index():
    now = datetime.now()
    yil = request.args.get('yil', now.year, type=int)
    secili_ay = request.args.get('ay', now.month, type=int)

    notlar = []
    for ay in range(1, 13):
        kayit = AylikNot.query.filter_by(yil=yil, ay=ay).first()
        notlar.append({
            'ay': ay,
            'ay_adi': AY_ISIMLERI[ay],
            'icerik': kayit.icerik if kayit else '',
            'var': kayit is not None and kayit.icerik.strip() != '',
            'tarih': kayit.guncelleme_tarihi if kayit else None,
        })

    secili = notlar[secili_ay - 1]

    return render_template('notlar.html', yil=yil, notlar=notlar,
                           secili=secili, secili_ay=secili_ay)


@bp.route('/kaydet', methods=['POST'])
def kaydet():
    yil = request.form.get('yil', type=int)
    ay = request.form.get('ay', type=int)
    icerik = request.form.get('icerik', '').strip()

    kayit = AylikNot.query.filter_by(yil=yil, ay=ay).first()
    if kayit:
        kayit.icerik = icerik
        kayit.guncelleme_tarihi = datetime.now()
    else:
        kayit = AylikNot(yil=yil, ay=ay, icerik=icerik, guncelleme_tarihi=datetime.now())
        db.session.add(kayit)
    db.session.commit()
    Log.kaydet(f'{AY_ISIMLERI[ay]} {yil} notu guncellendi')
    flash(f'{AY_ISIMLERI[ay]} {yil} notu kaydedildi.', 'success')
    return redirect(url_for('notlar.index', yil=yil, ay=ay))


@bp.route('/sil', methods=['POST'])
def sil():
    yil = request.form.get('yil', type=int)
    ay = request.form.get('ay', type=int)

    kayit = AylikNot.query.filter_by(yil=yil, ay=ay).first()
    if kayit:
        db.session.delete(kayit)
        db.session.commit()
        Log.kaydet(f'{AY_ISIMLERI[ay]} {yil} notu silindi')
        flash(f'{AY_ISIMLERI[ay]} {yil} notu silindi.', 'success')
    return redirect(url_for('notlar.index', yil=yil, ay=ay))
