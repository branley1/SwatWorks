from flask import Flask
from flask_login import LoginManager
import logging
from config import Config
<<<<<<< HEAD
=======
from .models import init_users_db, init_gigs_db, init_comments_db
>>>>>>> 6ac44c6 (SwatWorks final update)

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
<<<<<<< HEAD
    login_manager.login_view = 'auth.login'
=======
    login_manager.login_view = 'main.login'
>>>>>>> 6ac44c6 (SwatWorks final update)
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
<<<<<<< HEAD
        from app.auth.models import User
        return User.get(user_id)

    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.gigs import bp as gigs_bp
    app.register_blueprint(gigs_bp)

    from app.messages import bp as messages_bp
    app.register_blueprint(messages_bp)

=======
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

>>>>>>> 6ac44c6 (SwatWorks final update)
    app.logger.info('SwatWorks is ready!')

    return app 