from datetime import datetime
from flask import Blueprint, render_template, request
from models import Daire, Odeme, Ayar, AidatAyari

bp = Blueprint('mesajlar', __name__, url_prefix='/mesajlar')

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan',
    5: 'Mayis', 6: 'Haziran', 7: 'Temmuz', 8: 'Agustos',
    9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}

@bp.route('/')
def index():
    now = datetime.now()
    return render_template('mesajlar.html', yil=now.year, ay=now.month, ay_isimleri=AY_ISIMLERI)

@bp.route('/olustur')
def olustur():
    yil = request.args.get('yil', type=int)
    ay = request.args.get('ay', type=int)
    tur = request.args.get('tur', 'odemeyenler')
    aidat = AidatAyari.guncel_miktar()
    apartman_adi = Ayar.getir('apartman_adi', 'Apartman')
    sablon = Ayar.getir('mesaj_sablonu', '')
    ay_yil = f'{AY_ISIMLERI[ay]} {yil}'

    if tur == 'genel':
        # Genel hatirlatma: tum daireleri listele
        daireler = Daire.query.order_by(Daire.daire_no).all()
    else:
        # Sadece odemeyenler
        odenen_idler = {o.daire_id for o in Odeme.query.filter_by(yil=yil, ay=ay, odendi=True).all()}
        if odenen_idler:
            daireler = Daire.query.filter(~Daire.id.in_(odenen_idler)).order_by(Daire.daire_no).all()
        else:
            daireler = Daire.query.order_by(Daire.daire_no).all()

    satirlar = []
    for d in daireler:
        satirlar.append(f'- Daire {d.daire_no}')
    odemeyenler_metni = '\n'.join(satirlar) if satirlar else '- Herkes odemis!'

    mesaj = sablon.format(
        apartman_adi=apartman_adi,
        ay_yil=ay_yil,
        miktar=f'{aidat:.2f}',
        odemeyenler=odemeyenler_metni,
    )
    return render_template('parcalar/mesaj_onizleme.html', mesaj=mesaj, daireler=daireler,
                           yil=yil, ay=ay, ay_adi=AY_ISIMLERI[ay])
