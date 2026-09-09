from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate   import Migrate 
from flask_login import LoginManager

db=SQLAlchemy()
migrate=Migrate()
login_manager=LoginManager()

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
    
    return app