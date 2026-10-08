from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import StaffUser
from app.validation import FormValidator

auth_bp=Blueprint('auth', __name__)

def safe_next_url(target):
    """Only allow redirects back into this site after login."""
    if target and target.startswith('/') and not target.startswith('//') and '\\' not in target:
        return target
    return url_for('dashboard.index')

 
@auth_bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method=='POST':
        v=FormValidator(request.form)
        username=v.string('username', 'Username', required=True, max_length=200)
        password=request.form.get('password') or ''
        if not password:
            v.add_error('password', 'Password is required.')
        if not v.is_valid:
            return render_template('auth/login.html', errors=v.errors), 400

        user=StaffUser.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(safe_next_url(request.args.get('next')))
        return render_template('auth/login.html', errors={'login': 'Incorrect username or password. Please try again.'}), 401
    return render_template('auth/login.html', errors={})

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))