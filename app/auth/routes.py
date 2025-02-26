from flask import render_template, request, redirect, url_for, session, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import bp
from app.auth.models import User, users_db

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect to account
    if current_user.is_authenticated:
        return redirect(url_for('auth.account'))
    
    # Display login form for GET requests
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    # Handle form submission for POST requests
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Validate form data
    if not username or not password:
        return render_template('auth/login.html', error='Username and password are required')
    
    # Check credentials
    if User.check_password(username, password):
        user = User(username)
        login_user(user)
        session['user'] = username
        return redirect(url_for('auth.account'))
    else:
        return render_template('auth/login.html', error='Invalid username or password')

@bp.route('/logout')
def logout():
    session.pop('user', None)
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    # If already logged in, redirect to account
    if current_user.is_authenticated:
        return redirect(url_for('auth.account'))
    
    # Handle form submission for POST requests
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        
        # Validate form data
        if not username or not password:
            return render_template('auth/register.html', error='Username and password are required')
        
        if password != password2:
            return render_template('auth/register.html', error='Passwords do not match')
        
        # Add new user
        if User.add_user(username, password):
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            return render_template('auth/register.html', error='Username already exists')
    
    # Display registration form for GET requests
    return render_template('auth/register.html')

@bp.route('/account')
@login_required
def account():
    return render_template('auth/account.html', username=current_user.username)

@bp.route('/users')
@login_required
def list_users():
    users_list = User.get_all_users()
    return render_template('auth/users.html', users=users_list)

