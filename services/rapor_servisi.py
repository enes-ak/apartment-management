import io
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from models import Daire, Odeme, Gider, GiderKalemi, Kasa, Ayar, AidatAyari

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan', 5: 'Mayis', 6: 'Haziran',
    7: 'Temmuz', 8: 'Agustos', 9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}

# ── Excel Styles ──────────────────────────────────────────────
BASLIK_FONT = Font(bold=True, size=14, color='FFFFFF')
ALT_BASLIK_FONT = Font(bold=True, size=11, color='FFFFFF')
BASLIK_FILL = PatternFill(start_color='1a1d21', end_color='1a1d21', fill_type='solid')
YESIL_FILL = PatternFill(start_color='d4edda', end_color='d4edda', fill_type='solid')
KIRMIZI_FILL = PatternFill(start_color='f8d7da', end_color='f8d7da', fill_type='solid')
INCE_BORDER = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin')
)


# ── Excel Helpers ─────────────────────────────────────────────
def _excel_baslik(ws, apartman_adi, rapor_adi, tarih_str):
    ws.append([apartman_adi])
    ws.append([rapor_adi])
    ws.append([f'Olusturma Tarihi: {tarih_str}'])
    for row in ws.iter_rows(min_row=1, max_row=3, max_col=1):
        for cell in row:
            cell.font = BASLIK_FONT if cell.row == 1 else ALT_BASLIK_FONT
            cell.fill = BASLIK_FILL
            cell.alignment = Alignment(horizontal='left')


def _excel_tablo_basligi(ws, basliklar, satir_no):
    for col_idx, baslik in enumerate(basliklar, 1):
        cell = ws.cell(row=satir_no, column=col_idx, value=baslik)
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = BASLIK_FILL
        cell.alignment = Alignment(horizontal='center')
        cell.border = INCE_BORDER


def _excel_satir(ws, degerler, satir_no, fill=None):
    for col_idx, deger in enumerate(degerler, 1):
        cell = ws.cell(row=satir_no, column=col_idx, value=deger)
        cell.border = INCE_BORDER
        cell.alignment = Alignment(horizontal='center')
        if fill:
            cell.fill = fill


def _kaydet_excel(wb):
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


# ── PDF Helpers ───────────────────────────────────────────────
def _pdf_baslik_tablosu(apartman_adi, rapor_adi, tarih_str):
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph(apartman_adi, styles['Title']))
    elements.append(Paragraph(rapor_adi, styles['Heading2']))
    elements.append(Paragraph(f'Olusturma Tarihi: {tarih_str}', styles['Normal']))
    elements.append(Spacer(1, 10 * mm))
    return elements


def _pdf_tablo(basliklar, veriler, col_widths=None):
    data = [basliklar] + veriler
    t = Table(data, colWidths=col_widths)
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1d21')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]
    # Alternating row colors
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f0f0f0')))
    t.setStyle(TableStyle(style_cmds))
    return t


def _kaydet_pdf(elements):
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4,
                            leftMargin=15 * mm, rightMargin=15 * mm,
                            topMargin=15 * mm, bottomMargin=15 * mm)
    doc.build(elements)
    output.seek(0)
    return output


def _apartman_adi():
    return Ayar.getir('apartman_adi', 'Apartman')


def _tarih_str():
    return datetime.now().strftime('%d.%m.%Y')


