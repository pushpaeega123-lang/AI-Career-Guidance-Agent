from flask import jsonify
from . import opportunities_bp

@opportunities_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Opportunities (Jobs, Govt Jobs, Exams, Internships, Scholarships) module."""
    return jsonify({
        "status": "healthy",
        "module": "opportunities_navigator"
    }), 200
