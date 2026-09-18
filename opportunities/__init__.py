from flask import Blueprint

opportunities_bp = Blueprint('opportunities', __name__, url_prefix='/api/opportunities')

from . import routes
