from datetime import datetime
from flask import Blueprint, render_template, request, send_file
from services import rapor_servisi

bp = Blueprint('raporlar', __name__, url_prefix='/raporlar')

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan', 5: 'Mayis', 6: 'Haziran',
    7: 'Temmuz', 8: 'Agustos', 9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}
RAPOR_TURLERI = {
    'aylik_ozet': 'Aylik Ozet Raporu',
    'odeme_durumu': 'Odeme Durumu Raporu',
    'gider_detay': 'Gider Detay Raporu',
    'yillik_ozet': 'Yillik Ozet Raporu',
}


@bp.route('/')
def index():
    now = datetime.now()
    return render_template('raporlar.html', yil=now.year, ay=now.month,
                           ay_isimleri=AY_ISIMLERI, rapor_turleri=RAPOR_TURLERI)


@bp.route('/olustur')
def olustur():
    tur = request.args.get('tur')
    fmt = request.args.get('format', 'excel')
    yil = request.args.get('yil', type=int)
    ay = request.args.get('ay', type=int)

    fonksiyonlar = {
        ('aylik_ozet', 'excel'): lambda: rapor_servisi.aylik_ozet_excel(yil, ay),
        ('aylik_ozet', 'pdf'): lambda: rapor_servisi.aylik_ozet_pdf(yil, ay),
        ('odeme_durumu', 'excel'): lambda: rapor_servisi.odeme_durumu_excel(yil, ay),
        ('odeme_durumu', 'pdf'): lambda: rapor_servisi.odeme_durumu_pdf(yil, ay),
        ('gider_detay', 'excel'): lambda: rapor_servisi.gider_detay_excel(yil, ay),
        ('gider_detay', 'pdf'): lambda: rapor_servisi.gider_detay_pdf(yil, ay),
        ('yillik_ozet', 'excel'): lambda: rapor_servisi.yillik_ozet_excel(yil),
        ('yillik_ozet', 'pdf'): lambda: rapor_servisi.yillik_ozet_pdf(yil),
    }

    fonksiyon = fonksiyonlar.get((tur, fmt))
    if not fonksiyon:
        return 'Gecersiz rapor turu veya format', 400

    output = fonksiyon()
    ay_adi = AY_ISIMLERI.get(ay, '')

    if fmt == 'excel':
        dosya_adi = f'{tur}_{ay_adi}_{yil}.xlsx' if ay else f'{tur}_{yil}.xlsx'
        return send_file(output,
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True, download_name=dosya_adi)
    else:
        dosya_adi = f'{tur}_{ay_adi}_{yil}.pdf' if ay else f'{tur}_{yil}.pdf'
        return send_file(output, mimetype='application/pdf',
                         as_attachment=True, download_name=dosya_adi)
