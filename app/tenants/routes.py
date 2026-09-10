from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app import db
from app.models import Tenant

tenants_bp=Blueprint('tenants', __name__, url_prefix='/tenants')

@tenants_bp.route('/')
@login_required
def list_tenants():
    tenants=Tenant.query.order_by(Tenant.first_name).all()
    return render_template('tenants/list.html', tenants=tenants)

@tenants_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_tenant():
    if request.method=='POST':
        tenant=Tenant(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            dob=request.form['dob'] or None,
            driver_license=request.form['driver_license'] or None,
            phone=request.form['phone'] or None,
            email=request.form['email'] or None,
        )
        db.session.add(tenant)
        db.session.commit()
        flash('Tenant added successfully')
        return redirect(url_for('tenants.list_tenants'))
    return render_template('tenants/form.html', tenant=None)

@tenants_bp.route('/<int:tenant_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_tenant(tenant_id):
    tenant=Tenant.query.get_or_404(tenant_id)

    if request.method=='POST':
        tenant.first_name=request.form['first_name']
        tenant.last_name=request.form['last_name']
        tenant.dob=request.form['dob']
        tenant.driver_license=request.form['driver_license']
        tenant.phone=request.form['phone']
        tenant.email=request.form['email']

        db.session.commit()
        flash('Tenant updated successfully')
        return redirect(url_for('tenants.list_tenants'))

    return render_template('tenants/form.html', tenant=tenant)


@tenants_bp.route('/<int:tenant_id>/delete', methods=['POST'])
@login_required
def delete_tenant(tenant_id):
    tenant=Tenant.query.get_or_404(tenant_id)

    db.session.delete(tenant)
    db.session.commit()
    flash('Tenant deleted successfully')
    return redirect(url_for('tenants.list_tenants'))

