from datetime import datetime
from flask import Blueprint, render_template, request, send_file
from services import report_service

bp = Blueprint('reports', __name__, url_prefix='/raporlar')

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan', 5: 'Mayis', 6: 'Haziran',
    7: 'Temmuz', 8: 'Agustos', 9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}
REPORT_TYPES = {
    'aylik_ozet': 'Aylik Ozet Raporu',
    'odeme_durumu': 'Odeme Durumu Raporu',
    'gider_detay': 'Gider Detay Raporu',
    'yillik_ozet': 'Yillik Ozet Raporu',
}


@bp.route('/')
def index():
    now = datetime.now()
    return render_template('raporlar.html', year=now.year, month=now.month,
                           MONTH_NAMES=AY_ISIMLERI, REPORT_TYPES=REPORT_TYPES)


@bp.route('/olustur')
def generate():
    report_type = request.args.get('tur')
    fmt = request.args.get('format', 'excel')
    year = request.args.get('yil', type=int)
    month = request.args.get('ay', type=int)

    functions = {
        ('aylik_ozet', 'excel'): lambda: report_service.monthly_summary_excel(year, month),
        ('aylik_ozet', 'pdf'): lambda: report_service.monthly_summary_pdf(year, month),
        ('odeme_durumu', 'excel'): lambda: report_service.payment_status_excel(year, month),
        ('odeme_durumu', 'pdf'): lambda: report_service.payment_status_pdf(year, month),
        ('gider_detay', 'excel'): lambda: report_service.expense_detail_excel(year, month),
        ('gider_detay', 'pdf'): lambda: report_service.expense_detail_pdf(year, month),
        ('yillik_ozet', 'excel'): lambda: report_service.annual_summary_excel(year),
        ('yillik_ozet', 'pdf'): lambda: report_service.annual_summary_pdf(year),
    }

    func = functions.get((report_type, fmt))
    if not func:
        return 'Gecersiz rapor turu veya format', 400

    output = func()
    month_name = AY_ISIMLERI.get(month, '')

    if fmt == 'excel':
        filename = f'{report_type}_{month_name}_{year}.xlsx' if month else f'{report_type}_{year}.xlsx'
        return send_file(output,
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True, download_name=filename)
    else:
        filename = f'{report_type}_{month_name}_{year}.pdf' if month else f'{report_type}_{year}.pdf'
        return send_file(output, mimetype='application/pdf',
                         as_attachment=True, download_name=filename)
