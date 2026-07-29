from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.extensions import db
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('events.list_events'))
        
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not full_name or not username or not email or not password or not confirm_password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.register'))
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))
            
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return redirect(url_for('auth.register'))
            
        # Email format validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email format.', 'danger')
            return redirect(url_for('auth.register'))
            
        # Reserved usernames
        reserved_usernames = ['admin', 'administrator', 'root']
        if username.lower() in reserved_usernames:
            flash('Username is reserved.', 'danger')
            return redirect(url_for('auth.register'))
            
        # Check duplicates
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            if existing_user.username == username:
                flash('Username already exists.', 'danger')
            else:
                flash('Email already exists.', 'danger')
            return redirect(url_for('auth.register'))
            
        new_user = User(full_name=full_name, username=username, email=email, role='user', is_active=True)
        new_user.set_password(password)
        db.session.add(new_user)
        try:
            db.session.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('auth.register'))
        
    return render_template('register.html')

from sqlalchemy import func

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('events.list_events'))
        
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')
        
        if not identifier or not password:
            flash('Both fields are required.', 'danger')
            return redirect(url_for('auth.login'))
            
        identifier_lower = identifier.lower()
        user = User.query.filter(
            (func.lower(User.email) == identifier_lower) | 
            (func.lower(User.username) == identifier_lower)
        ).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Account is inactive.', 'danger')
                return redirect(url_for('auth.login'))
                
            login_user(user)
            flash('Login successful.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('events.list_events'))
        else:
            flash('Invalid username/email or password.', 'danger')
            
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
