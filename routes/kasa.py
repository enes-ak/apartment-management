from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Kasa
from services.kasa_servisi import kasa_hesapla, yillik_kasa

bp = Blueprint('kasa', __name__, url_prefix='/kasa')

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan',
    5: 'Mayis', 6: 'Haziran', 7: 'Temmuz', 8: 'Agustos',
    9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}

@bp.route('/')
def index():
    now = datetime.now()
    yil = request.args.get('yil', now.year, type=int)
    kayitlar = yillik_kasa(yil)
    toplam_gelir = sum(k.toplam_gelir for k in kayitlar if k)
    toplam_gider = sum(k.toplam_gider for k in kayitlar if k)
    son_bakiye = 0
    for k in reversed(kayitlar):
        if k:
            son_bakiye = k.bakiye
            break
    return render_template('kasa.html', kayitlar=kayitlar, yil=yil,
                           toplam_gelir=toplam_gelir, toplam_gider=toplam_gider,
                           son_bakiye=son_bakiye, ay_isimleri=AY_ISIMLERI)

@bp.route('/hesapla', methods=['POST'])
def hesapla():
    yil = request.form.get('yil', type=int)
    ay = request.form.get('ay', type=int)
    kasa_hesapla(yil, ay)
    flash(f'{AY_ISIMLERI[ay]} {yil} kasa durumu hesaplandi.', 'success')
    return redirect(url_for('kasa.index', yil=yil))
