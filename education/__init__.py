from flask import Blueprint

education_bp = Blueprint('education', __name__, url_prefix='/api/education')

from . import routes
