from flask import jsonify, render_template, request
from . import eligibility_bp
from .services import EligibilityService


@eligibility_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Eligibility Engine module."""
    return jsonify({
        "status": "healthy",
        "module": "eligibility_checker"
    }), 200


@eligibility_bp.route('/demo', methods=['GET'])
def eligibility_demo_view():
    """Interactive demo interface for testing the Eligibility Engine."""
    return render_template('eligibility.html')


@eligibility_bp.route('/check', methods=['POST'])
def check_eligibility():
    """
    Evaluate eligibility of a student profile against target opportunity criteria.

    Expected JSON body payload:
    {
        "student_profile": { ... },
        "opportunity": { ... }
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

    # Extract student and opportunity objects with support for common key aliases
    student_data = (
        data.get("student_profile")
        or data.get("student")
        or data.get("student_profile_data")
        or data.get("profile")
        or {}
    )

    opportunity_data = (
        data.get("opportunity")
        or data.get("target_opportunity")
        or data.get("target_opportunity_data")
        or data.get("requirements")
        or data.get("pathway")
        or {}
    )

    # Evaluate eligibility using deterministic engine
    result = EligibilityService.check_eligibility(
        student_profile_data=student_data,
        target_opportunity_data=opportunity_data
    )

    return jsonify(result), 200
