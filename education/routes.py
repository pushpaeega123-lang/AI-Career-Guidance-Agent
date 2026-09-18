from flask import jsonify
from . import education_bp

@education_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Education Guidance module."""
    return jsonify({
        "status": "healthy",
        "module": "education_pathway_guidance"
    }), 200
