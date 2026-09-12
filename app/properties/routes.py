from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app import db
from app.models import Property 

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
