from flask import jsonify, request
from . import profile_bp

@profile_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Student Profile & Interest Intelligence module."""
    return jsonify({
        "status": "healthy",
        "module": "profile_and_interest_intelligence"
    }), 200
