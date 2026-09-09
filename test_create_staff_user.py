from app import create_app, db
from app.models import StaffUser

app=create_app()
with app.app_context():
    existing=StaffUser.query.filter_by(username='admin').first()
    if not existing:
        user=StaffUser(username='admin', role='1234')
        user.set_password('12345678')
        db.session.add(user)
        db.session.commit()
        print("Staff user created")
    else:
        print("User already exists")
