from flask import jsonify, request, session
from . import opportunities_bp
from .services import OpportunityService


@opportunities_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Opportunities (Jobs, Govt Jobs, Exams, Internships, Scholarships) module."""
    return jsonify({
        "status": "healthy",
        "module": "opportunities_navigator"
    }), 200


@opportunities_bp.route('/sectors', methods=['GET'])
def get_sectors():
    """
    Retrieve dynamically calculated sectors and their job counts for a category.
    """
    category = request.args.get('category') or request.args.get('type')
    result = OpportunityService.get_sectors(category=category)
    return jsonify(result), 200


@opportunities_bp.route('/skills', methods=['GET'])
def get_skills():
    """
    Retrieve unique available skills for a given category and sector.
    """
    category = request.args.get('category') or request.args.get('type')
    sector = request.args.get('sector')
    result = OpportunityService.get_available_skills(category=category, sector=sector)
    return jsonify(result), 200


@opportunities_bp.route('/match', methods=['GET', 'POST'])
def match_opportunities():
    """
    Match opportunities based on Category, Sector, Education Level, and Multi-Select Skills.
    Returns ALL matching jobs ordered by relevance score with explainability metadata.
    """
    if request.method == 'POST' and request.is_json:
        data = request.get_json(silent=True) or {}
        category = data.get('category') or data.get('type')
        sector = data.get('sector')
        education_level = data.get('education_level') or data.get('qualification')
        skills = data.get('skills') or []
    else:
        category = request.args.get('category') or request.args.get('type')
        sector = request.args.get('sector')
        education_level = request.args.get('education_level') or request.args.get('qualification')
        # skills can be passed as multiple params or comma-separated
        skills_arg = request.args.getlist('skills') or request.args.getlist('skills[]')
        if not skills_arg and request.args.get('skills'):
            skills_arg = [s.strip() for s in request.args.get('skills').split(',') if s.strip()]
        skills = skills_arg

    # If education level not passed, look up student profile/session
    if not education_level:
        education_level = OpportunityService.get_student_qualification()

    result = OpportunityService.match_jobs(
        category=category,
        sector=sector,
        education_level=education_level,
        skills=skills
    )
    return jsonify(result), 200


@opportunities_bp.route('/jobs', methods=['GET', 'POST'])
@opportunities_bp.route('/list', methods=['GET'])
def list_opportunities():
    """
    Retrieve verified job and government opportunities filtered by
    category ('govt_job' or 'private_job') and student qualification.
    """
    category = None
    qualification = None

    if request.method == 'POST' and request.is_json:
        data = request.get_json(silent=True) or {}
        category = data.get('category') or data.get('type')
        qualification = data.get('qualification') or data.get('education_level')
    else:
        category = request.args.get('category') or request.args.get('type')
        qualification = request.args.get('qualification') or request.args.get('education_level')

    if not qualification:
        qualification = OpportunityService.get_student_qualification()

    result = OpportunityService.get_opportunities(category=category, qualification=qualification)
    return jsonify(result), 200


@opportunities_bp.route('/qualification', methods=['GET'])
def get_current_qualification():
    """
    Retrieve the current student's known qualification and skills from active profile/session
    without modifying career state.
    """
    qual = OpportunityService.get_student_qualification()
    skills = OpportunityService.get_student_skills()
    return jsonify({
        "status": "success",
        "qualification": qual,
        "skills": skills,
        "is_detected": bool(qual or skills)
    }), 200


