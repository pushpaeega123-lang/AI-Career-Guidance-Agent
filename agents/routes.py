from flask import jsonify, render_template, request
from . import agents_bp
from .orchestrator import AgentOrchestrator

# Global orchestrator instance
orchestrator = AgentOrchestrator()


@agents_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Agent Orchestrator module."""
    return jsonify({
        "status": "healthy",
        "module": "agent_orchestrator"
    }), 200


@agents_bp.route('/demo', methods=['GET'])
@agents_bp.route('/assistant', methods=['GET'])
def assistant_demo_view():
    """Interactive multi-agent guidance console."""
    return render_template('assistant.html')


@agents_bp.route('/orchestrate', methods=['POST'])
@agents_bp.route('/execute', methods=['POST'])
@agents_bp.route('/chat', methods=['POST'])
def orchestrate_request():
    """
    Orchestrate user query or structured task across specialized domain agents.

    Expected JSON body payload:
    {
        "query": "How do I become a Cloud Engineer?",
        "context": {
            "student_id": 1,
            "target_role": "Cloud Engineer",
            "current_skills": ["Python", "Linux"]
        },
        "intent": "comprehensive_guidance"  # Optional override
    }
    """
    if not request.is_json and request.content_type != 'application/json':
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({
                "error": "Invalid request. Request body must be a valid JSON object."
            }), 400
    else:
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({
                "error": "Invalid JSON format or empty request body."
            }), 400

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON dictionary."
        }), 400

    user_query = data.get("query") or data.get("user_query") or data.get("message") or ""
    context = data.get("context") or {}

    if not isinstance(context, dict):
        context = {}

    # Allow top-level keys to supplement context if omitted
    for k in ("student_id", "target_role", "current_skills", "target_skills", "intent", "student_profile", "opportunity"):
        if k in data and k not in context:
            context[k] = data[k]

    response = orchestrator.route_request(user_query=user_query, context=context)
    return jsonify(response), 200
