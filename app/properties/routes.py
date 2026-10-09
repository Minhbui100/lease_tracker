from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required
from app import db
from app.models import Property, MaintenanceRequest, Image, PropertyExpense, Payment, Lease, MaintenanceRequest
from app.validation import FormValidator, ZIP_RE
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy import func

properties_bp=Blueprint('properties', __name__, url_prefix='/properties')

@properties_bp.route('/')
@login_required
def list_properties():
    properties=Property.query.order_by(Property.state, Property.city, Property.zip, Property.id).all()
    return render_template('properties/list.html', properties=properties)

PROPERTY_TYPES={'single-family', 'multi-family'}
PROPERTY_FIELDS=('address', 'city', 'state', 'zip', 'county', 'property_type',
                 'year_built', 'current_value', 'bedrooms', 'bathrooms', 'area')


def validate_property_form(form, property_id=None):
    """Returns (cleaned_data, errors) for the property add/edit form."""
    v=FormValidator(form)
    data={
        'address': v.string('address', 'Address', required=True, max_length=250),
        'city': v.string('city', 'City', required=True, max_length=100),
        'state': v.string('state', 'State', required=True, max_length=100),
        'zip': v.string('zip', 'Zipcode', required=True, max_length=10, pattern=ZIP_RE,
                        pattern_message='Zipcode must be 5 digits (e.g. 12345) or ZIP+4 (e.g. 12345-6789).'),
        'county': v.string('county', 'County', required=True, max_length=100),
        'property_type': v.choice('property_type', 'Property type', PROPERTY_TYPES, required=True),
        'year_built': v.integer('year_built', 'Year built', min_value=1700, max_value=date.today().year+2),
        'current_value': v.decimal('current_value', 'Current value', min_value=0, max_value=Decimal('9999999999.99')),
        'bedrooms': v.integer('bedrooms', 'Bedrooms', min_value=0, max_value=50),
        'bathrooms': v.decimal('bathrooms', 'Bathrooms', min_value=0, max_value=Decimal('9.99')),
        'area': v.decimal('area', 'Area', min_value=Decimal('0.01'), max_value=Decimal('9999999999.99')),
    }

    if data['address'] and data['city']:
        duplicate=Property.query.filter(
            db.func.lower(Property.address)==data['address'].lower(),
            db.func.lower(Property.city)==data['city'].lower(),
        )
        if property_id is not None:
            duplicate=duplicate.filter(Property.id!=property_id)
        if duplicate.first():
            v.add_error('address', f"A property at {data['address']}, {data['city']} already exists.")

    return data, v.errors


@properties_bp.route('/new', methods=['GET', 'POST'])
@login_required
def add_property():
    if request.method=='POST':
        data, errors=validate_property_form(request.form)
        if errors:
            return render_template('properties/form.html', property=None, errors=errors), 400

        property=Property(is_occupied=False, **data)
        db.session.add(property)
        db.session.commit()
        flash('Property added successfully')
        return redirect(url_for('properties.list_properties'))

    return render_template('properties/form.html', property=None, errors={})

