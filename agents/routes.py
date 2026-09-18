from flask import jsonify
from . import agents_bp

@agents_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Agent Orchestrator module."""
    return jsonify({
        "status": "healthy",
        "module": "agent_orchestrator"
    }), 200
