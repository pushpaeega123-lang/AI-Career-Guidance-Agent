from flask import jsonify, render_template, request, session
from planner.roadmap import RoadmapService
from planner.services import PlannerService
from . import career_bp
from .services import CareerDirectionService, PathwayAnalysisService, PathwayDiscoveryService


@career_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Career Guidance module."""
    return jsonify({
        "status": "healthy",
        "module": "career_pathway_guidance"
    }), 200


@career_bp.route('/direction', methods=['GET'])
def get_career_direction():
    """
    Retrieve current career direction workflow state or render UI selection page.
    """
    if request.is_json or request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
        state = CareerDirectionService.get_direction()
        return jsonify(state), 200

    return render_template('career_direction.html')


@career_bp.route('/direction', methods=['POST'])
def set_career_direction():
    """
    Store student career direction decision ('known' with target_role or 'exploring').
    """
    data = None
    if request.is_json:
        data = request.get_json(silent=True)
    elif request.form:
        data = request.form.to_dict()

    if data is None:
        return jsonify({
            "error": "Invalid request. Request body must be a valid JSON object or form data."
        }), 400

    direction = data.get("career_direction") or data.get("direction")
    target_role = data.get("target_role") or data.get("role")

    try:
        result = CareerDirectionService.set_direction(
            direction=direction,
            target_role=target_role
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Failed to save career direction: {str(e)}"
        }), 500


@career_bp.route('/direction', methods=['DELETE'])
def clear_career_direction():
    """
    Reset stored career direction workflow state.
    """
    result = CareerDirectionService.clear_direction()
    return jsonify(result), 200


# =============================================================================
# Pathway Discovery & Selection Endpoints
# =============================================================================

@career_bp.route('/pathways', methods=['GET'])
def get_pathways():
    """
    Execute pathway discovery based on active session state or render Pathway Discovery UI.
    """
    if request.is_json or request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
        result = PathwayDiscoveryService.discover_pathways()
        return jsonify(result), 200

    return render_template('pathways.html')


@career_bp.route('/pathways/discover', methods=['POST'])
def discover_pathways_api():
    """
    Execute pathway discovery for explicitly provided payload.
    """
    data = request.get_json(silent=True) or {}
    try:
        result = PathwayDiscoveryService.discover_pathways(context=data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "error": f"Pathway discovery failed: {str(e)}"
        }), 500


@career_bp.route('/pathways/select', methods=['POST'])
def select_pathway():
    """
    Select and persist a pathway for downstream Eligibility evaluation.
    """
    data = None
    if request.is_json:
        data = request.get_json(silent=True)
    elif request.form:
        data = request.form.to_dict()

    if not data:
        return jsonify({
            "error": "Invalid request. Provide pathway_id in JSON payload or form data."
        }), 400

    pathway_id = data.get("pathway_id") or data.get("id")
    pathway_name = data.get("pathway_name") or data.get("name")

    try:
        result = PathwayDiscoveryService.select_pathway(
            pathway_id=pathway_id,
            pathway_name=pathway_name
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to select pathway: {str(e)}"}), 500


@career_bp.route('/pathways/selected', methods=['GET'])
def get_selected_pathway():
    """
    Retrieve current selected pathway from session.
    """
    result = PathwayDiscoveryService.get_selected_pathway()
    return jsonify(result), 200


@career_bp.route('/pathways/selected', methods=['DELETE'])
def clear_selected_pathway():
    """
    Reset selected pathway in session.
    """
    result = PathwayDiscoveryService.clear_selected_pathway()
    return jsonify(result), 200


@career_bp.route('/pathways/shortlist', methods=['POST'])
def toggle_shortlist():
    """
    Toggle pathway ID in student shortlist set.
    """
    data = request.get_json(silent=True) or {}
    pathway_id = data.get("pathway_id") or data.get("id")

    try:
        result = PathwayDiscoveryService.toggle_shortlist(pathway_id=pathway_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to toggle shortlist: {str(e)}"}), 500


@career_bp.route('/pathways/analysis', methods=['GET'])
def pathway_analysis_view():
    """
    Retrieve current combined Eligibility and Skill Gap fit analysis for selected pathway,
    or render the Pathway Fit Analysis UI.
    """
    if request.is_json or request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
        result = PathwayAnalysisService.analyze_pathway_fit()
        return jsonify(result), 200

    return render_template('pathway_analysis.html')


@career_bp.route('/pathways/analyze', methods=['POST'])
def analyze_pathway_fit_api():
    """
    Execute combined Eligibility and Skill Gap fit analysis on provided payload or session.
    """
    data = request.get_json(silent=True) or {}
    try:
        result = PathwayAnalysisService.analyze_pathway_fit(context=data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Pathway fit analysis failed: {str(e)}"}), 500


@career_bp.route('/pathways/action-plan', methods=['POST'])
def create_pathway_action_plan():
    """
    Create a personalized action plan derived directly from the currently selected pathway
    and its completed Pathway Fit Analysis (Eligibility + Skill Gap).
    """
    data = request.get_json(silent=True) or {}

    fit_analysis = PathwayAnalysisService.analyze_pathway_fit(context=data)
    if fit_analysis.get("status") == "clarification_needed" or not fit_analysis.get("selected_pathway"):
        return jsonify({
            "status": "error",
            "message": "Select a pathway first before creating an action plan.",
            "error": "No pathway selected."
        }), 400

    if fit_analysis.get("status") == "conflict_detected":
        return jsonify({
            "status": "error",
            "message": fit_analysis.get("error", "Conflict detected between target role and selected pathway."),
            "error": fit_analysis.get("error")
        }), 400

    student_id = data.get("student_id") or session.get("student_id") or 1
    selected_pathway = fit_analysis.get("selected_pathway")
    target_role = (
        data.get("target_role")
        or (selected_pathway.get("name") if isinstance(selected_pathway, dict) else None)
        or fit_analysis.get("target_role")
    )

    student_profile = fit_analysis.get("student_profile") or {}
    current_skills = data.get("current_skills") or student_profile.get("skills")
    education_level = data.get("education_level") or student_profile.get("education_level")
    timeline_months = data.get("timeline_months", 6)

    skill_gap = fit_analysis.get("skill_gap") or {}
    missing_skills = data.get("skill_gaps") or skill_gap.get("missing_skills", [])
    learning_areas = skill_gap.get("learning_areas", [])

    eligibility = fit_analysis.get("eligibility") or {}
    eligibility_status = eligibility.get("status")

    reuse_existing = data.get("reuse_existing", False)

    try:
        plan = PlannerService.create_plan(
            student_id=student_id,
            target_role=target_role,
            current_skills=current_skills,
            skill_gaps=missing_skills,
            education_level=education_level,
            timeline_months=timeline_months,
            eligibility_status=eligibility_status,
            eligibility_result=eligibility,
            pathway_data=selected_pathway,
            learning_areas=learning_areas,
            reuse_existing=reuse_existing,
        )
        session["active_plan_id"] = plan.id
        return jsonify(plan.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to create pathway action plan: {str(e)}"}), 500


@career_bp.route('/pathways/roadmap', methods=['GET'])
def get_pathway_career_roadmap():
    """
    Retrieve the end-to-end career roadmap connecting the selected pathway,
    student profile, eligibility, skill gap analysis, and action plan.
    """
    student_id = session.get("student_id") or 1
    fit_analysis = PathwayAnalysisService.analyze_pathway_fit()

    selected_pathway = fit_analysis.get("selected_pathway")
    eligibility = fit_analysis.get("eligibility")
    skill_gap = fit_analysis.get("skill_gap")
    student_profile = fit_analysis.get("student_profile") or {}

    try:
        roadmap = RoadmapService.build_roadmap(
            student_id=student_id,
            target_role=selected_pathway.get("name") if isinstance(selected_pathway, dict) else None,
            current_skills=student_profile.get("skills"),
            pathway_data=selected_pathway,
            eligibility_result=eligibility,
            skill_gap_result=skill_gap,
        )
        return jsonify(roadmap), 200
    except Exception as e:
        return jsonify({"error": f"Failed to build pathway career roadmap: {str(e)}"}), 500


