from flask import jsonify, render_template, request
from . import skill_gap_bp
from .services import SkillGapService


@skill_gap_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Skill Gap Analysis module."""
    return jsonify({
        "status": "healthy",
        "module": "skill_gap_analyzer"
    }), 200


@skill_gap_bp.route('/demo', methods=['GET'])
def skill_gap_demo_view():
    """Interactive dashboard view for Skill Gap Analysis."""
    return render_template('skill_gap.html')


@skill_gap_bp.route('/analyze', methods=['POST'])
def analyze_skill_gap():
    """
    Analyze skill gap between student current skills and target career skills.

    Expected JSON body payload:
    {
        "current_skills": ["Python", "Flask", "SQL"],
        "target_skills": ["Python", "Flask", "SQL", "Docker", "Kubernetes"]
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

    # Extract current student skills
    current_skills = (
        data.get("current_skills")
        or data.get("student_skills")
        or data.get("student")
        or data.get("current")
        or []
    )

    # Extract target career / opportunity required skills
    target_skills = (
        data.get("target_skills")
        or data.get("target_career_skills")
        or data.get("required_skills")
        or data.get("target")
        or data.get("career_skills")
        or []
    )

    # Execute deterministic analysis
    result = SkillGapService.analyze_gap(
        current_skills=current_skills,
        target_career_skills=target_skills
    )

    return jsonify(result), 200
