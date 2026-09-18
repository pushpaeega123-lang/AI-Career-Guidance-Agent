from flask import Blueprint

planner_bp = Blueprint('planner', __name__, url_prefix='/api/planner')

from . import routes
