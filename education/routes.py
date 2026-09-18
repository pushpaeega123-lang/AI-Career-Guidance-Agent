"""
Education Pathway Guidance Blueprint Routes (Member 2 - Steps 6 & 7).
Exposes REST endpoints for the Education Pathway Catalogue and Profile-Connected
Education Pathway Guidance Engine, as well as the student-facing Education Dashboard UI.
"""

from flask import jsonify, request, render_template
from . import education_bp
from .services import EducationService
from .catalogue import EDUCATION_PATHWAY_CATALOGUE, PATHWAY_BY_ID, PATHWAYS_BY_LEVEL
from profile.services import ProfileService
from career.catalogue import CAREER_CATALOGUE, CATALOGUE_BY_ID


@education_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Education Guidance module."""
    return jsonify({
        "status": "healthy",
        "module": "education_pathway_guidance"
    }), 200


@education_bp.route('/catalogue', methods=['GET'])
def get_catalogue():
    """
    Retrieves the internal Education Pathway Catalogue.
    Optional query params:
      - ?education_level=<level> (e.g. Undergraduate, Diploma, Higher Secondary)
      - ?domain=<domain> (e.g. Technology & Software, Data & AI)
    """
    education_level = request.args.get('education_level')
    domain = request.args.get('domain')
    pathways = EducationService.get_education_catalogue(
        education_level=education_level,
        domain=domain
    )

    return jsonify({
        "success": True,
        "total": len(pathways),
        "filter_education_level": education_level,
        "filter_domain": domain,
        "available_levels": list(PATHWAYS_BY_LEVEL.keys()),
        "pathways": pathways
    }), 200


@education_bp.route('/catalogue/<pathway_id>', methods=['GET'])
def get_pathway_detail(pathway_id):
    """
    Retrieves a single education pathway definition by unique ID.
    """
    pathway = EducationService.get_pathway_by_id(pathway_id)
    if not pathway:
        return jsonify({
            "success": False,
            "error": f"Education pathway with ID '{pathway_id}' not found."
        }), 404

    return jsonify({
        "success": True,
        "pathway": pathway
    }), 200


@education_bp.route('/pathways/<int:profile_id>', methods=['GET'])
def get_education_pathways(profile_id):
    """
    Generates explainable education pathway guidance for a student profile ID.
    Optional query param:
      - ?career_id=<career_id> to tailor educational progression toward a target career.
    """
    career_id = request.args.get('career_id')
    guidance, error = EducationService.get_pathways_for_profile(
        profile_id=profile_id,
        career_id=career_id
    )

    if error:
        return jsonify({
            "success": False,
            "error": error
        }), 404

    return jsonify(guidance), 200


# ==============================================================================
# Student Education Pathway Dashboard UI Route (Member 2 - Step 7)
# ==============================================================================

@education_bp.route('/ui', methods=['GET'])
@education_bp.route('/ui/<int:profile_id>', methods=['GET'])
def education_pathways_dashboard(profile_id=None):
    """
    Renders the student-facing Education Pathway Dashboard.
    Supports ?career_id=<career_id> to display target-career-tailored educational pathways.
    If profile_id is not specified, selects the first available profile or renders
    a clean empty state when no profiles exist.
    """
    profiles = ProfileService.list_profiles(limit=50)
    career_id = request.args.get('career_id')

    # Check query param if profile_id not in URL path
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
                'education_pathways.html',
                active_profile=None,
                guidance=None,
                profiles=profiles,
                career_catalogue=CAREER_CATALOGUE,
                catalogue=EducationService.get_education_catalogue(),
                catalogue_levels=list(PATHWAYS_BY_LEVEL.keys()),
                error=f"Student profile with ID {profile_id} was not found."
            ), 404

        guidance_data, err = EducationService.get_pathways_for_profile(
            profile_id=profile_id,
            career_id=career_id
        )
        if err:
            error_msg = err
            # If career_id was invalid, return 404
            return render_template(
                'education_pathways.html',
                active_profile=active_profile,
                guidance=None,
                profiles=profiles,
                career_catalogue=CAREER_CATALOGUE,
                catalogue=EducationService.get_education_catalogue(),
                catalogue_levels=list(PATHWAYS_BY_LEVEL.keys()),
                error=error_msg
            ), 404
        else:
            guidance = guidance_data
    elif profiles:
        # Default to first available profile
        active_profile = profiles[0]
        guidance_data, err = EducationService.get_pathways_for_profile(
            profile_id=active_profile.id,
            career_id=career_id
        )
        if err:
            error_msg = err
        else:
            guidance = guidance_data

    return render_template(
        'education_pathways.html',
        active_profile=active_profile,
        guidance=guidance,
        profiles=profiles,
        career_catalogue=CAREER_CATALOGUE,
        catalogue=EducationService.get_education_catalogue(),
        catalogue_levels=list(PATHWAYS_BY_LEVEL.keys()),
        error=error_msg
    ), 200