# ══════════════════════════════════════════════════════════════
# 1) Aylik Ozet
# ══════════════════════════════════════════════════════════════
def aylik_ozet_excel(yil, ay):
    apartman = _apartman_adi()
    ay_adi = AY_ISIMLERI.get(ay, '')
    tarih = _tarih_str()

    aidat = AidatAyari.guncel_miktar()
    odenen = Odeme.query.filter_by(yil=yil, ay=ay, odendi=True).count()
    toplam_daire = Daire.query.count()
    kasa = Kasa.query.filter_by(yil=yil, ay=ay).first()

    toplam_gelir = kasa.toplam_gelir if kasa else 0
    toplam_gider = kasa.toplam_gider if kasa else 0
    devir = kasa.devir if kasa else 0
    bakiye = kasa.bakiye if kasa else 0

    wb = Workbook()
    ws = wb.active
    ws.title = 'Aylik Ozet'

    _excel_baslik(ws, apartman, f'{ay_adi} {yil} - Aylik Ozet Raporu', tarih)

    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 20

    satir = 5
    bilgiler = [
        ('Aidat Tutari', f'{aidat:.2f} TL'),
        ('Odeme Yapan', f'{odenen} / {toplam_daire}'),
        ('Toplam Gelir', f'{toplam_gelir:.2f} TL'),
        ('Toplam Gider', f'{toplam_gider:.2f} TL'),
        ('Onceki Ay Devir', f'{devir:.2f} TL'),
        ('Bakiye', f'{bakiye:.2f} TL'),
    ]
    for etiket, deger in bilgiler:
        _excel_satir(ws, [etiket, deger], satir)
        satir += 1

    # Gider detay tablosu
    satir += 1
    _excel_tablo_basligi(ws, ['Gider Kalemi', 'Tutar'], satir)
    satir += 1
    giderler = Gider.query.filter_by(yil=yil, ay=ay).all()
    kalem_toplam = {}
    for g in giderler:
        ad = g.kalem.kalem_adi
        kalem_toplam[ad] = kalem_toplam.get(ad, 0) + g.tutar
    for ad, tutar in kalem_toplam.items():
        _excel_satir(ws, [ad, f'{tutar:.2f} TL'], satir)
        satir += 1
    _excel_satir(ws, ['TOPLAM', f'{toplam_gider:.2f} TL'], satir)
    ws.cell(row=satir, column=1).font = Font(bold=True)
    ws.cell(row=satir, column=2).font = Font(bold=True)

    return _kaydet_excel(wb)


def aylik_ozet_pdf(yil, ay):
    apartman = _apartman_adi()
    ay_adi = AY_ISIMLERI.get(ay, '')
    tarih = _tarih_str()

    aidat = AidatAyari.guncel_miktar()
    odenen = Odeme.query.filter_by(yil=yil, ay=ay, odendi=True).count()
    toplam_daire = Daire.query.count()
    kasa = Kasa.query.filter_by(yil=yil, ay=ay).first()

    toplam_gelir = kasa.toplam_gelir if kasa else 0
    toplam_gider = kasa.toplam_gider if kasa else 0
    devir = kasa.devir if kasa else 0
    bakiye = kasa.bakiye if kasa else 0

    elements = _pdf_baslik_tablosu(apartman, f'{ay_adi} {yil} - Aylik Ozet Raporu', tarih)

    ozet_data = [
        ['Aidat Tutari', f'{aidat:.2f} TL'],
        ['Odeme Yapan', f'{odenen} / {toplam_daire}'],
        ['Toplam Gelir', f'{toplam_gelir:.2f} TL'],
        ['Toplam Gider', f'{toplam_gider:.2f} TL'],
        ['Onceki Ay Devir', f'{devir:.2f} TL'],
        ['Bakiye', f'{bakiye:.2f} TL'],
    ]
    elements.append(_pdf_tablo(['Bilgi', 'Deger'], ozet_data, col_widths=[60 * mm, 60 * mm]))
    elements.append(Spacer(1, 10 * mm))

    # Gider detay
    giderler = Gider.query.filter_by(yil=yil, ay=ay).all()
    kalem_toplam = {}
    for g in giderler:
        ad = g.kalem.kalem_adi
        kalem_toplam[ad] = kalem_toplam.get(ad, 0) + g.tutar
    gider_rows = [[ad, f'{tutar:.2f} TL'] for ad, tutar in kalem_toplam.items()]
    gider_rows.append(['TOPLAM', f'{toplam_gider:.2f} TL'])
    elements.append(_pdf_tablo(['Gider Kalemi', 'Tutar'], gider_rows, col_widths=[60 * mm, 60 * mm]))

    return _kaydet_pdf(elements)


