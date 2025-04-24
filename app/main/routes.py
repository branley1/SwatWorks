<<<<<<< HEAD
from flask import render_template, redirect, url_for
from flask_login import current_user
from app.main import bp
=======
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.main import bp
from app.models import User, GIGS_DB_PATH, USERS_DB_PATH, COMMENTS_DB_PATH, get_db
import sqlite3
import datetime
import traceback
import re
import os
import json
>>>>>>> 6ac44c6 (SwatWorks final update)

@bp.route('/')
@bp.route('/index')
def index():
    # Render the index template
<<<<<<< HEAD
    return render_template('main/index.html') 
=======
    return render_template('main/index.html') 

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect to index
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Handle form submission
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validate form data
        if not username or not password:
            return render_template('auth/login.html', error='Username and password are required')
        
        # Authenticate user
        user = User.get(username)
        if user and User.check_password(username, password):
            login_user(user)
            
            next_page = request.args.get('next')
            
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            else:
                return redirect(url_for('main.index'))
        else:
            return render_template('auth/login.html', error='Invalid username or password')
    
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.pop('user', None)
    logout_user()
    return redirect(url_for('main.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    # If already logged in, redirect to index
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Handle form submission for POST requests
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        name = request.form.get('name') or None
        class_name = request.form.get('class_name') or None
        dorm = request.form.get('dorm') or None
        venmo = request.form.get('venmo') or None
        
        # Validate form data
        if not username or not password:
            return render_template('auth/register.html', error='Username and password are required', username=username, name=name, class_name=class_name, dorm=dorm, venmo=venmo)
        
        if password != password2:
            return render_template('auth/register.html', error='Passwords do not match', username=username, name=name, class_name=class_name, dorm=dorm, venmo=venmo)
        
        # Enforce password requirements
        if len(password) < 8:
            return render_template('auth/register.html', error='Password must be at least 8 characters long', username=username, name=name, class_name=class_name, dorm=dorm, venmo=venmo)
        if not re.search(r'[A-Z]', password):
            return render_template('auth/register.html', error='Password must contain at least one uppercase letter', username=username, name=name, class_name=class_name, dorm=dorm, venmo=venmo)
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return render_template('auth/register.html', error='Password must contain at least one special character', username=username, name=name, class_name=class_name, dorm=dorm, venmo=venmo)
        
        # Add new user
        if User.add_user(username, password, name, class_name, dorm, venmo):
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('main.login'))
        else:
            return render_template('auth/register.html', error='Username already exists or database error occurred', username=username, name=name, class_name=class_name, dorm=dorm, venmo=venmo)
    
    # Display registration form for GET requests
    return render_template('auth/register.html', class_name=None)

@bp.route('/account')
@login_required
def account():
    gigs = []
    gigs_error = None

    try:
        connection = sqlite3.connect(GIGS_DB_PATH)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        
        sql = "SELECT * FROM gigs WHERE user_id = ? ORDER BY date DESC"
        cursor.execute(sql, (current_user.id,))
        
        result = cursor.fetchall()
        gigs = [dict(row) for row in result]
        
        connection.close()
    except Exception as e:
        print(f"Error fetching gigs for user {current_user.id}: {e}") 
        gigs_error = "Could not load your gigs at this time. Please try again later."

    return render_template('auth/account.html', user=current_user, result=gigs, gigs_error=gigs_error)


@bp.route('/feed')
@login_required
def feed():
    gigs = []
    search = request.args.get('search', '').strip().lower()
    gig_type = request.args.get('gig_type', '').strip().lower()
    category = request.args.get('category', '').strip().lower()
    gig_sort = request.args.get('gig_sort', '').strip().lower()
    compensation = request.args.get('compensation', '').strip().lower()

    try:
        # Connect to gigs database and get all gigs
        gigs_conn = sqlite3.connect(GIGS_DB_PATH)
        gigs_conn.row_factory = sqlite3.Row
        gigs_cursor = gigs_conn.cursor()
        
        query = "SELECT * FROM gigs WHERE 1=1"
        params = []

        if search:
            query += " AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
        if gig_type in ['request', 'offer']:
            query += " AND LOWER(offer_status) LIKE ?"
            params.append(f"%{gig_type}%")
        if category in ['arts', 'tech', 'academics', 'physical', 'other']:
            query += " AND LOWER(category) LIKE ?"
            params.append(f"%{category}%")
        if compensation in ['no', 'yes']:
            query += " AND LOWER(compensation) LIKE ?"
            params.append(f"%{compensation}%")

        if gig_sort == 'date_asc':
            query += " ORDER BY date ASC"
        elif gig_sort == 'budget_asc':
            query += " ORDER BY budget ASC"
        elif gig_sort == 'budget_des':
            query += " ORDER BY budget DESC"
        else:
            query += " ORDER BY date DESC"
        gigs_cursor.execute(query, tuple(params))
        
        gigs_rows = gigs_cursor.fetchall()
        gigs = [dict(row) for row in gigs_rows]
        
        # Connect to users database and add user details to each gig
        users_conn = get_db()  # Connects to users.db
        users_conn.row_factory = sqlite3.Row
        users_cursor = users_conn.cursor()
        
        for gig in gigs:
            users_cursor.execute("SELECT username, name FROM users WHERE username = ?", (gig['user_id'],))
            user = users_cursor.fetchone()
            if user:
                gig['user_name'] = user['name']
                gig['poster_username'] = user['username']
            else:
                gig['user_name'] = None  
                gig['poster_username'] = gig['user_id']
        
        gigs_conn.close()
        users_conn.close()
        
    except Exception as e:
        error_message = f"Error fetching feed: {e}"
        print(error_message)
        traceback.print_exc()
        flash("Could not load the gig feed at this time.", "error")
        
    return render_template('auth/feed.html', username=current_user.username, result=gigs)

@bp.route('/create_gig', methods=['GET'])
@login_required
def create_gig_form():
    return render_template('auth/create_gig.html')

@bp.route('/create_gig', methods=['POST'])
@login_required
def create_gig():
    offer_status = request.form.get('offer_status')
    title = request.form.get('title')
    description = request.form.get('description')
    compensation = request.form.get('compensation')
    category = request.form.get('category')
    user_id = current_user.id
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    venmo = current_user.venmo

    budget = None
    compensation_type = None

    if compensation == 'yes':
        budget_str = request.form.get('budget')
        compensation_type = request.form.get('compensation_type')

        if not budget_str or not compensation_type:
             flash('Budget and compensation rate are required if compensation is selected.', 'error')
             return render_template('auth/create_gig.html', **request.form)

        try:
            budget = float(budget_str)
            if budget < 1:
                flash('Budget must be at least $1.00.', 'error')
                return render_template('auth/create_gig.html', **request.form)
        except ValueError:
            flash('Invalid budget amount entered.', 'error')
            return render_template('auth/create_gig.html', **request.form)
    
    connection = None
    try:
        connection = sqlite3.connect(GIGS_DB_PATH)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO gigs (offer_status, title, description, compensation, budget, category, user_id, date, compensation_type, venmo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (offer_status, title, description, compensation, budget, category, user_id, date, compensation_type, venmo))

        connection.commit()
        flash('Gig created successfully!', 'success')
        return redirect(url_for('main.feed')) 
        
    except Exception as e:
        print(f"Error creating gig: {e}")
        flash('An error occurred while creating the gig. Please try again.', 'error')
        if connection:
             connection.rollback()
        return render_template('auth/create_gig.html', **request.form)
    finally:
         if connection:
             connection.close()

@bp.route('/users')
@login_required
def list_users():
    users_list = User.get_all_users()
    return render_template('auth/users.html', users=users_list)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        name = request.form.get('name')
        dorm = request.form.get('dorm')
        venmo = request.form.get('venmo')
        conn = sqlite3.connect(GIGS_DB_PATH)
        c = conn.cursor()
            
        c.execute("UPDATE gigs SET venmo=? WHERE user_id=?", (venmo, current_user.id))
        conn.commit()
        conn.close()
        
        class_name = request.form.get('class_name')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        password_error = None
        if new_password:
            if not current_password:
                 password_error = 'Current password is required to set a new password.'
            elif not User.check_password(current_user.id, current_password):
                password_error = 'Incorrect current password.'
            elif new_password != confirm_password:
                password_error = 'New passwords do not match.'
            elif len(new_password) < 8:
                 password_error = 'New password must be at least 8 characters long'
            elif not re.search(r'[A-Z]', new_password):
                 password_error = 'New password must contain at least one uppercase letter'
            elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
                 password_error = 'New password must contain at least one special character'
        
        if password_error:
             flash(password_error, 'error') 
             user_data = User.get(current_user.id) 
             return render_template('auth/edit_profile.html', user=user_data)

        graduation_year = None 
        if class_name: 
            current_cal_year = datetime.date.today().year
            if class_name == "Senior": graduation_year = current_cal_year + 1
            elif class_name == "Junior": graduation_year = current_cal_year + 2
            elif class_name == "Sophomore": graduation_year = current_cal_year + 3
            elif class_name == "Freshman": graduation_year = current_cal_year + 4
        
        password_to_update = new_password if not password_error and new_password else None 

        if User.update_profile(current_user.id, name=name, dorm=dorm, venmo=venmo, class_year=graduation_year, new_password=password_to_update):
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.account'))
        else:
            flash('An error occurred while updating your profile.', 'error')
            user_data = User.get(current_user.id)
            return render_template('auth/edit_profile.html', user=user_data)

    else:
        user_data = User.get(current_user.id) 
        if not user_data:
            flash('Could not load user data.', 'error')
            return redirect(url_for('main.account'))
        return render_template('auth/edit_profile.html', user=user_data)

@bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user_id_to_delete = current_user.id

    gigs_conn = None
    users_conn = None
    try:
        gigs_conn = sqlite3.connect(GIGS_DB_PATH)
        gigs_cursor = gigs_conn.cursor()
        gigs_cursor.execute("DELETE FROM gigs WHERE user_id = ?", (user_id_to_delete,))
        gigs_conn.commit()
        print(f"Deleted gigs for user {user_id_to_delete}")

        users_conn = get_db()
        users_cursor = users_conn.cursor()
        users_cursor.execute("DELETE FROM users WHERE username = ?", (user_id_to_delete,))
        users_conn.commit()
        print(f"Deleted user {user_id_to_delete}")

        logout_user()
        flash('Your account and associated data have been permanently deleted.', 'success')
        return redirect(url_for('main.index'))

    except Exception as e:
        print(f"Error deleting account for {user_id_to_delete}: {e}")
        if gigs_conn: gigs_conn.rollback()
        if users_conn: users_conn.rollback()
        flash('An error occurred while deleting your account. Please contact support.', 'error')
        return redirect(url_for('main.account'))
    finally:
        if gigs_conn: gigs_conn.close()
        if users_conn: users_conn.close()


@bp.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    try:
        print("got to the root")
        conn = sqlite3.connect(COMMENTS_DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM comments WHERE id = ?", (comment_id,))

        conn.commit()
        c.close()

        return jsonify({"success": True, "message": "Comment deleted successfully"})
    except Exception as e:
        print(f"Error deleting gig {comment_id}: {e}")
        if conn and conn.in_transaction:
            conn.rollback()
        if conn:
            conn.close()
        return jsonify({"success": False, "message": "An error occurred while deleting the comment"}), 500
    
     
@bp.route('/delete_gig/<int:gig_id>', methods=['POST'])
@login_required
def delete_gig(gig_id):
    try:
        conn = sqlite3.connect(GIGS_DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT user_id FROM gigs WHERE id = ?", (gig_id,))
        gig = c.fetchone()
        
        if not gig:
            conn.close()
            return jsonify({"success": False, "message": "Gig not found"}), 404
        
        if hasattr(gig, 'keys'):
            gig_user_id = gig['user_id']
        else:
            gig_user_id = gig[0]
            
        if gig_user_id != current_user.id:
            conn.close()
            return jsonify({"success": False, "message": "You don't have permission to delete this gig"}), 403
        
        c.execute("DELETE FROM gigs WHERE id = ?", (gig_id,))
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": "Gig deleted successfully"})
        
    except Exception as e:
        print(f"Error deleting gig {gig_id}: {e}")
        if conn and conn.in_transaction:
            conn.rollback()
        if conn:
            conn.close()
        return jsonify({"success": False, "message": "An error occurred while deleting the gig"}), 500
    

@bp.route('/gig/<int:gigId>')
@login_required
def gig(gigId):
    gigs_conn = sqlite3.connect(GIGS_DB_PATH)
    gigs_conn.row_factory = sqlite3.Row
    gigs_cursor = gigs_conn.cursor()
    sql = f"SELECT * FROM gigs WHERE id = '{gigId}'"
    gigs_cursor.execute(sql)
    gig = gigs_cursor.fetchone()
    

    if not gig:
        flash("Gig not found.", "error")
        return redirect(url_for('main.feed'))
    
    gigs_conn.close()

    comments_conn = sqlite3.connect(COMMENTS_DB_PATH)
    comments_conn.row_factory = sqlite3.Row
    comments_cursor = comments_conn.cursor()
    sql = f"SELECT * FROM comments WHERE gigId == '{gigId}'"
    comments_cursor.execute(sql)
    comments = comments_cursor.fetchall()
    if not comments:
        comments = []
    comments.reverse()
    comments_conn.close()
    print(comments)
    
    return render_template('auth/gig.html', gig=dict(gig), comments = comments, user=current_user)

@bp.route('/gig/<int:gigId>/comment', methods = ["POST"])
@login_required
def add_comment(gigId):
    commentText = request.form.get("comment_text")
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        conn = sqlite3.connect(COMMENTS_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO comments (gigId, text, username, date) VALUES (?, ?, ?, ?)",
                       (gigId, commentText, current_user.id, date))

        
        conn.commit()
        conn.close()

        flash("Comment added successfully!", "success")
    except Exception as e:
        print(f"Error adding comment: {e}")
        flash("Could not add comment.", "error")

    return redirect(url_for('main.gig', gigId=gigId))
@login_required
@bp.route('/edit_gig/<int:gig_id>', methods=['GET', 'POST'])
@login_required
def edit_gig(gig_id):
    if request.method == 'GET':
        try:
            conn = sqlite3.connect(GIGS_DB_PATH)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            c.execute("SELECT * FROM gigs WHERE id = ?", (gig_id,))
            gig = c.fetchone()
            conn.close()
            
            if not gig:
                flash("Gig not found.", "error")
                return redirect(url_for('main.account'))
            
            if gig['user_id'] != current_user.id:
                flash("You don't have permission to edit this gig.", "error")
                return redirect(url_for('main.account'))
            
            return render_template('auth/edit_gig.html', gig=gig)
            
        except Exception as e:
            print(f"Error fetching gig {gig_id} for editing: {e}")
            flash("An error occurred while trying to edit the gig.", "error")
            return redirect(url_for('main.account'))
    
    else:  # request.method == 'POST'
        try:
            offer_status = request.form.get('offer_status')
            title = request.form.get('title')
            description = request.form.get('description')
            compensation = request.form.get('compensation')
            category = request.form.get('category')
            budget = None
            compensation_type = None

            if compensation == 'yes':
                budget_str = request.form.get('budget')
                compensation_type = request.form.get('compensation_type')

                if not budget_str or not compensation_type:
                    flash('Budget and compensation rate are required if compensation is selected.', 'error')
                    return redirect(url_for('main.edit_gig', gig_id=gig_id))

                try:
                    budget = float(budget_str)
                    if budget < 1:
                        flash('Budget must be at least $1.00.', 'error')
                        return redirect(url_for('main.edit_gig', gig_id=gig_id))
                except ValueError:
                    flash('Invalid budget amount entered.', 'error')
                    return redirect(url_for('main.edit_gig', gig_id=gig_id))

            conn = sqlite3.connect(GIGS_DB_PATH)
            c = conn.cursor()
            
            c.execute("SELECT user_id FROM gigs WHERE id = ?", (gig_id,))
            gig = c.fetchone()
            
            if not gig:
                conn.close()
                flash("Gig not found.", "error")
                return redirect(url_for('main.account'))
            
            if gig[0] != current_user.id:
                conn.close()
                flash("You don't have permission to edit this gig.", "error")
                return redirect(url_for('main.account'))
            
            c.execute("""
                UPDATE gigs SET 
                    offer_status = ?, 
                    title = ?, 
                    description = ?, 
                    compensation = ?, 
                    budget = ?, 
                    category = ?,
                    compensation_type = ?
                WHERE id = ?
            """, (offer_status, title, description, compensation, budget, category, compensation_type, gig_id))
            
            conn.commit()
            conn.close()
            
            flash("Gig updated successfully!", "success")
            return redirect(url_for('main.account'))
            
        except Exception as e:
            print(f"Error updating gig {gig_id}: {e}")
            if conn and conn.in_transaction:
                conn.rollback()
            if conn:
                conn.close()
            flash("An error occurred while updating the gig.", "error")
            return redirect(url_for('main.edit_gig', gig_id=gig_id))

>>>>>>> 6ac44c6 (SwatWorks final update)
