from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate   import Migrate 
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date

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

    scheduler=BackgroundScheduler()
    with app.app_context():
        scheduler.add_job(func=expire_old_leases, trigger='cron', hour=0, minute=0)
    scheduler.start()
    return app

