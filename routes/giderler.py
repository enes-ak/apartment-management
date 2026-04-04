from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from models import GiderKalemi, Gider

bp = Blueprint('giderler', __name__, url_prefix='/giderler')

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan',
    5: 'Mayis', 6: 'Haziran', 7: 'Temmuz', 8: 'Agustos',
    9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}


@bp.route('/')
def index():
    now = datetime.now()
    yil = request.args.get('yil', now.year, type=int)
    ay = request.args.get('ay', now.month, type=int)
    kalemleri = GiderKalemi.query.filter_by(aktif=True).all()
    giderler = Gider.query.filter_by(yil=yil, ay=ay).all()
    toplam = sum(g.tutar for g in giderler)
    return render_template('giderler.html', kalemleri=kalemleri, giderler=giderler,
                           yil=yil, ay=ay, toplam=toplam, ay_isimleri=AY_ISIMLERI)


@bp.route('/ekle', methods=['POST'])
def ekle():
    kalem_id = request.form.get('kalem_id', type=int)
    yil = request.form.get('yil', type=int)
    ay = request.form.get('ay', type=int)
    tutar = request.form.get('tutar', type=float)
    aciklama = request.form.get('aciklama', '')
    gider = Gider(kalem_id=kalem_id, yil=yil, ay=ay, tutar=tutar, aciklama=aciklama)
    db.session.add(gider)
    db.session.commit()
    flash('Gider eklendi.', 'success')
    return redirect(url_for('giderler.index', yil=yil, ay=ay))


@bp.route('/sil/<int:gider_id>', methods=['POST'])
def sil(gider_id):
    gider = Gider.query.get_or_404(gider_id)
    yil, ay = gider.yil, gider.ay
    db.session.delete(gider)
    db.session.commit()
    flash('Gider silindi.', 'success')
    return redirect(url_for('giderler.index', yil=yil, ay=ay))
