from flask import Flask
from flask_login import LoginManager
import logging
from config import Config

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
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
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

    app.logger.info('SwatWorks is ready!')

    return app 