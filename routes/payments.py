from datetime import datetime
from flask import Blueprint, render_template, request, send_file
from database import db
from models import Apartment, Payment, DuesConfig, Log
from services.cash_service import calculate_cash
from services.report_service import apartment_report_pdf

bp = Blueprint('payments', __name__, url_prefix='/odemeler')

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan',
    5: 'Mayis', 6: 'Haziran', 7: 'Temmuz', 8: 'Agustos',
    9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}

@bp.route('/')
def index():
    now = datetime.now()
    year = request.args.get('yil', now.year, type=int)
    month = request.args.get('ay', now.month, type=int)
    apartments = Apartment.query.order_by(Apartment.unit_no).all()
    dues = DuesConfig.current_amount()
    payment_statuses = {}
    for apartment in apartments:
        payment = Payment.query.filter_by(apartment_id=apartment.id, year=year, month=month).first()
        payment_statuses[apartment.id] = payment
    total_apartments = len(apartments)
    paid = sum(1 for p in payment_statuses.values() if p and p.is_paid)
    unpaid = total_apartments - paid
    return render_template('odemeler.html', apartments=apartments, payment_statuses=payment_statuses,
                           year=year, month=month, dues=dues, MONTH_NAMES=AY_ISIMLERI,
                           total_apartments=total_apartments, paid_count=paid, unpaid_count=unpaid)

@bp.route('/toggle/<int:daire_id>/<int:yil>/<int:ay>', methods=['POST'])
def toggle(daire_id, yil, ay):
    payment = Payment.query.filter_by(apartment_id=daire_id, year=yil, month=ay).first()
    if payment is None:
        payment = Payment(apartment_id=daire_id, year=yil, month=ay, is_paid=True, payment_date=datetime.now())
        db.session.add(payment)
    else:
        payment.is_paid = not payment.is_paid
        payment.payment_date = datetime.now() if payment.is_paid else None
    db.session.commit()
    calculate_cash(yil, ay)
    apartment = Apartment.query.get(daire_id)
    status = 'odendi' if payment.is_paid else 'geri alindi'
    Log.record(f'Daire {apartment.unit_no} - {AY_ISIMLERI[ay]} {yil} aidat {status}')
    return render_template('parcalar/odeme_satir.html', apartment=apartment, payment=payment, year=yil, month=ay, MONTH_NAMES=AY_ISIMLERI)

@bp.route('/toplu/<int:daire_id>/<int:yil>', methods=['POST'])
def bulk_pay(daire_id, yil):
    from flask import redirect, url_for, flash
    selected_months = request.form.getlist('aylar', type=int)
    if not selected_months:
        flash('Hicbir ay secilmedi.', 'warning')
        return redirect(url_for('payments.index', yil=yil, ay=request.args.get('ay', datetime.now().month, type=int)))

    for month in selected_months:
        payment = Payment.query.filter_by(apartment_id=daire_id, year=yil, month=month).first()
        if payment is None:
            payment = Payment(apartment_id=daire_id, year=yil, month=month, is_paid=True, payment_date=datetime.now())
            db.session.add(payment)
        elif not payment.is_paid:
            payment.is_paid = True
            payment.payment_date = datetime.now()
    db.session.commit()
    for month in set(selected_months):
        calculate_cash(yil, month)
    apartment = Apartment.query.get(daire_id)
    Log.record(f'Daire {apartment.unit_no} - {len(selected_months)} ay toplu odeme kaydedildi ({yil})')
    flash(f'Daire {apartment.unit_no} - {len(selected_months)} ay odeme kaydedildi.', 'success')
    return redirect(url_for('payments.index', yil=yil, ay=request.args.get('ay', datetime.now().month, type=int)))


@bp.route('/daire/<int:daire_id>')
def apartment_detail(daire_id):
    apartment = Apartment.query.get_or_404(daire_id)
    dues = DuesConfig.current_amount()
    now = datetime.now()
    year = request.args.get('yil', now.year, type=int)

    # Build all months for the year (up to current month if current year)
    last_month = now.month if year == now.year else 12
    monthly_status = []
    paid_count = 0
    overdue_count = 0

    for month in range(1, 13):
        payment = Payment.query.filter_by(apartment_id=daire_id, year=year, month=month).first()
        is_paid = payment.is_paid if payment else False
        is_overdue = (not is_paid) and (month <= last_month)

        monthly_status.append({
            'month': month,
            'month_name': AY_ISIMLERI[month],
            'is_paid': is_paid,
            'payment_date': payment.payment_date if payment and payment.is_paid else None,
            'is_overdue': is_overdue,
        })

        if is_paid:
            paid_count += 1
        if is_overdue:
            overdue_count += 1

    unpaid_count = 12 - paid_count
    yearly_total = 12 * dues
    paid_amount = paid_count * dues
    remaining_amount = unpaid_count * dues
    overdue_amount = overdue_count * dues

    return render_template('daire_detay.html', apartment=apartment, monthly_status=monthly_status,
                           dues=dues, year=year, last_month=last_month,
                           paid_count=paid_count, unpaid_count=unpaid_count,
                           overdue_count=overdue_count,
                           annual_total=yearly_total, paid_amount=paid_amount,
                           remaining_amount=remaining_amount, overdue_amount=overdue_amount,
                           MONTH_NAMES=AY_ISIMLERI)


@bp.route('/daire-rapor/<int:daire_id>/<int:yil>')
def apartment_report(daire_id, yil):
    apartment = Apartment.query.get_or_404(daire_id)
    output = apartment_report_pdf(daire_id, yil)
    filename = f'daire_{apartment.unit_no}_{yil}_odeme_raporu.pdf'
    return send_file(output, mimetype='application/pdf', as_attachment=True, download_name=filename)