# ══════════════════════════════════════════════════════════════
# 2) Odeme Durumu
# ══════════════════════════════════════════════════════════════
def odeme_durumu_excel(yil, ay):
    apartman = _apartman_adi()
    ay_adi = AY_ISIMLERI.get(ay, '')
    tarih = _tarih_str()

    wb = Workbook()
    ws = wb.active
    ws.title = 'Odeme Durumu'

    _excel_baslik(ws, apartman, f'{ay_adi} {yil} - Odeme Durumu Raporu', tarih)

    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 15

    satir = 5
    _excel_tablo_basligi(ws, ['Daire No', 'Sakin Adi', 'Durum'], satir)
    satir += 1

    daireler = Daire.query.order_by(Daire.daire_no).all()
    odenen_sayisi = 0
    for d in daireler:
        odeme = Odeme.query.filter_by(daire_id=d.id, yil=yil, ay=ay).first()
        odendi = odeme.odendi if odeme else False
        durum = 'Odendi' if odendi else 'Odenmedi'
        fill = YESIL_FILL if odendi else KIRMIZI_FILL
        _excel_satir(ws, [d.daire_no, d.sakin_adi, durum], satir, fill=fill)
        if odendi:
            odenen_sayisi += 1
        satir += 1

    satir += 1
    ws.cell(row=satir, column=1, value='Toplam Odenen:').font = Font(bold=True)
    ws.cell(row=satir, column=2, value=f'{odenen_sayisi} / {len(daireler)}')

    return _kaydet_excel(wb)


def odeme_durumu_pdf(yil, ay):
    apartman = _apartman_adi()
    ay_adi = AY_ISIMLERI.get(ay, '')
    tarih = _tarih_str()

    elements = _pdf_baslik_tablosu(apartman, f'{ay_adi} {yil} - Odeme Durumu Raporu', tarih)

    daireler = Daire.query.order_by(Daire.daire_no).all()
    rows = []
    odenen_sayisi = 0
    for d in daireler:
        odeme = Odeme.query.filter_by(daire_id=d.id, yil=yil, ay=ay).first()
        odendi = odeme.odendi if odeme else False
        durum = 'Odendi' if odendi else 'Odenmedi'
        rows.append([str(d.daire_no), d.sakin_adi or '', durum])
        if odendi:
            odenen_sayisi += 1

    basliklar = ['Daire No', 'Sakin Adi', 'Durum']
    data = [basliklar] + rows
    col_widths = [30 * mm, 60 * mm, 40 * mm]
    t = Table(data, colWidths=col_widths)
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1d21')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]
    for i in range(1, len(data)):
        row_data = rows[i - 1]
        if row_data[2] == 'Odendi':
            style_cmds.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#d4edda')))
        else:
            style_cmds.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8d7da')))
    t.setStyle(TableStyle(style_cmds))
    elements.append(t)

    elements.append(Spacer(1, 5 * mm))
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f'Toplam Odenen: {odenen_sayisi} / {len(daireler)}', styles['Normal']))

    return _kaydet_pdf(elements)


# ══════════════════════════════════════════════════════════════
# 3) Gider Detay
# ══════════════════════════════════════════════════════════════
def gider_detay_excel(yil, ay):
    apartman = _apartman_adi()
    ay_adi = AY_ISIMLERI.get(ay, '')
    tarih = _tarih_str()

    wb = Workbook()
    ws = wb.active
    ws.title = 'Gider Detay'

    _excel_baslik(ws, apartman, f'{ay_adi} {yil} - Gider Detay Raporu', tarih)

    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 18
    ws.column_dimensions['C'].width = 12

    giderler = Gider.query.filter_by(yil=yil, ay=ay).all()
    kalem_toplam = {}
    for g in giderler:
        ad = g.kalem.kalem_adi
        kalem_toplam[ad] = kalem_toplam.get(ad, 0) + g.tutar
    genel_toplam = sum(kalem_toplam.values())

    satir = 5
    _excel_tablo_basligi(ws, ['Gider Kalemi', 'Tutar', 'Oran (%)'], satir)
    satir += 1
    for ad, tutar in kalem_toplam.items():
        oran = (tutar / genel_toplam * 100) if genel_toplam > 0 else 0
        _excel_satir(ws, [ad, f'{tutar:.2f} TL', f'{oran:.1f}%'], satir)
        satir += 1
    _excel_satir(ws, ['TOPLAM', f'{genel_toplam:.2f} TL', '100%'], satir)
    for col in range(1, 4):
        ws.cell(row=satir, column=col).font = Font(bold=True)

    return _kaydet_excel(wb)


