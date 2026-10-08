import re
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app import db
from app.models import Tenant
from app.validation import FormValidator
from datetime import date

tenants_bp=Blueprint('tenants', __name__, url_prefix='/tenants')

LICENSE_RE=re.compile(r'^[A-Za-z0-9 -]+$')
TENANT_FIELDS=('first_name', 'last_name', 'dob', 'driver_license', 'phone', 'email')


def validate_tenant_form(form):
    """Returns (cleaned_data, errors) for the tenant add/edit form."""
    v=FormValidator(form)
    today=date.today()
    data={
        'first_name': v.string('first_name', 'First name', required=True, max_length=100),
        'last_name': v.string('last_name', 'Last name', required=True, max_length=100),
        'dob': v.date('dob', 'Date of birth', min_value=date(1900, 1, 1), max_value=today),
        'driver_license': v.string('driver_license', "Driver's license", max_length=30, pattern=LICENSE_RE,
                                   pattern_message="Driver's license can only contain letters, numbers, spaces, and dashes."),
        'phone': v.phone('phone'),
        'email': v.email('email'),
    }

    dob=data['dob']
    if dob and (today.year-dob.year-((today.month, today.day)<(dob.month, dob.day)))<18:
        v.add_error('dob', 'Tenant must be at least 18 years old to sign a lease.')

    return data, v.errors


@tenants_bp.route('/')
@login_required
def list_tenants():
    tenants=Tenant.query.order_by(Tenant.first_name).all()
    return render_template('tenants/list.html', tenants=tenants)

@tenants_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_tenant():
    if request.method=='POST':
        data, errors=validate_tenant_form(request.form)
        if errors:
            return render_template('tenants/form.html', tenant=None, errors=errors), 400

        tenant=Tenant(**data)
        db.session.add(tenant)
        db.session.commit()
        flash('Tenant added successfully')
        return redirect(url_for('tenants.list_tenants'))
    return render_template('tenants/form.html', tenant=None, errors={})

@tenants_bp.route('/<int:tenant_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_tenant(tenant_id):
    tenant=Tenant.query.get_or_404(tenant_id)

    if request.method=='POST':
        data, errors=validate_tenant_form(request.form)
        if errors:
            return render_template('tenants/form.html', tenant=tenant, errors=errors), 400

        for field in TENANT_FIELDS:
            setattr(tenant, field, data[field])
        db.session.commit()
        flash('Tenant updated successfully')
        return redirect(url_for('tenants.list_tenants'))

    return render_template('tenants/form.html', tenant=tenant, errors={})


@tenants_bp.route('/<int:tenant_id>/delete', methods=['POST'])
@login_required
def delete_tenant(tenant_id):
    tenant=Tenant.query.get_or_404(tenant_id)
    if tenant.leases:
        flash(f'Cannot delete {tenant.first_name} {tenant.last_name} because they are on a lease. Remove them from the lease first.')
        return redirect(url_for('tenants.list_tenants'))
    if tenant.emergency_contacts:
        flash(f'Cannot delete {tenant.first_name} {tenant.last_name} because they have emergency contacts on file.')
        return redirect(url_for('tenants.list_tenants'))

    db.session.delete(tenant)
    db.session.commit()
    flash('Tenant deleted successfully')
    return redirect(url_for('tenants.list_tenants'))
