"""
Career Pathway Guidance Blueprint Routes (Member 2).
Exposes REST endpoints for the Career Catalogue and Career Pathway Guidance Engine,
as well as the server-rendered Student Career Guidance Dashboard.
"""

from flask import jsonify, request, render_template
from . import career_bp
from .services import CareerService
from .catalogue import CAREER_CATALOGUE, CATALOGUE_BY_DOMAIN
from profile.services import ProfileService


@career_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Career Guidance module."""
    return jsonify({
        "status": "healthy",
        "module": "career_pathway_guidance"
    }), 200


@career_bp.route('/catalogue', methods=['GET'])
def get_catalogue():
    """
    Retrieves the internal career catalogue.
    Optional query param: ?domain=<domain_name>
    """
    domain = request.args.get('domain')
    careers = CareerService.get_career_catalogue(domain=domain)
    
    return jsonify({
        "success": True,
        "total": len(careers),
        "filter_domain": domain,
        "available_domains": list(CATALOGUE_BY_DOMAIN.keys()),
        "careers": careers
    }), 200


@career_bp.route('/catalogue/<career_id>', methods=['GET'])
def get_career_detail(career_id):
    """
    Retrieves a single career pathway definition by ID.
    """
    career = CareerService.get_career_by_id(career_id)
    if not career:
        return jsonify({
            "success": False,
            "error": f"Career pathway with ID '{career_id}' not found."
        }), 404

    return jsonify({
        "success": True,
        "career": career
    }), 200


@career_bp.route('/guidance/<int:profile_id>', methods=['GET'])
def get_career_guidance(profile_id):
    """
    Generates transparent, explainable career guidance for a student profile ID.
    Evaluates profile interests, skills, education, and career goals against
    the Career Catalogue and Interest Intelligence engine.
    """
    guidance, error = CareerService.generate_guidance_for_profile(profile_id)
    if error:
        return jsonify({
            "success": False,
            "error": error
        }), 404

    return jsonify(guidance), 200


# ==============================================================================
# Student Dashboard UI Route (Member 2 - Step 5)
# ==============================================================================

@career_bp.route('/ui', methods=['GET'])
@career_bp.route('/ui/<int:profile_id>', methods=['GET'])
def career_guidance_dashboard(profile_id=None):
    """
    Renders the student-facing Career Guidance Dashboard.
    If profile_id is not provided, checks query param ?profile_id or defaults to first profile.
    If no profiles exist, displays an instructional empty state.
    """
    profiles = ProfileService.list_profiles(limit=50)

    # Check query parameter if profile_id was not in path
    if profile_id is None and request.args.get('profile_id'):
        try:
            profile_id = int(request.args.get('profile_id'))
        except (ValueError, TypeError):
            profile_id = None

    active_profile = None
    guidance = None
    error_msg = None

    if profile_id is not None:
        active_profile = ProfileService.get_profile_by_id(profile_id)
        if not active_profile:
            return render_template(
                'career_guidance.html',
                active_profile=None,
                guidance=None,
                profiles=profiles,
                catalogue=CareerService.get_career_catalogue(),
                catalogue_domains=list(CATALOGUE_BY_DOMAIN.keys()),
                error=f"Student profile with ID {profile_id} was not found."
            ), 404

        guidance_data, err = CareerService.generate_guidance_for_profile(profile_id)
        if err:
            error_msg = err
        else:
            guidance = guidance_data
    elif profiles:
        # Default to the first available student profile
        active_profile = profiles[0]
        guidance_data, err = CareerService.generate_guidance_for_profile(active_profile.id)
        if err:
            error_msg = err
        else:
            guidance = guidance_data

    target_career = guidance.get("target_career") if guidance else None
    skill_matched_careers = guidance.get("skill_matched_careers", []) if guidance else []

    return render_template(
        'career_guidance.html',
        active_profile=active_profile,
        guidance=guidance,
        target_career=target_career,
        skill_matched_careers=skill_matched_careers,
        profiles=profiles,
        catalogue=CareerService.get_career_catalogue(),
        catalogue_domains=list(CATALOGUE_BY_DOMAIN.keys()),
        error=error_msg
    ), 200
