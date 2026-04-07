import io
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

# Turkce karakter destegi icin DejaVu Sans fontu
pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
PDF_FONT = 'DejaVuSans'
PDF_FONT_BOLD = 'DejaVuSans-Bold'

from models import Apartment, Payment, Expense, ExpenseCategory, CashRegister, Setting, DuesConfig

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan', 5: 'Mayis', 6: 'Haziran',
    7: 'Temmuz', 8: 'Agustos', 9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}

# ── Excel Styles ──────────────────────────────────────────────
HEADER_FONT = Font(bold=True, size=14, color='FFFFFF')
SUBHEADER_FONT = Font(bold=True, size=11, color='FFFFFF')
HEADER_FILL = PatternFill(start_color='1a1d21', end_color='1a1d21', fill_type='solid')
GREEN_FILL = PatternFill(start_color='d4edda', end_color='d4edda', fill_type='solid')
RED_FILL = PatternFill(start_color='f8d7da', end_color='f8d7da', fill_type='solid')
THIN_BORDER = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin')
)


# ── Excel Helpers ─────────────────────────────────────────────
def _excel_header(ws, building_name, report_name, date_str):
    ws.append([building_name])
    ws.append([report_name])
    ws.append([f'Olusturma Tarihi: {date_str}'])
    for row in ws.iter_rows(min_row=1, max_row=3, max_col=1):
        for cell in row:
            cell.font = HEADER_FONT if cell.row == 1 else SUBHEADER_FONT
            cell.fill = HEADER_FILL
            cell.alignment = Alignment(horizontal='left')


def _excel_table_header(ws, headers, row_num):
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=row_num, column=col_idx, value=header)
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal='center')
        cell.border = THIN_BORDER


def _excel_row(ws, values, row_num, fill=None):
    for col_idx, value in enumerate(values, 1):
        cell = ws.cell(row=row_num, column=col_idx, value=value)
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal='center')
        if fill:
            cell.fill = fill


def _save_excel(wb):
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


# ── PDF Helpers ───────────────────────────────────────────────
def _pdf_header_block(building_name, report_name, date_str):
    title_style = ParagraphStyle('TRTitle', fontName=PDF_FONT_BOLD, fontSize=16, spaceAfter=4)
    heading_style = ParagraphStyle('TRHeading', fontName=PDF_FONT_BOLD, fontSize=12, spaceAfter=4)
    normal_style = ParagraphStyle('TRNormal', fontName=PDF_FONT, fontSize=9, textColor=colors.grey)
    elements = []
    elements.append(Paragraph(building_name, title_style))
    elements.append(Paragraph(report_name, heading_style))
    elements.append(Paragraph(f'Olusturma Tarihi: {date_str}', normal_style))
    elements.append(Spacer(1, 10 * mm))
    return elements


def _pdf_table(headers, data_rows, col_widths=None):
    data = [headers] + data_rows
    t = Table(data, colWidths=col_widths)
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1d21')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), PDF_FONT_BOLD),
        ('FONTNAME', (0, 1), (-1, -1), PDF_FONT),
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


def _save_pdf(elements):
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4,
                            leftMargin=15 * mm, rightMargin=15 * mm,
                            topMargin=15 * mm, bottomMargin=15 * mm)
    doc.build(elements)
    output.seek(0)
    return output


def _building_name():
    return Setting.getir('apartman_adi', 'Apartman')


def _date_str():
    return datetime.now().strftime('%d.%m.%Y')


def _calculate_month(year, month):
    """Calculate income/expense/breakdown for a month (independent of cash register)."""
    dues = DuesConfig.current_amount()
    paid_count = Payment.query.filter_by(year=year, month=month, is_paid=True).count()
    total_apartments = Apartment.query.count()
    income = paid_count * dues

    expenses = Expense.query.filter_by(year=year, month=month).all()
    total_expense = sum(e.amount for e in expenses)

    category_totals = {}
    for e in expenses:
        name = e.kalem.kalem_adi
        category_totals[name] = category_totals.get(name, 0) + e.amount

    return {
        'dues': dues,
        'paid_count': paid_count,
        'total_apartments': total_apartments,
        'income': income,
        'expense': total_expense,
        'category_totals': category_totals,
    }


