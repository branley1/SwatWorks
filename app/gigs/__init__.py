from flask import Blueprint

bp = Blueprint('gigs', __name__, url_prefix='/gigs')

from app.gigs import routes
