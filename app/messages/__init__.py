from flask import Blueprint

bp = Blueprint('messages', __name__, url_prefix='/messages')

from app.messages import routes