# ══════════════════════════════════════════════════════════════
# 1) Monthly Summary
# ══════════════════════════════════════════════════════════════
def monthly_summary_excel(year, month):
    building_name = _building_name()
    month_name = AY_ISIMLERI.get(month, '')
    date_str = _date_str()
    h = _calculate_month(year, month)

    wb = Workbook()
    ws = wb.active
    ws.title = 'Aylik Ozet'

    _excel_header(ws, building_name, f'{month_name} {year} - Aylik Ozet Raporu', date_str)

    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 20

    row_num = 5
    info_items = [
        ('Aidat Tutari', f'{h["dues"]:.2f} TL'),
        ('Odeme Yapan', f'{h["paid_count"]} / {h["total_apartments"]}'),
        ('Toplam Gelir', f'{h["income"]:.2f} TL'),
        ('Toplam Gider', f'{h["expense"]:.2f} TL'),
        ('Net', f'{h["income"] - h["expense"]:.2f} TL'),
    ]
    for label, value in info_items:
        _excel_row(ws, [label, value], row_num)
        row_num += 1

    if h['category_totals']:
        row_num += 1
        _excel_table_header(ws, ['Gider Kalemi', 'Tutar'], row_num)
        row_num += 1
        for name, amount in h['category_totals'].items():
            _excel_row(ws, [name, f'{amount:.2f} TL'], row_num)
            row_num += 1
        _excel_row(ws, ['TOPLAM', f'{h["expense"]:.2f} TL'], row_num)
        ws.cell(row=row_num, column=1).font = Font(bold=True)
        ws.cell(row=row_num, column=2).font = Font(bold=True)

    return _save_excel(wb)


def monthly_summary_pdf(year, month):
    building_name = _building_name()
    month_name = AY_ISIMLERI.get(month, '')
    date_str = _date_str()
    h = _calculate_month(year, month)

    elements = _pdf_header_block(building_name, f'{month_name} {year} - Aylik Ozet Raporu', date_str)

    summary_data = [
        ['Aidat Tutari', f'{h["dues"]:.2f} TL'],
        ['Odeme Yapan', f'{h["paid_count"]} / {h["total_apartments"]}'],
        ['Toplam Gelir', f'{h["income"]:.2f} TL'],
        ['Toplam Gider', f'{h["expense"]:.2f} TL'],
        ['Net', f'{h["income"] - h["expense"]:.2f} TL'],
    ]
    elements.append(_pdf_table(['Bilgi', 'Deger'], summary_data, col_widths=[60 * mm, 60 * mm]))
    elements.append(Spacer(1, 10 * mm))

    if h['category_totals']:
        expense_rows = [[name, f'{amount:.2f} TL'] for name, amount in h['category_totals'].items()]
        expense_rows.append(['TOPLAM', f'{h["expense"]:.2f} TL'])
        elements.append(_pdf_table(['Gider Kalemi', 'Tutar'], expense_rows, col_widths=[60 * mm, 60 * mm]))

    return _save_pdf(elements)


# ══════════════════════════════════════════════════════════════
# 2) Payment Status
# ══════════════════════════════════════════════════════════════
def payment_status_excel(year, month):
    building_name = _building_name()
    month_name = AY_ISIMLERI.get(month, '')
    date_str = _date_str()

    wb = Workbook()
    ws = wb.active
    ws.title = 'Odeme Durumu'

    _excel_header(ws, building_name, f'{month_name} {year} - Odeme Durumu Raporu', date_str)

    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 15

    row_num = 5
    _excel_table_header(ws, ['Daire No', 'Sakin Adi', 'Durum'], row_num)
    row_num += 1

    apartments = Apartment.query.order_by(Apartment.daire_no).all()
    paid_count = 0
    for apt in apartments:
        payment = Payment.query.filter_by(daire_id=apt.id, year=year, month=month).first()
        is_paid = payment.is_paid if payment else False
        status = 'Odendi' if is_paid else 'Odenmedi'
        fill = GREEN_FILL if is_paid else RED_FILL
        _excel_row(ws, [apt.daire_no, apt.sakin_adi, status], row_num, fill=fill)
        if is_paid:
            paid_count += 1
        row_num += 1

    row_num += 1
    ws.cell(row=row_num, column=1, value='Toplam Odenen:').font = Font(bold=True)
    ws.cell(row=row_num, column=2, value=f'{paid_count} / {len(apartments)}')

    return _save_excel(wb)


