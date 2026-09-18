from flask import Blueprint

eligibility_bp = Blueprint('eligibility', __name__, url_prefix='/api/eligibility')

from . import routes
