from flask import Flask
from flask_login import LoginManager
import logging
from config import Config
from .models import init_users_db, init_gigs_db, init_comments_db

login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Set up basic console logging
    app.logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s'
    ))
    app.logger.addHandler(console_handler)

    # Initialize login manager
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.get(user_id)

    # Initialize databases
    with app.app_context():
        app.logger.info('Initializing databases...')
        init_users_db()
        init_gigs_db()
        init_comments_db()
        app.logger.info('Databases initialized.')


    # Register only main blueprint
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    app.logger.info('SwatWorks is ready!')

    return app 