@properties_bp.route('/<int:property_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_property(property_id):
    property=Property.query.get_or_404(property_id)
    if request.method=='POST':
        data, errors=validate_property_form(request.form, property_id=property.id)
        if errors:
            return render_template('properties/form.html', property=property, errors=errors), 400

        for field in PROPERTY_FIELDS:
            setattr(property, field, data[field])
        db.session.commit()
        flash('Property updated successfully')
        return redirect(url_for('properties.list_properties'))

    return render_template('properties/form.html', property=property, errors={})


@properties_bp.route('/<int:property_id>/delete', methods=['POST'])
@login_required
def delete_property(property_id):
    property=Property.query.get_or_404(property_id)
    if property.leases:
        flash('Cannot delete a property with existing lease')
        return redirect(url_for('properties.list_properties'))
    db.session.delete(property)
    db.session.commit()
    flash('Property deleted successfully')
    return redirect(url_for('properties.list_properties'))

EXPENSE_CATEGORIES = {
        'down_payment': 'Down payment',
        'closing_costs': 'Closing costs',
        'mortgage': 'Mortgage',
        'hoa': 'HOA',
        'property_tax': 'Property tax',
        'insurance': 'Insurance',
        'utilities': 'Utilities',
        'management_fee': 'Management fee',
        'remodel': 'Remodel',
        'legal': 'Legal',
        'other': 'Other',
    }

@properties_bp.route('/<int:property_id>')
@login_required
def view_property(property_id):
    
    property_obj=Property.query.get_or_404(property_id)
    maintenance_history=MaintenanceRequest.query.filter_by(property_id=property_id).order_by(MaintenanceRequest.submission_time.desc()).all()

    #cash_in is all payments from the property's tenants
    cash_in=Decimal(db.session.query(func.coalesce(func.sum(Payment.amount), 0))
                    .join(Lease, Payment.lease_id==Lease.id)
                    .filter(Lease.property_id==property_id, Payment.status=='paid')
                    .scalar())

    #cash_out is maintenance and property expenses
    maintenance_out=Decimal(db.session.query(func.coalesce(func.sum(func.coalesce(MaintenanceRequest.labor_cost,0)+func.coalesce(MaintenanceRequest.material_cost,0)),0 ))
                            .filter(MaintenanceRequest.property_id==property_id, MaintenanceRequest.paid_by=='owner')
                            .scalar())

    expenses=PropertyExpense.query.filter_by(property_id=property_id).order_by(PropertyExpense.expense_date.desc()).all()
    expenses_out=sum((e.amount for e in expenses), Decimal('0'))

    cash_out=maintenance_out+expenses_out
    balance=cash_in-cash_out

    category_totals={key: Decimal('0') for key in EXPENSE_CATEGORIES}
    for e in expenses:
        category_totals[e.category]+=e.amount
    
    return render_template('properties/detail.html', property=property_obj, maintenance_history=maintenance_history, 
                           expenses=expenses, categories=EXPENSE_CATEGORIES, maintenance_out=maintenance_out,
                           cash_in=cash_in, cash_out=cash_out, balance=balance, category_totals=category_totals)


@properties_bp.route('/<int:property_id>/expenses/add', methods=['POST'])
@login_required
def add_expense(property_id):
    Property.query.get_or_404(property_id)
    v=FormValidator(request.form)
    data={
        'category':v.choice('category', 'Category', set(EXPENSE_CATEGORIES), required=True),
        'amount':v.decimal('amount', 'Amount', required=True, min_value=Decimal('0.01'), max_value=Decimal('9999999999.99')),
        'expense_date':v.date('expense_date', 'Date', required=True, min_value=date(1900,1,1)),
        'memo':v.string('memo', 'Memo', max_length=100),
    }
    if v.errors:
        for msg in v.errors.values():
            flash(msg if isinstance(msg, str) else ' '.join(msg))
        return redirect(url_for('properties.view_property', property_id=property_id))

    db.session.add(PropertyExpense(property_id=property_id, **data))
    db.session.commit()
    flash('Expense added')
    return redirect(url_for('properties.view_property', property_id=property_id)) 

@properties_bp.route('/<int:property_id>/expenses/<int:expense_id>/delete', methods=['POST'])
@login_required
def delete_expense(property_id, expense_id):
    expense=PropertyExpense.query.filter_by(id=expense_id, property_id=property_id).first()
    db.session.delete(expense)
    db.commit()
    flash('Expense deleted')
    return redirect(url_for('properties.view_property', property_id=property_id)) 


"""class PropertyExpense(db.Model):
    __tablename__='property_expense'
    id=db.Column(db.Integer, primary_key=True)
    property_id=db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    category=db.Column(db.String(40), nullable=False)
    amount=db.Column(db.Numeric(12,2), nullable=False)
    expense_date=db.Column(db.Date, nullable=False)
    memo=db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
"""

import os
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@properties_bp.route('/<int:property_id>/images/add', methods=['POST'])
@login_required
def add_image(property_id):
    Property.query.get_or_404(property_id)
    file = request.files.get('photo')

    if not file or file.filename == '':
        flash('Please choose a photo to upload.')
        return redirect(url_for('properties.view_property', property_id=property_id))

    if not allowed_file(file.filename) or not (file.mimetype or '').startswith('image/'):
        flash('Unsupported file type. Please upload a PNG, JPG, GIF, or WEBP image.')
        return redirect(url_for('properties.view_property', property_id=property_id))

    filename = secure_filename(file.filename)
    unique_filename = f"{property_id}_{int(datetime.now(timezone.utc).timestamp())}_{filename}"
    upload_path = os.path.join(current_app.root_path, 'static', 'uploads', unique_filename)
    file.save(upload_path)

    image = Image(property_id=property_id, link=unique_filename)
    db.session.add(image)
    db.session.commit()
    flash('Photo uploaded')
    return redirect(url_for('properties.view_property', property_id=property_id))


@properties_bp.route('/<int:property_id>/images/<int:image_id>/delete', methods=['POST'])
@login_required
def delete_image(property_id, image_id):
    image = Image.query.filter_by(id=image_id, property_id=property_id).first_or_404()

    file_path = os.path.join(current_app.root_path, 'static', 'uploads', image.link)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(image)
    db.session.commit()
    flash('Photo deleted')
    return redirect(url_for('properties.view_property', property_id=property_id))