def payment_status_pdf(year, month):
    building_name = _building_name()
    month_name = AY_ISIMLERI.get(month, '')
    date_str = _date_str()

    elements = _pdf_header_block(building_name, f'{month_name} {year} - Odeme Durumu Raporu', date_str)

    apartments = Apartment.query.order_by(Apartment.daire_no).all()
    rows = []
    paid_count = 0
    for apt in apartments:
        payment = Payment.query.filter_by(daire_id=apt.id, year=year, month=month).first()
        is_paid = payment.is_paid if payment else False
        status = 'Odendi' if is_paid else 'Odenmedi'
        rows.append([str(apt.daire_no), status])
        if is_paid:
            paid_count += 1

    headers = ['Daire No', 'Durum']
    data = [headers] + rows
    col_widths = [40 * mm, 50 * mm]
    t = Table(data, colWidths=col_widths)
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1d21')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), PDF_FONT_BOLD),
        ('FONTNAME', (0, 1), (-1, -1), PDF_FONT),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]
    for i in range(1, len(data)):
        row_data = rows[i - 1]
        if row_data[1] == 'Odendi':
            style_cmds.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#d4edda')))
        else:
            style_cmds.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8d7da')))
    t.setStyle(TableStyle(style_cmds))
    elements.append(t)

    elements.append(Spacer(1, 5 * mm))
    summary_style = ParagraphStyle('TROzet', fontName=PDF_FONT_BOLD, fontSize=10)
    elements.append(Paragraph(f'Toplam Odenen: {paid_count} / {len(apartments)}', summary_style))

    return _save_pdf(elements)


# ══════════════════════════════════════════════════════════════
# 3) Expense Detail
# ══════════════════════════════════════════════════════════════
def expense_detail_excel(year, month):
    building_name = _building_name()
    month_name = AY_ISIMLERI.get(month, '')
    date_str = _date_str()
    h = _calculate_month(year, month)

    wb = Workbook()
    ws = wb.active
    ws.title = 'Gider Detay'

    _excel_header(ws, building_name, f'{month_name} {year} - Gider Detay Raporu', date_str)

    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 18
    ws.column_dimensions['C'].width = 12

    row_num = 5
    _excel_table_header(ws, ['Gider Kalemi', 'Tutar', 'Oran (%)'], row_num)
    row_num += 1
    for name, amount in h['category_totals'].items():
        ratio = (amount / h['expense'] * 100) if h['expense'] > 0 else 0
        _excel_row(ws, [name, f'{amount:.2f} TL', f'{ratio:.1f}%'], row_num)
        row_num += 1
    _excel_row(ws, ['TOPLAM', f'{h["expense"]:.2f} TL', '100%'], row_num)
    for col in range(1, 4):
        ws.cell(row=row_num, column=col).font = Font(bold=True)

    return _save_excel(wb)


def expense_detail_pdf(year, month):
    building_name = _building_name()
    month_name = AY_ISIMLERI.get(month, '')
    date_str = _date_str()
    h = _calculate_month(year, month)

    elements = _pdf_header_block(building_name, f'{month_name} {year} - Gider Detay Raporu', date_str)

    rows = []
    for name, amount in h['category_totals'].items():
        ratio = (amount / h['expense'] * 100) if h['expense'] > 0 else 0
        rows.append([name, f'{amount:.2f} TL', f'{ratio:.1f}%'])
    rows.append(['TOPLAM', f'{h["expense"]:.2f} TL', '100%'])

    elements.append(_pdf_table(['Gider Kalemi', 'Tutar', 'Oran (%)'], rows,
                               col_widths=[50 * mm, 40 * mm, 30 * mm]))

    return _save_pdf(elements)


# ══════════════════════════════════════════════════════════════
# 4) Annual Summary
# ══════════════════════════════════════════════════════════════
def annual_summary_excel(year):
    building_name = _building_name()
    date_str = _date_str()

    wb = Workbook()
    ws = wb.active
    ws.title = 'Yillik Ozet'

    _excel_header(ws, building_name, f'{year} - Yillik Ozet Raporu', date_str)

    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 18
    ws.column_dimensions['C'].width = 18
    ws.column_dimensions['D'].width = 18

    row_num = 5
    _excel_table_header(ws, ['Ay', 'Gelir', 'Gider', 'Net'], row_num)
    row_num += 1

    total_income = 0
    total_expense = 0
    for month_num in range(1, 13):
        h = _calculate_month(year, month_num)
        total_income += h['income']
        total_expense += h['expense']
        net = h['income'] - h['expense']
        month_name = AY_ISIMLERI[month_num]
        _excel_row(ws, [month_name, f'{h["income"]:.2f} TL', f'{h["expense"]:.2f} TL',
                          f'{net:.2f} TL'], row_num)
        row_num += 1
    net_total = total_income - total_expense
    _excel_row(ws, ['TOPLAM', f'{total_income:.2f} TL', f'{total_expense:.2f} TL',
                      f'{net_total:.2f} TL'], row_num)
    for col in range(1, 5):
        ws.cell(row=row_num, column=col).font = Font(bold=True)

    return _save_excel(wb)


