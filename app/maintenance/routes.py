from flask import flash, Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from app import db
from app.models import MaintenanceRequest, Property, Tenant
from datetime import datetime, timezone


maintenance_bp=Blueprint('maintenance', __name__, url_prefix='/maintenance')

@maintenance_bp.route('/')
@login_required
def list_requests():
    requests=MaintenanceRequest.query.order_by(MaintenanceRequest.submission_time).all()
    return render_template('maintenance/list.html', requests=requests)

@maintenance_bp.route('/new', methods=['POST', 'GET'])
@login_required
def add_request():
    if request.method=='POST':
        maintenance_request=MaintenanceRequest(
            reported_by=request.form.get('reported_by') or 'staff',
            property_id=request.form['property_id'],
            description=request.form['description'],
            status='open',
            submission_time=datetime.now(timezone.utc) 
        )
        db.session.add(maintenance_request)
        db.session.commit()
        flash('Request added successfully.')
        return redirect(url_for('maintenance.list_requests'))
    properties=Property.query.order_by(Property.state, Property.city, Property.address).all()
    return render_template('maintenance/form.html', properties=properties, maintenance_request=None)



@maintenance_bp.route('/<int:request_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_request(request_id):
    maintenance_request = MaintenanceRequest.query.get_or_404(request_id)

    if request.method == 'POST':
        maintenance_request.property_id = request.form['property_id']
        maintenance_request.reported_by = request.form.get('reported_by') or 'staff'        
        maintenance_request.description = request.form['description']
        maintenance_request.status = request.form['status']
        maintenance_request.material_cost = request.form['material_cost'] or None
        maintenance_request.labor_cost = request.form['labor_cost'] or None
        maintenance_request.paid_by = request.form.get('paid_by') or 'owner'

        if maintenance_request.status == 'resolved' and not maintenance_request.resolution_time:
            maintenance_request.resolution_time = datetime.now(timezone.utc)

        db.session.commit()
        flash('Maintenance request updated successfully')
        return redirect(url_for('maintenance.list_requests'))

    properties = Property.query.order_by(Property.address).all()
    return render_template('maintenance/form.html', maintenance_request=maintenance_request,
                            properties=properties)


@maintenance_bp.route('/<int:request_id>/delete', methods=['POST'])
@login_required
def delete_request(request_id):
    maintenance_request = MaintenanceRequest.query.get_or_404(request_id)
    db.session.delete(maintenance_request)
    db.session.commit()
    flash('Maintenance request deleted')
    return redirect(url_for('maintenance.list_requests'))