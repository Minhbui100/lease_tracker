from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app import db
from app.models import Property, MaintenanceRequest, Image
from datetime import datetime, timezone

properties_bp=Blueprint('properties', __name__, url_prefix='/properties')

@properties_bp.route('/')
@login_required
def list_properties():
    properties=Property.query.order_by(Property.state, Property.city, Property.zip, Property.id).all()
    return render_template('properties/list.html', properties=properties)

@properties_bp.route('/new', methods=['GET', 'POST'])
@login_required
def add_property():
    if request.method=='POST':
        address=request.form['address']
        city=request.form['city']
        existing=Property.query.filter_by(address=address, city=city).first()
        if existing:
            flash('This property exists in the system')
            unsaved = Property(
                address=address,
                city=city,
                state=request.form['state'],
                zip=request.form['zip'],
                county=request.form['county'],
                property_type=request.form['property_type'],
                year_built=request.form['year_built'] or None,
                current_value=request.form['current_value'] or None,
                bedrooms=request.form['bedrooms'] or None,
                bathrooms=request.form['bathrooms'] or None,
                area=request.form['area'] or None,
            )
            return render_template('properties/form.html', property=unsaved)

        
        property=Property(
            address=request.form['address'],
            city=request.form['city'],
            state=request.form['state'],
            zip=request.form['zip'],
            county=request.form['county'],
            property_type=request.form['property_type'],
            year_built=request.form['year_built'] or None,
            current_value=request.form['current_value'] or None,
            bedrooms=request.form['bedrooms'] or None,
            bathrooms=request.form['bathrooms'] or None,
            area=request.form['area'] or None,
            is_occupied=False,
        )
        
        db.session.add(property)
        db.session.commit()
        flash('Property added successfully')
        return redirect(url_for('properties.list_properties'))

    return render_template('properties/form.html', property=None)

@properties_bp.route('/<int:property_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_property(property_id):
    property=Property.query.get_or_404(property_id)
    if request.method=='POST':
        property.address=request.form['address']
        property.city=request.form['city']
        property.state=request.form['state']
        property.zip=request.form['zip']
        property.county=request.form['county']
        property.property_type=request.form['property_type']
        property.year_built=request.form['year_built'] or None
        property.current_value=request.form['current_value'] or None
        property.bedrooms=request.form['bedrooms'] or None
        property.bathrooms=request.form['bathrooms'] or None
        property.area=request.form['area'] or None
    
        db.session.commit()
        flash('Property updated successfully')
        return redirect(url_for('properties.list_properties'))

    return render_template('properties/form.html', property=property)


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


@properties_bp.route('/<int:property_id>')
@login_required
def view_property(property_id):
    property_obj=Property.query.get_or_404(property_id)
    maintenance_history=MaintenanceRequest.query.filter_by(property_id=property_id).order_by(MaintenanceRequest.submission_time.desc()).all()
    return render_template('properties/detail.html', property=property_obj, maintenance_history=maintenance_history)



import os
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@properties_bp.route('/<int:property_id>/images/add', methods=['POST'])
@login_required
def add_image(property_id):
    file = request.files.get('photo')

    if not file or file.filename == '':
        flash('Please choose a photo to upload.')
        return redirect(url_for('properties.view_property', property_id=property_id))

    if not allowed_file(file.filename):
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
    image = Image.query.get_or_404(image_id)

    file_path = os.path.join(current_app.root_path, 'static', 'uploads', image.link)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(image)
    db.session.commit()
    flash('Photo deleted')
    return redirect(url_for('properties.view_property', property_id=property_id))
