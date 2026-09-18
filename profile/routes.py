from flask import jsonify, render_template, request
from . import profile_bp
from .services import CareerDiscoveryService, ProfileService

@profile_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Student Profile & Interest Intelligence module."""
    return jsonify({
        "status": "healthy",
        "module": "profile_and_interest_intelligence"
    }), 200


@profile_bp.route('/discovery', methods=['GET'])
def get_career_discovery():
    """
    Retrieve current exploration profile or render the Career Discovery questionnaire.
    """
    if request.is_json or request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
        profile_state = CareerDiscoveryService.get_exploration_profile()
        return jsonify(profile_state), 200

    return render_template('career_discovery.html')


@profile_bp.route('/discovery', methods=['POST'])
def submit_career_discovery():
    """
    Validate and save submitted student exploration questionnaire profile.
    """
    data = None
    if request.is_json:
        data = request.get_json(silent=True)
    elif request.form:
        # Parse form data (supporting multi-value inputs like checkboxes)
        data = {}
        for key in request.form:
            values = request.form.getlist(key)
            if len(values) > 1 or key.endswith('[]') or key in ('subjects', 'skills', 'interests', 'work_preferences', 'career_preferences'):
                clean_key = key[:-2] if key.endswith('[]') else key
                data[clean_key] = values
            else:
                data[key] = values[0] if values else None

    if data is None:
        return jsonify({
            "error": "Invalid request. Request body must be a valid JSON object or form data."
        }), 400

    student_id = data.get("student_id")
    try:
        student_id_int = int(student_id) if student_id is not None else None
    except (ValueError, TypeError):
        student_id_int = None

    try:
        result = CareerDiscoveryService.save_exploration_profile(
            data=data,
            student_id=student_id_int
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Failed to save exploration profile: {str(e)}"
        }), 500


@profile_bp.route('/discovery', methods=['DELETE'])
def clear_career_discovery():
    """
    Reset stored career exploration profile state.
    """
    result = CareerDiscoveryService.clear_exploration_profile()
    return jsonify(result), 200

