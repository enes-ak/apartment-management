from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from database import db
from models import Apartment, ExtraCollection, ExtraPayment, Log
from services.cash_service import calculate_cash
from services.report_service import extra_collection_report_pdf

bp = Blueprint('extra_collections', __name__, url_prefix='/ekstra-tahsilat')

AY_ISIMLERI = {
    1: 'Ocak', 2: 'Subat', 3: 'Mart', 4: 'Nisan', 5: 'Mayis', 6: 'Haziran',
    7: 'Temmuz', 8: 'Agustos', 9: 'Eylul', 10: 'Ekim', 11: 'Kasim', 12: 'Aralik'
}


@bp.route('/')
def index():
    now = datetime.now()
    collections = ExtraCollection.query.order_by(ExtraCollection.created_at.desc()).all()

    collection_stats = []
    for c in collections:
        paid = sum(1 for p in c.payments if p.is_paid)
        total = len(c.payments)
        collected = paid * c.per_unit_amount
        collection_stats.append({
            'collection': c,
            'paid_count': paid,
            'total_count': total,
            'collected': collected,
        })

    return render_template('extra_collections.html',
                           collections=collection_stats,
                           MONTH_NAMES=AY_ISIMLERI,
                           year=now.year, month=now.month)


@bp.route('/ekle', methods=['POST'])
def create():
    description = request.form.get('aciklama', '').strip()
    total_amount = request.form.get('tutar', type=float)
    year = request.form.get('yil', type=int)
    month = request.form.get('ay', type=int)

    if not description or not total_amount or total_amount <= 0:
        flash('Aciklama ve gecerli bir tutar giriniz.', 'danger')
        return redirect(url_for('extra_collections.index'))

    apartments = Apartment.query.all()
    if not apartments:
        flash('Sistemde daire bulunamadi.', 'danger')
        return redirect(url_for('extra_collections.index'))

    per_unit = round(total_amount / len(apartments), 2)

    collection = ExtraCollection(
        description=description,
        total_amount=total_amount,
        per_unit_amount=per_unit,
        created_at=datetime.now(),
        year=year,
        month=month,
    )
    db.session.add(collection)
    db.session.flush()

    for apt in apartments:
        ep = ExtraPayment(collection_id=collection.id, apartment_id=apt.id)
        db.session.add(ep)

    db.session.commit()
    Log.record(f'Ekstra tahsilat olusturuldu: {description} - {total_amount:.2f} TL (Daire basi {per_unit:.2f} TL)')
    flash(f'Ekstra tahsilat olusturuldu: {description}', 'success')
    return redirect(url_for('extra_collections.detail', collection_id=collection.id))


@bp.route('/<int:collection_id>')
def detail(collection_id):
    collection = ExtraCollection.query.get_or_404(collection_id)
    payments = ExtraPayment.query.filter_by(collection_id=collection_id)\
        .join(Apartment).order_by(Apartment.unit_no).all()

    paid_count = sum(1 for p in payments if p.is_paid)
    collected = paid_count * collection.per_unit_amount

    return render_template('extra_collection_detail.html',
                           collection=collection,
                           payments=payments,
                           paid_count=paid_count,
                           total_count=len(payments),
                           collected=collected,
                           AY_ISIMLERI=AY_ISIMLERI)


@bp.route('/toggle/<int:payment_id>', methods=['POST'])
def toggle(payment_id):
    ep = ExtraPayment.query.get_or_404(payment_id)
    collection = ep.collection

    ep.is_paid = not ep.is_paid
    ep.payment_date = datetime.now() if ep.is_paid else None
    db.session.commit()

    status = 'odendi' if ep.is_paid else 'geri alindi'
    Log.record(f'Ekstra tahsilat - Daire {ep.apartment.unit_no}: {collection.description} {status}')

    calculate_cash(collection.year, collection.month)

    payments = ExtraPayment.query.filter_by(collection_id=collection.id)\
        .join(Apartment).order_by(Apartment.unit_no).all()
    paid_count = sum(1 for p in payments if p.is_paid)
    collected = paid_count * collection.per_unit_amount

    return render_template('partials/extra_payment_row.html',
                           ep=ep, collection=collection)


@bp.route('/rapor/<int:collection_id>')
def report_pdf(collection_id):
    collection = ExtraCollection.query.get_or_404(collection_id)
    output = extra_collection_report_pdf(collection)
    filename = f'ekstra_tahsilat_{collection.id}.pdf'
    return send_file(output, mimetype='application/pdf',
                     as_attachment=True, download_name=filename)


@bp.route('/sil/<int:collection_id>', methods=['POST'])
def delete(collection_id):
    collection = ExtraCollection.query.get_or_404(collection_id)
    year, month = collection.year, collection.month
    description = collection.description

    db.session.delete(collection)
    db.session.commit()

    calculate_cash(year, month)
    Log.record(f'Ekstra tahsilat silindi: {description}')
    flash('Ekstra tahsilat silindi.', 'success')
    return redirect(url_for('extra_collections.index'))
