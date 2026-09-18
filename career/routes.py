from flask import jsonify
from . import career_bp

@career_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Career Guidance module."""
    return jsonify({
        "status": "healthy",
        "module": "career_pathway_guidance"
    }), 200
