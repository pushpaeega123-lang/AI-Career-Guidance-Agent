from flask import Blueprint

skill_gap_bp = Blueprint('skill_gap', __name__, url_prefix='/api/skill-gap')

from . import routes
