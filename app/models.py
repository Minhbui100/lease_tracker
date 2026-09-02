from app import db
from datetime import datetime




class Property(db.Model):
    __tablename__='property'
    id=db.Column(db.Integer, primary_key=True)
    address=db.Column(db.String(250), nullable=False)
    city=db.Column(db.String(100), nullable=False)
    state=db.Column(db.String(100), nullable=False)
    zip=db.Column(db.String(100), nullable=False)
    county=db.Column(db.String(100), nullable=False)
    property_type=db.Column(db.String(100), nullable=False)
    year_built=db.Column(db.Integer)
    current_value=db.Column(db.Numeric(12,2))
    bedrooms=db.Column(db.Integer)
    bathrooms=db.Column(db.Numeric(3,2))
    area=db.Column(db.Numeric(12,2))
    is_occupied=db.Column(db.Boolean, default=False)
    created_at=db.Column(db.Date, default=datetime.utcnow)

    leases=db.relationship('Lease', backref='property', lazy=True)
    maintenance_requests=db.relationship('MaintenanceRequest', backref='property', lazy=True)
    images=db.relationship('Image', backref='property', lazy=True)



class Tenant(db.Model):
    __tablename__='tenant'
    id=db.Column(db.Integer, primary_key=True)
    first_name=db.Column(db.String(100), nullable=False)
    last_name=db.Column(db.String(100), nullable=False)
    dob=db.Column(db.Date)
    driver_license=db.Column(db.String(30))
    phone=db.Column(db.String(20))
    email=db.Column(db.String(200))
    created_at=db.Column(db.Date, default=datetime.utcnow)

    maintenance_requests=db.relationship('MaintenanceRequest', backref='tenant', lazy=True)
    emergency_contacts=db.relationship('EmergencyContact', backref='tenant', lazy=True)
    leases=db.relationship('Lease', secondary='lease_tenant', backref='tenants', lazy=True)



class Lease(db.Model):
    __tablename__='lease'
    id=db.Column(db.Integer, primary_key=True)
    property_id=db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    start_date=db.Column(db.Date, nullable=False)
    end_date=db.Column(db.Date, nullable=False)
    monthly_rent=db.Column(db.Numeric(10,2), nullable=False)
    rent_due_date=db.Column(db.Integer, nullable=False)
    refundable_deposit=db.Column(db.Numeric(10,2))
    nonrefundable_deposit=db.Column(db.Numeric(10,2))
    cars=db.Column(db.Integer)
    pets=db.Column(db.Integer)
    status=db.Column(db.String(20), default='active')
    created_at=db.Column(db.DateTime, default=datetime.utcnow)

    payments=db.relationship('Payment', backref='lease', lazy=True)
    dependents=db.relationship('Dependence', backref='lease', lazy=True)

class LeaseTenant(db.Model):
    __tablename__='lease_tenant'
    tenant_id=db.Column(db.Integer, db.ForeignKey('tenant.id'), primary_key=True)
    lease_id=db.Column(db.Integer, db.ForeignKey('lease.id'), primary_key=True)


class Payment(db.Model):
    __tablename__='payment'
    id=db.Column(db.Integer, primary_key=True)
    lease_id=db.Column(db.Integer, db.ForeignKey('lease.id'), nullable=False)
    rent_due_date=db.Column(db.Date, nullable=False)
    amount=db.Column(db.Numeric(10,2), nullable=False)
    status=db.Column(db.String(20), default='pending')
    created_at=db.Column(db.DateTime, default=datetime.utcnow)


class MaintenanceRequest(db.Model):
    __tablename__='maintenance_request'
    id=db.Column(db.Integer, primary_key=True)
    tenant_id=db.Column(db.Integer, db.ForeignKey('tenant.id'))
    property_id=db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    description=db.Column(db.Text, nullable=False)
    status=db.Column(db.String(20), default='open')
    submission_time=db.Column(db.DateTime)
    resolution_time=db.Column(db.DateTime)
    material_cost=db.Column(db.Numeric(20,2))
    labor_cost=db.Column(db.Numeric(20,2))
    paid_by=db.Column(db.String(20), default='owner')
    created_at=db.Column(db.DateTime, default=datetime.utcnow)



class EmergencyContact(db.Model):
    __tablename__='emergency_contact'
    id=db.Column(db.Integer, primary_key=True)
    first_name=db.Column(db.String(100), nullable=False)
    last_name=db.Column(db.String(100), nullable=False)
    tenant_id=db.Column(db.Integer, db.ForeignKey('tenant.id'), nullable=False)
    address=db.Column(db.String(500))
    phone=db.Column(db.String(30), nullable=False)
    email=db.Column(db.String(200))

class Dependence(db.Model):
    __tablename__='dependence'
    id=db.Column(db.Integer, primary_key=True)
    first_name=db.Column(db.String(100), nullable=False)
    last_name=db.Column(db.String(100), nullable=False)
    dob=db.Column(db.Date)
    relationship_type=db.Column('relationship', db.String(50), nullable=False)
    lease_id=db.Column(db.Integer, db.ForeignKey('lease.id'), nullable=False)

class Image(db.Model):
    __tablename__='image'
    id=db.Column(db.Integer, primary_key=True)
    link=db.Column(db.Text, nullable=False)
    property_id=db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)


from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class StaffUser(db.Model, UserMixin):
    __tablename__='staff_user'
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(200), unique=True, nullable=False)
    password_hash=db.Column(db.String(300), nullable=False)
    role=db.Column(db.String(50), default='staff')
    created_at=db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash=generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)