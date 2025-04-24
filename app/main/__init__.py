from flask import Blueprint

<<<<<<< HEAD
bp = Blueprint('main', __name__)
=======
bp = Blueprint('main', __name__, static_folder='static')
>>>>>>> 6ac44c6 (SwatWorks final update)

from app.main import routes 