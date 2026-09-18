from flask import jsonify, request, render_template, redirect, url_for
from . import profile_bp
from .services import ProfileService

@profile_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Student Profile & Interest Intelligence module."""
    return jsonify({
        "status": "healthy",
        "module": "profile_and_interest_intelligence"
    }), 200

@profile_bp.route('', methods=['POST'])
@profile_bp.route('/', methods=['POST'])
@profile_bp.route('/create', methods=['POST'])
def create_profile():
    """Create a new student profile."""
    data = request.get_json(silent=True)
    if not data and request.form:
        data = request.form.to_dict()

    if not data:
        return jsonify({
            "status": "error",
            "message": "Invalid request: JSON body or form data required"
        }), 400

    profile, error = ProfileService.create_profile(data)
    if error:
        return jsonify({
            "status": "error",
            "message": error
        }), 400

    return jsonify({
        "status": "success",
        "message": "Student profile created successfully",
        "profile": profile.to_dict()
    }), 201

@profile_bp.route('/<int:profile_id>', methods=['GET'])
def get_profile(profile_id):
    """Retrieve a student profile by ID."""
    profile = ProfileService.get_profile_by_id(profile_id)
    if not profile:
        return jsonify({
            "status": "error",
            "message": f"Profile with ID {profile_id} not found"
        }), 404

    return jsonify({
        "status": "success",
        "profile": profile.to_dict()
    }), 200

@profile_bp.route('/<int:profile_id>', methods=['PUT', 'PATCH'])
@profile_bp.route('/<int:profile_id>/update', methods=['POST', 'PUT'])
def update_profile(profile_id):
    """Update an existing student profile."""
    data = request.get_json(silent=True)
    if not data and request.form:
        data = request.form.to_dict()

    if not data:
        return jsonify({
            "status": "error",
            "message": "Invalid request: JSON body or form data required"
        }), 400

    profile, error = ProfileService.update_profile(profile_id, data)
    if error:
        status_code = 404 if "not found" in error.lower() else 400
        return jsonify({
            "status": "error",
            "message": error
        }), status_code

    return jsonify({
        "status": "success",
        "message": "Student profile updated successfully",
        "profile": profile.to_dict()
    }), 200

@profile_bp.route('/by-email', methods=['GET'])
def get_profile_by_email():
    """Retrieve a profile by email query parameter."""
    email = request.args.get('email')
    if not email:
        return jsonify({
            "status": "error",
            "message": "Missing 'email' query parameter"
        }), 400

    profile = ProfileService.get_profile_by_email(email)
    if not profile:
        return jsonify({
            "status": "error",
            "message": f"No profile found for email '{email}'"
        }), 404

    return jsonify({
        "status": "success",
        "profile": profile.to_dict()
    }), 200

@profile_bp.route('/all', methods=['GET'])
def list_profiles():
    """List student profiles with optional limit and offset."""
    try:
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = max(int(request.args.get('offset', 0)), 0)
    except ValueError:
        limit, offset = 50, 0

    profiles = ProfileService.list_profiles(limit=limit, offset=offset)
    return jsonify({
        "status": "success",
        "count": len(profiles),
        "profiles": [p.to_dict() for p in profiles]
    }), 200

@profile_bp.route('/<int:profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    """Delete a student profile."""
    success, error = ProfileService.delete_profile(profile_id)
    if not success:
        return jsonify({
            "status": "error",
            "message": error
        }), 404

    return jsonify({
        "status": "success",
        "message": f"Profile {profile_id} deleted successfully"
    }), 200

# --- Minimum Template UI Support Routes ---

@profile_bp.route('/ui', methods=['GET'])
@profile_bp.route('/ui/<int:profile_id>', methods=['GET'])
def profile_ui(profile_id=None):
    """Render the student profile management interface."""
    # Check query parameter if profile_id not in URL path
    if profile_id is None and request.args.get('profile_id'):
        try:
            profile_id = int(request.args.get('profile_id'))
        except (ValueError, TypeError):
            profile_id = None

    profile = None
    if profile_id:
        profile = ProfileService.get_profile_by_id(profile_id)
    profiles = ProfileService.list_profiles(limit=50)
    return render_template('profile.html', active_profile=profile, profiles=profiles)

# --- Interest Intelligence Endpoints ---

@profile_bp.route('/interests/analyze', methods=['POST'])
def analyze_interests():
    """
    Interest Intelligence Engine endpoint.
    Normalizes student interests, maps them to career domains, and provides factual explainability rationales.
    Accepts JSON payload:
      - {"interests": ["python", "machine learning"]} OR
      - {"interests": "python, machine learning"} OR
      - {"profile_id": 1}
    """
    data = request.get_json(silent=True)
    if data is None and request.form:
        data = request.form.to_dict()

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Invalid request: JSON object required"
        }), 400

    profile_id = data.get('profile_id')
    raw_interests = data.get('interests')

    if profile_id is None and raw_interests is None:
        return jsonify({
            "status": "error",
            "message": "Either 'interests' or 'profile_id' must be provided in the request payload"
        }), 400

    analysis, error = ProfileService.analyze_student_interests(
        profile_id=profile_id,
        interests=raw_interests
    )

    if error:
        status_code = 404 if "not found" in error.lower() else 400
        return jsonify({
            "status": "error",
            "message": error
        }), status_code

    return jsonify(analysis), 200

@profile_bp.route('/interests/domains', methods=['GET'])
def get_career_domains():
    """Returns the standardized career domains catalogue."""
    from .interest_intelligence import InterestIntelligenceService
    return jsonify({
        "status": "success",
        "domains": InterestIntelligenceService.get_career_domains()
    }), 200


