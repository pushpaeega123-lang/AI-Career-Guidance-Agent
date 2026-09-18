from flask import jsonify
from . import notifications_bp

@notifications_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Personalized Notifications module."""
    return jsonify({
        "status": "healthy",
        "module": "personalized_notifications"
    }), 200
