from flask import jsonify
from . import planner_bp

@planner_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Personalized Career Action Planner module."""
    return jsonify({
        "status": "healthy",
        "module": "personalized_action_planner"
    }), 200
