from flask import jsonify
from . import skill_gap_bp

@skill_gap_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Skill Gap Analysis module."""
    return jsonify({
        "status": "healthy",
        "module": "skill_gap_analyzer"
    }), 200
