from flask import jsonify
from . import eligibility_bp

@eligibility_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Eligibility Engine module."""
    return jsonify({
        "status": "healthy",
        "module": "eligibility_checker"
    }), 200