def annual_summary_pdf(year):
    building_name = _building_name()
    date_str = _date_str()

    elements = _pdf_header_block(building_name, f'{year} - Yillik Ozet Raporu', date_str)

    rows = []
    total_income = 0
    total_expense = 0
    for month_num in range(1, 13):
        h = _calculate_month(year, month_num)
        total_income += h['income']
        total_expense += h['expense']
        net = h['income'] - h['expense']
        month_name = AY_ISIMLERI[month_num]
        rows.append([month_name, f'{h["income"]:.2f} TL', f'{h["expense"]:.2f} TL',
                     f'{net:.2f} TL'])
    net_total = total_income - total_expense
    rows.append(['TOPLAM', f'{total_income:.2f} TL', f'{total_expense:.2f} TL',
                 f'{net_total:.2f} TL'])

    elements.append(_pdf_table(['Ay', 'Gelir', 'Gider', 'Net'], rows,
                               col_widths=[35 * mm, 40 * mm, 40 * mm, 40 * mm]))

    return _save_pdf(elements)


# ══════════════════════════════════════════════════════════════
# 5) Apartment Payment Report
# ══════════════════════════════════════════════════════════════
def apartment_report_pdf(apartment_id, year):
    building_name = _building_name()
    date_str = _date_str()
    apartment = Apartment.query.get(apartment_id)
    dues = DuesConfig.current_amount()

    floor_str = 'Giris Kat' if apartment.kat == 0 else f'{apartment.kat}. Kat'
    subtitle = f'Daire {apartment.daire_no} - {year} Yili Aidat Odeme Raporu'

    elements = _pdf_header_block(building_name, subtitle, date_str)

    info_style = ParagraphStyle('TRBilgi', fontName=PDF_FONT, fontSize=9, spaceAfter=2)
    elements.append(Paragraph(f'Daire No: {apartment.daire_no}', info_style))
    elements.append(Paragraph(f'Kat: {floor_str}', info_style))
    elements.append(Paragraph(f'Aylik Aidat: {dues:.2f} TL', info_style))
    elements.append(Spacer(1, 8 * mm))

    rows = []
    paid_count = 0
    now = datetime.now()
    last_month = now.month if year == now.year else 12

    for month in range(1, 13):
        payment = Payment.query.filter_by(daire_id=apartment_id, year=year, month=month).first()
        is_paid = payment.is_paid if payment else False
        month_name = AY_ISIMLERI[month]

        if is_paid:
            status = 'Odendi'
            payment_date = payment.odeme_tarihi.strftime('%d.%m.%Y') if payment.odeme_tarihi else '-'
            paid_count += 1
        elif month <= last_month:
            status = 'Gecikmis'
            payment_date = '-'
        else:
            status = 'Bekleniyor'
            payment_date = '-'

        rows.append([month_name, f'{dues:.2f} TL', status, payment_date])

    headers = ['Ay', 'Aidat', 'Durum', 'Odeme Tarihi']
    data = [headers] + rows
    col_widths = [30 * mm, 35 * mm, 35 * mm, 40 * mm]
    t = Table(data, colWidths=col_widths)

    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1d21')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), PDF_FONT_BOLD),
        ('FONTNAME', (0, 1), (-1, -1), PDF_FONT),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]

    for i, row in enumerate(rows):
        row_idx = i + 1
        if row[2] == 'Odendi':
            style_cmds.append(('BACKGROUND', (2, row_idx), (2, row_idx), colors.HexColor('#d4edda')))
        elif row[2] == 'Gecikmis':
            style_cmds.append(('BACKGROUND', (2, row_idx), (2, row_idx), colors.HexColor('#f8d7da')))
        else:
            style_cmds.append(('BACKGROUND', (2, row_idx), (2, row_idx), colors.HexColor('#e2e3e5')))

    t.setStyle(TableStyle(style_cmds))
    elements.append(t)

    elements.append(Spacer(1, 8 * mm))
    unpaid = 12 - paid_count
    summary_style = ParagraphStyle('TROzetDaire', fontName=PDF_FONT_BOLD, fontSize=10, spaceAfter=3)
    normal_style = ParagraphStyle('TRNormalDaire', fontName=PDF_FONT, fontSize=9, spaceAfter=2)

    elements.append(Paragraph('Ozet', summary_style))
    elements.append(Paragraph(f'Yillik Toplam: {12 * dues:.2f} TL', normal_style))
    elements.append(Paragraph(f'Odenen: {paid_count} ay - {paid_count * dues:.2f} TL', normal_style))
    elements.append(Paragraph(f'Kalan: {unpaid} ay - {unpaid * dues:.2f} TL', normal_style))

    overdue = sum(1 for r in rows if r[2] == 'Gecikmis')
    if overdue > 0:
        overdue_style = ParagraphStyle('TRGecikmeDaire', fontName=PDF_FONT_BOLD, fontSize=9, textColor=colors.HexColor('#dc3545'))
        elements.append(Paragraph(f'Gecikmis: {overdue} ay - {overdue * dues:.2f} TL', overdue_style))

    return _save_pdf(elements)