def gider_detay_pdf(yil, ay):
    apartman = _apartman_adi()
    ay_adi = AY_ISIMLERI.get(ay, '')
    tarih = _tarih_str()

    elements = _pdf_baslik_tablosu(apartman, f'{ay_adi} {yil} - Gider Detay Raporu', tarih)

    giderler = Gider.query.filter_by(yil=yil, ay=ay).all()
    kalem_toplam = {}
    for g in giderler:
        ad = g.kalem.kalem_adi
        kalem_toplam[ad] = kalem_toplam.get(ad, 0) + g.tutar
    genel_toplam = sum(kalem_toplam.values())

    rows = []
    for ad, tutar in kalem_toplam.items():
        oran = (tutar / genel_toplam * 100) if genel_toplam > 0 else 0
        rows.append([ad, f'{tutar:.2f} TL', f'{oran:.1f}%'])
    rows.append(['TOPLAM', f'{genel_toplam:.2f} TL', '100%'])

    elements.append(_pdf_tablo(['Gider Kalemi', 'Tutar', 'Oran (%)'], rows,
                               col_widths=[50 * mm, 40 * mm, 30 * mm]))

    return _kaydet_pdf(elements)


# ══════════════════════════════════════════════════════════════
# 4) Yillik Ozet
# ══════════════════════════════════════════════════════════════
def yillik_ozet_excel(yil):
    apartman = _apartman_adi()
    tarih = _tarih_str()

    wb = Workbook()
    ws = wb.active
    ws.title = 'Yillik Ozet'

    _excel_baslik(ws, apartman, f'{yil} - Yillik Ozet Raporu', tarih)

    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 18
    ws.column_dimensions['C'].width = 18
    ws.column_dimensions['D'].width = 18
    ws.column_dimensions['E'].width = 18

    satir = 5
    _excel_tablo_basligi(ws, ['Ay', 'Gelir', 'Gider', 'Devir', 'Bakiye'], satir)
    satir += 1

    toplam_gelir = 0
    toplam_gider = 0
    for ay_no in range(1, 13):
        kasa = Kasa.query.filter_by(yil=yil, ay=ay_no).first()
        gelir = kasa.toplam_gelir if kasa else 0
        gider = kasa.toplam_gider if kasa else 0
        devir = kasa.devir if kasa else 0
        bakiye = kasa.bakiye if kasa else 0
        toplam_gelir += gelir
        toplam_gider += gider
        ay_adi = AY_ISIMLERI[ay_no]
        _excel_satir(ws, [ay_adi, f'{gelir:.2f} TL', f'{gider:.2f} TL',
                          f'{devir:.2f} TL', f'{bakiye:.2f} TL'], satir)
        satir += 1
    _excel_satir(ws, ['TOPLAM', f'{toplam_gelir:.2f} TL', f'{toplam_gider:.2f} TL', '', ''], satir)
    for col in range(1, 6):
        ws.cell(row=satir, column=col).font = Font(bold=True)

    return _kaydet_excel(wb)


def yillik_ozet_pdf(yil):
    apartman = _apartman_adi()
    tarih = _tarih_str()

    elements = _pdf_baslik_tablosu(apartman, f'{yil} - Yillik Ozet Raporu', tarih)

    rows = []
    toplam_gelir = 0
    toplam_gider = 0
    for ay_no in range(1, 13):
        kasa = Kasa.query.filter_by(yil=yil, ay=ay_no).first()
        gelir = kasa.toplam_gelir if kasa else 0
        gider = kasa.toplam_gider if kasa else 0
        devir = kasa.devir if kasa else 0
        bakiye = kasa.bakiye if kasa else 0
        toplam_gelir += gelir
        toplam_gider += gider
        ay_adi = AY_ISIMLERI[ay_no]
        rows.append([ay_adi, f'{gelir:.2f} TL', f'{gider:.2f} TL',
                     f'{devir:.2f} TL', f'{bakiye:.2f} TL'])
    rows.append(['TOPLAM', f'{toplam_gelir:.2f} TL', f'{toplam_gider:.2f} TL', '', ''])

    elements.append(_pdf_tablo(['Ay', 'Gelir', 'Gider', 'Devir', 'Bakiye'], rows,
                               col_widths=[30 * mm, 35 * mm, 35 * mm, 35 * mm, 35 * mm]))

    return _kaydet_pdf(elements)
