from flask import flash, Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from app import db
from app.models import MaintenanceRequest, Property
from app.validation import FormValidator
from datetime import datetime, timezone
from decimal import Decimal


maintenance_bp=Blueprint('maintenance', __name__, url_prefix='/maintenance')

@maintenance_bp.route('/')
@login_required
def list_requests():
    requests=MaintenanceRequest.query.order_by(MaintenanceRequest.submission_time.desc()).all()
    return render_template('maintenance/list.html', requests=requests)

REPORTERS={'tenant', 'staff'}
REQUEST_STATUSES={'open', 'in_progress', 'resolved'}
PAYERS={'owner', 'renter'}
MAX_COST=Decimal('99999999.99')


def validate_request_form(form, is_edit=False):
    """Returns (cleaned_data, errors) for the maintenance request add/edit form."""
    v=FormValidator(form)
    data={
        'property': v.record('property_id', 'Property', Property),
        'reported_by': v.choice('reported_by', 'Reporter', REPORTERS, default='staff'),
        'description': v.string('description', 'Description', required=True, max_length=2000),
    }
    if is_edit:
        data['status']=v.choice('status', 'Status', REQUEST_STATUSES, required=True)
        data['material_cost']=v.decimal('material_cost', 'Material cost', min_value=0, max_value=MAX_COST)
        data['labor_cost']=v.decimal('labor_cost', 'Labor cost', min_value=0, max_value=MAX_COST)
        data['paid_by']=v.choice('paid_by', 'Payer', PAYERS, default='owner')
    return data, v.errors


def request_form_properties():
    return Property.query.order_by(Property.state, Property.city, Property.address).all()


@maintenance_bp.route('/new', methods=['POST', 'GET'])
@login_required
def add_request():
    if request.method=='POST':
        data, errors=validate_request_form(request.form)
        if errors:
            return render_template('maintenance/form.html', properties=request_form_properties(), maintenance_request=None, errors=errors), 400

        maintenance_request=MaintenanceRequest(
            reported_by=data['reported_by'],
            property_id=data['property'].id,
            description=data['description'],
            status='open',
            submission_time=datetime.now(timezone.utc) 
        )
        db.session.add(maintenance_request)
        db.session.commit()
        flash('Request added successfully.')
        return redirect(url_for('maintenance.list_requests'))
    return render_template('maintenance/form.html', properties=request_form_properties(), maintenance_request=None, errors={})



@maintenance_bp.route('/<int:request_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_request(request_id):
    maintenance_request = MaintenanceRequest.query.get_or_404(request_id)

    if request.method == 'POST':
        data, errors = validate_request_form(request.form, is_edit=True)
        if errors:
            return render_template('maintenance/form.html', maintenance_request=maintenance_request,
                                   properties=request_form_properties(), errors=errors), 400

        maintenance_request.property_id = data['property'].id
        maintenance_request.reported_by = data['reported_by']
        maintenance_request.description = data['description']
        maintenance_request.status = data['status']
        maintenance_request.material_cost = data['material_cost']
        maintenance_request.labor_cost = data['labor_cost']
        maintenance_request.paid_by = data['paid_by']

        if maintenance_request.status == 'resolved' and not maintenance_request.resolution_time:
            maintenance_request.resolution_time = datetime.now(timezone.utc)

        db.session.commit()
        flash('Maintenance request updated successfully')
        return redirect(url_for('maintenance.list_requests'))

    return render_template('maintenance/form.html', maintenance_request=maintenance_request,
                            properties=request_form_properties(), errors={})


@maintenance_bp.route('/<int:request_id>/delete', methods=['POST'])
@login_required
def delete_request(request_id):
    maintenance_request = MaintenanceRequest.query.get_or_404(request_id)
    db.session.delete(maintenance_request)
    db.session.commit()
    flash('Maintenance request deleted')
    return redirect(url_for('maintenance.list_requests'))