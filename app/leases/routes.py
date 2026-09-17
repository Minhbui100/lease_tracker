from flask import redirect, render_template, flash, Blueprint, url_for, request
from flask_login import login_required
from app import db
from app.models import Lease, Property, Tenant
from datetime import date

leases_bp=Blueprint('leases', __name__, url_prefix='/leases')

@leases_bp.route('/')
@login_required
def list_leases():
    leases=Lease.query.order_by(Lease.start_date).all()
    return render_template('leases/list.html', leases=leases)

@leases_bp.route('/new', methods=['POST', 'GET'])
@login_required
def add_lease():
    if request.method=='POST':
        start_date=request.form['start_date']
        end_date=request.form['end_date']
        if end_date <= start_date:
            flash('End date must be after start date.')
            tenants = Tenant.query.order_by(Tenant.first_name, Tenant.last_name).all()
            available_properties = Property.query.filter_by(is_occupied=False).all()
            return render_template('leases/form.html', lease=None, tenants=tenants, properties=available_properties)

        today=date.today().isoformat()
        if end_date<today:
            leases_status='expired'
        else: 
            leases_status='active'
        lease=Lease(
            property_id=request.form['property_id'],
            start_date=request.form['start_date'],
            end_date=request.form['end_date'],
            monthly_rent=request.form['monthly_rent'],
            rent_due_date=request.form['rent_due_date'],
            refundable_deposit=request.form['refundable_deposit'] or 0,
            nonrefundable_deposit=request.form['nonrefundable_deposit'] or 0,
            cars=request.form['cars'] or 0,
            pets=request.form['pets'] or 0,
            status=leases_status                  
        )
        db.session.add(lease)

        tenant_ids=request.form.getlist('tenant_ids')
        for tenant_id in tenant_ids:
            tenant=Tenant.query.get(int(tenant_id))
            if tenant:
                lease.tenants.append(tenant)

        property=Property.query.get(lease.property_id)
        property.is_occupied=True

        db.session.commit()
        flash('Lease added successfully')
        return redirect(url_for('leases.list_leases'))

    tenants=Tenant.query.order_by(Tenant.first_name, Tenant.last_name).all()
    available_properties=Property.query.filter_by(is_occupied=False).all()
    return render_template('leases/form.html', lease=None, tenants=tenants, properties=available_properties)

    
@leases_bp.route('/<int:lease_id>/edit', methods=['POST', 'GET'])
@login_required
def edit_lease(lease_id):
    lease=Lease.query.get_or_404(lease_id)
    if request.method=='POST':
        start_date=request.form['start_date']
        end_date=request.form['end_date']
        tenants = Tenant.query.order_by(Tenant.first_name, Tenant.last_name).all()
        available_properties = Property.query.filter((Property.is_occupied == False) | (Property.id == lease.property_id)).all()        
        today = date.today().isoformat()
        if end_date <= start_date:
            flash('End date must be after start date.')
            return render_template('leases/form.html', lease=lease, tenants=tenants, properties=available_properties)
        
        
        lease.property_id=request.form['property_id']
        lease.start_date=request.form['start_date']
        lease.end_date=request.form['end_date']
        lease.monthly_rent=request.form['monthly_rent']
        lease.rent_due_date=request.form['rent_due_date']
        lease.refundable_deposit=request.form['refundable_deposit'] or 0
        lease.nonrefundable_deposit=request.form['nonrefundable_deposit'] or 0
        lease.cars=request.form['cars'] or 0
        lease.pets=request.form['pets'] or 0
        lease.status=request.form['status']

        lease.tenants=[]
        tenant_ids=request.form.getlist('tenant_ids')
        for tenant_id in tenant_ids:
            tenant=Tenant.query.get(int(tenant_id))
            if tenant:
                lease.tenants.append(tenant)
                
        if end_date<today and lease.status=='active':
            lease.status='expired'
            flash('This lease is automatically set as expired because end date has passed.')
                        

        db.session.commit()
        flash('Lease updated successfully')
        return redirect(url_for('leases.list_leases'))

    tenants=Tenant.query.order_by(Tenant.first_name, Tenant.last_name).all()
    available_properties=Property.query.filter((Property.is_occupied==False) | (Property.id==lease.property_id)).all()
    return render_template('leases/form.html', lease=lease, tenants=tenants, properties=available_properties)
    

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





