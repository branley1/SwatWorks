from flask import render_template, redirect, url_for
from flask_login import current_user
from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    # Render the index template
    return render_template('main/index.html') 