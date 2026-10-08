from flask import redirect, render_template, flash, Blueprint, url_for, request
from flask_login import login_required
from app import db
from app.models import Lease, Property, Tenant
from app.validation import FormValidator
from datetime import date
from decimal import Decimal

leases_bp=Blueprint('leases', __name__, url_prefix='/leases')

@leases_bp.route('/')
@login_required
def list_leases():
    leases=Lease.query.order_by(Lease.start_date).all()
    return render_template('leases/list.html', leases=leases)

LEASE_STATUSES={'active', 'expired', 'terminated'}
MAX_MONEY=Decimal('99999999.99')


def lease_form_options(lease=None):
    tenants=Tenant.query.order_by(Tenant.first_name, Tenant.last_name).all()
    properties=available_properties_query(lease).order_by(Property.address).all()
    return tenants, properties


def available_properties_query(lease=None):
    if lease is None:
        return Property.query.filter(Property.is_occupied==False)
    return Property.query.filter((Property.is_occupied==False) | (Property.id==lease.property_id))


def validate_lease_form(form, lease=None):
    v=FormValidator(form)
    data={
        'property': v.record('property_id', 'Property', Property, query=available_properties_query(lease)),
        'start_date': v.date('start_date', 'Start date', required=True, min_value=date(1900, 1, 1)),
        'end_date': v.date('end_date', 'End date', required=True, min_value=date(1900, 1, 1)),
        'monthly_rent': v.decimal('monthly_rent', 'Monthly rent', required=True, min_value=Decimal('0.01'), max_value=MAX_MONEY),
        'rent_due_date': v.integer('rent_due_date', 'Rent due date', required=True, min_value=1, max_value=31),
        'refundable_deposit': v.decimal('refundable_deposit', 'Refundable deposit', min_value=0, max_value=MAX_MONEY),
        'nonrefundable_deposit': v.decimal('nonrefundable_deposit', 'Non-refundable deposit', min_value=0, max_value=MAX_MONEY),
        'cars': v.integer('cars', 'Cars', min_value=0, max_value=20),
        'pets': v.integer('pets', 'Pets', min_value=0, max_value=20),
    }
    if lease is not None:
        data['status']=v.choice('status', 'Status', LEASE_STATUSES, required=True)

    if data['start_date'] and data['end_date'] and data['end_date']<=data['start_date']:
        v.add_error('end_date', 'End date must be after start date.')

    tenants=[]
    tenant_ids=form.getlist('tenant_ids')
    if not tenant_ids:
        v.add_error('tenant_ids', 'Please select at least one tenant.')
    for tenant_id in tenant_ids:
        tenant=db.session.get(Tenant, int(tenant_id)) if tenant_id.isdigit() else None
        if tenant is None:
            v.add_error('tenant_ids', 'One of the selected tenants no longer exists. Please review the tenant list.')
            break
        tenants.append(tenant)
    data['tenants']=tenants

    for field in ('refundable_deposit', 'nonrefundable_deposit', 'cars', 'pets'):
        if data[field] is None:
            data[field]=0

    return data, v.errors


@leases_bp.route('/new', methods=['POST', 'GET'])
@login_required
def add_lease():
    if request.method=='POST':
        data, errors=validate_lease_form(request.form)
        if errors:
            tenants, properties=lease_form_options()
            return render_template('leases/form.html', lease=None, tenants=tenants, properties=properties, errors=errors), 400

        lease=Lease(
            property_id=data['property'].id,
            start_date=data['start_date'],
            end_date=data['end_date'],
            monthly_rent=data['monthly_rent'],
            rent_due_date=data['rent_due_date'],
            refundable_deposit=data['refundable_deposit'],
            nonrefundable_deposit=data['nonrefundable_deposit'],
            cars=data['cars'],
            pets=data['pets'],
            status='expired' if data['end_date']<date.today() else 'active',
        )
        lease.tenants=data['tenants']
        db.session.add(lease)
        data['property'].is_occupied=True

        db.session.commit()
        flash('Lease added successfully')
        return redirect(url_for('leases.list_leases'))

    tenants, properties=lease_form_options()
    return render_template('leases/form.html', lease=None, tenants=tenants, properties=properties, errors={})

    
@leases_bp.route('/<int:lease_id>/edit', methods=['POST', 'GET'])
@login_required
def edit_lease(lease_id):
    lease=Lease.query.get_or_404(lease_id)
    if request.method=='POST':
        data, errors=validate_lease_form(request.form, lease=lease)
        if errors:
            tenants, properties=lease_form_options(lease)
            return render_template('leases/form.html', lease=lease, tenants=tenants, properties=properties, errors=errors), 400

        lease.property_id=data['property'].id
        lease.start_date=data['start_date']
        lease.end_date=data['end_date']
        lease.monthly_rent=data['monthly_rent']
        lease.rent_due_date=data['rent_due_date']
        lease.refundable_deposit=data['refundable_deposit']
        lease.nonrefundable_deposit=data['nonrefundable_deposit']
        lease.cars=data['cars']
        lease.pets=data['pets']
        lease.status=data['status']
        lease.tenants=data['tenants']

        if lease.end_date<date.today() and lease.status=='active':
            lease.status='expired'
            flash('This lease is automatically set as expired because end date has passed.')

        db.session.commit()
        flash('Lease updated successfully')
        return redirect(url_for('leases.list_leases'))

    tenants, properties=lease_form_options(lease)
    return render_template('leases/form.html', lease=lease, tenants=tenants, properties=properties, errors={})
    

@leases_bp.route('/<int:lease_id>/delete', methods=['POST'])
@login_required
def delete_lease(lease_id):
    lease=Lease.query.get_or_404(lease_id)
    if lease.payments:
        flash('Cannot delete the lease with payment history. Terminate it instead.')
        return redirect(url_for('leases.list_leases'))

    db.session.delete(lease)
    property=Property.query.get_or_404(lease.property_id)
    if property.is_occupied:
        property.is_occupied=False
    db.session.commit()
    flash('Lease deleted successfully')
    return redirect(url_for('leases.list_leases'))





