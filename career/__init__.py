from flask import Blueprint

career_bp = Blueprint('career', __name__, url_prefix='/api/career')

from . import routes
