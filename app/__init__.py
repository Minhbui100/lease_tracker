from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate   import Migrate 
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date
import calendar

db=SQLAlchemy()
migrate=Migrate()
login_manager=LoginManager()


def expire_old_leases():
    from app.models import Lease

    today=date.today().isoformat()
    expired_count=0

    active_leases=Lease.query.filter_by(status='active').all()
    for lease in active_leases:
        if str(lease.end_date)<today:
            lease.status='expired'
            expired_count+=1

    if expired_count>0:
        db.session.commit()
        print(f"Marked {expired_count} lease(s) as expired.")

def late_payments():
    from app.models import Payment
    today=date.today().isoformat()
    late_count=0

    pending_payments=Payment.query.filter_by(status='pending').all()
    for payment in pending_payments:
        if str(payment.due_date)<today:
            payment.status='late'
            late_count+=1

    if late_count>0:
        db.session.commit()
        print(f"Marked {late_count} payment(s) as late.")

def generate_monthly_rent():
    from app.models import Lease, Payment

    today=date.today()
    month=today.month
    year=today.year
    lastday_month=calendar.monthrange(year, month)[1]
    active_leases=Lease.query.filter_by(status='active').all()
    created_count=0

    for lease in active_leases:
        due_day=min(lease.rent_due_date, lastday_month)
        due_date=date(year, month, due_day)

        existing=Payment.query.filter_by(lease_id=lease.id, due_date=due_date).first()
        if existing:
            continue
        payment=Payment(
            lease_id=lease.id,
            due_date=due_date,
            amount=lease.monthly_rent,
            memo=f"{today.strftime('%B %Y')} Rent",
            status='pending'
        )
        db.session.add(payment)
        created_count+=1

    if created_count>0:
        db.session.commit()
        print(f"Generated {created_count} new pending payment(s) for {today.strftime('%B %Y')}.")

  
def create_app():
    app=Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view='auth.login'

    from app import models

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(models.StaffUser, int(user_id))
    
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    from app.tenants.routes import tenants_bp
    app.register_blueprint(tenants_bp)

    from app.properties.routes import properties_bp
    app.register_blueprint(properties_bp)

    from app.leases.routes import leases_bp
    app.register_blueprint(leases_bp)

    from app.payments.routes import payments_bp
    app.register_blueprint(payments_bp)

    scheduler=BackgroundScheduler()
    with app.app_context():
        scheduler.add_job(func=expire_old_leases, trigger='cron', hour=0, minute=0)
        scheduler.add_job(func=generate_monthly_rent, trigger='cron', day=1, hour=0, minute=0)
        scheduler.add_job(func=late_payments, trigger='cron', hour=0, minute=0)
    scheduler.start()

    return app

