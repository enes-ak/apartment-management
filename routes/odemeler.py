from datetime import datetime
from flask import Blueprint, render_template, request, send_file
from database import db
from models import Daire, Odeme, AidatAyari, Log
from services.kasa_servisi import kasa_hesapla
from services.rapor_servisi import daire_rapor_pdf

bp = Blueprint('odemeler', __name__, url_prefix='/odemeler')

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
    daireler = Daire.query.order_by(Daire.daire_no).all()
    aidat = AidatAyari.guncel_miktar()
    odeme_durumlari = {}
    for daire in daireler:
        odeme = Odeme.query.filter_by(daire_id=daire.id, yil=yil, ay=ay).first()
        odeme_durumlari[daire.id] = odeme
    toplam_daire = len(daireler)
    odenen = sum(1 for o in odeme_durumlari.values() if o and o.odendi)
    odenmeyen = toplam_daire - odenen
    return render_template('odemeler.html', daireler=daireler, odeme_durumlari=odeme_durumlari,
                           yil=yil, ay=ay, aidat=aidat, ay_isimleri=AY_ISIMLERI,
                           toplam_daire=toplam_daire, odenen=odenen, odenmeyen=odenmeyen)

@bp.route('/toggle/<int:daire_id>/<int:yil>/<int:ay>', methods=['POST'])
def toggle(daire_id, yil, ay):
    odeme = Odeme.query.filter_by(daire_id=daire_id, yil=yil, ay=ay).first()
    if odeme is None:
        odeme = Odeme(daire_id=daire_id, yil=yil, ay=ay, odendi=True, odeme_tarihi=datetime.now())
        db.session.add(odeme)
    else:
        odeme.odendi = not odeme.odendi
        odeme.odeme_tarihi = datetime.now() if odeme.odendi else None
    db.session.commit()
    kasa_hesapla(yil, ay)
    daire = Daire.query.get(daire_id)
    durum = 'odendi' if odeme.odendi else 'geri alindi'
    Log.kaydet(f'Daire {daire.daire_no} - {AY_ISIMLERI[ay]} {yil} aidat {durum}')
    return render_template('parcalar/odeme_satir.html', daire=daire, odeme=odeme, yil=yil, ay=ay, ay_isimleri=AY_ISIMLERI)

@bp.route('/toplu/<int:daire_id>/<int:yil>', methods=['POST'])
def toplu_ode(daire_id, yil):
    from flask import redirect, url_for, flash
    secilen_aylar = request.form.getlist('aylar', type=int)
    if not secilen_aylar:
        flash('Hicbir ay secilmedi.', 'warning')
        return redirect(url_for('odemeler.index', yil=yil, ay=request.args.get('ay', datetime.now().month, type=int)))

    for ay in secilen_aylar:
        odeme = Odeme.query.filter_by(daire_id=daire_id, yil=yil, ay=ay).first()
        if odeme is None:
            odeme = Odeme(daire_id=daire_id, yil=yil, ay=ay, odendi=True, odeme_tarihi=datetime.now())
            db.session.add(odeme)
        elif not odeme.odendi:
            odeme.odendi = True
            odeme.odeme_tarihi = datetime.now()
    db.session.commit()
    for ay in set(secilen_aylar):
        kasa_hesapla(yil, ay)
    daire = Daire.query.get(daire_id)
    Log.kaydet(f'Daire {daire.daire_no} - {len(secilen_aylar)} ay toplu odeme kaydedildi ({yil})')
    flash(f'Daire {daire.daire_no} - {len(secilen_aylar)} ay odeme kaydedildi.', 'success')
    return redirect(url_for('odemeler.index', yil=yil, ay=request.args.get('ay', datetime.now().month, type=int)))


@bp.route('/daire/<int:daire_id>')
def daire_detay(daire_id):
    daire = Daire.query.get_or_404(daire_id)
    aidat = AidatAyari.guncel_miktar()
    now = datetime.now()
    yil = request.args.get('yil', now.year, type=int)

    # Yilin tum aylarini olustur (bulundugumuz yil ise bugunki aya kadar)
    son_ay = now.month if yil == now.year else 12
    aylik_durum = []
    odenen_sayisi = 0
    gecikmis_sayisi = 0

    for ay in range(1, 13):
        odeme = Odeme.query.filter_by(daire_id=daire_id, yil=yil, ay=ay).first()
        odendi = odeme.odendi if odeme else False
        gecikmi = (not odendi) and (ay <= son_ay)

        aylik_durum.append({
            'ay': ay,
            'ay_adi': AY_ISIMLERI[ay],
            'odendi': odendi,
            'odeme_tarihi': odeme.odeme_tarihi if odeme and odeme.odendi else None,
            'gecikmis': gecikmi,
        })

        if odendi:
            odenen_sayisi += 1
        if gecikmi:
            gecikmis_sayisi += 1

    odenmeyen_sayisi = 12 - odenen_sayisi
    yillik_toplam = 12 * aidat
    odenen_tutar = odenen_sayisi * aidat
    kalan_tutar = odenmeyen_sayisi * aidat
    gecikmis_tutar = gecikmis_sayisi * aidat

    return render_template('daire_detay.html', daire=daire, aylik_durum=aylik_durum,
                           aidat=aidat, yil=yil, son_ay=son_ay,
                           odenen_sayisi=odenen_sayisi, odenmeyen_sayisi=odenmeyen_sayisi,
                           gecikmis_sayisi=gecikmis_sayisi,
                           yillik_toplam=yillik_toplam, odenen_tutar=odenen_tutar,
                           kalan_tutar=kalan_tutar, gecikmis_tutar=gecikmis_tutar,
                           ay_isimleri=AY_ISIMLERI)


@bp.route('/daire-rapor/<int:daire_id>/<int:yil>')
def daire_rapor(daire_id, yil):
    daire = Daire.query.get_or_404(daire_id)
    output = daire_rapor_pdf(daire_id, yil)
    dosya_adi = f'daire_{daire.daire_no}_{yil}_odeme_raporu.pdf'
    return send_file(output, mimetype='application/pdf', as_attachment=True, download_name=dosya_adi)
