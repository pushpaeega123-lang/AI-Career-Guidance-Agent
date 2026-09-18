from flask import jsonify, render_template, request
from . import planner_bp
from .roadmap import RoadmapService
from .services import PlannerService


@planner_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Personalized Career Action Planner module."""
    return jsonify({
        "status": "healthy",
        "module": "personalized_action_planner"
    }), 200


@planner_bp.route('/demo', methods=['GET'])
def planner_demo_view():
    """Interactive roadmap view for Personalized Career Action Planner."""
    return render_template('planner.html')


@planner_bp.route('/roadmap/view', methods=['GET'])
@planner_bp.route('/roadmap/demo', methods=['GET'])
@planner_bp.route('/roadmap-view', methods=['GET'])
def career_roadmap_view():
    """Unified visual Career Roadmap dashboard connecting all stages of the journey."""
    return render_template('roadmap.html')


@planner_bp.route('/plan', methods=['POST'])
@planner_bp.route('/create', methods=['POST'])
def create_action_plan():
    """
    Create a new personalized action plan with sequenced milestones.

    Expected JSON body payload:
    {
        "student_id": 1,
        "target_role": "Backend Engineer",
        "current_skills": ["Python", "SQL"],
        "skill_gaps": ["Docker", "Kubernetes"],
        "timeline_months": 6
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

    student_id = data.get("student_id")
    target_role = data.get("target_role") or data.get("role") or data.get("career_goal")
    current_skills = data.get("current_skills") or data.get("skills")
    skill_gaps = data.get("skill_gaps") or data.get("missing_skills")
    education_level = data.get("education_level")
    timeline_months = data.get("timeline_months", 6)

    if student_id is None:
        return jsonify({"error": "student_id is required."}), 400

    if not target_role or not str(target_role).strip():
        return jsonify({"error": "target_role is required and cannot be empty."}), 400

    try:
        plan = PlannerService.create_plan(
            student_id=student_id,
            target_role=target_role,
            current_skills=current_skills,
            skill_gaps=skill_gaps,
            education_level=education_level,
            timeline_months=timeline_months,
        )
        return jsonify(plan.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to create action plan: {str(e)}"}), 500


@planner_bp.route('/plan/<int:plan_id>', methods=['GET'])
def get_action_plan(plan_id):
    """Retrieve action plan details by ID."""
    plan = PlannerService.get_plan_by_id(plan_id)
    if not plan:
        return jsonify({"error": f"Action plan with ID {plan_id} not found."}), 404
    return jsonify(plan.to_dict()), 200


@planner_bp.route('/student/<int:student_id>', methods=['GET'])
def get_student_plans(student_id):
    """Retrieve all action plans for a specific student."""
    plans = PlannerService.get_plans_by_student(student_id)
    return jsonify({
        "student_id": student_id,
        "count": len(plans),
        "plans": [p.to_dict() for p in plans]
    }), 200


@planner_bp.route('/plan/<int:plan_id>/milestone/<string:milestone_id>', methods=['PATCH', 'POST'])
def update_milestone_status(plan_id, milestone_id):
    """
    Update the status of a specific milestone within an action plan.

    Expected JSON body payload:
    {
        "status": "completed"  # "pending" | "in_progress" | "completed"
    }
    """
    if not request.is_json and request.content_type != 'application/json':
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Request body must be a valid JSON object."}), 400
    else:
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Invalid JSON format or empty request body."}), 400

    new_status = data.get("status")
    if not new_status:
        return jsonify({"error": "Status field is required."}), 400

    try:
        updated_plan = PlannerService.update_milestone_status(
            plan_id=plan_id,
            milestone_id=milestone_id,
            new_status=new_status,
        )
        return jsonify(updated_plan.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update milestone: {str(e)}"}), 500


@planner_bp.route('/roadmap/<int:student_id>', methods=['GET'])
def get_student_career_roadmap(student_id):
    """
    Retrieve the unified career roadmap for a student.
    Connects Student Profile → Career Goal → Education → Skills → Opportunities → Action Plan → Progress.
    """
    try:
        roadmap = RoadmapService.build_roadmap(student_id=student_id)
        return jsonify(roadmap), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to build career roadmap: {str(e)}"}), 500


@planner_bp.route('/roadmap', methods=['POST'])
def generate_custom_career_roadmap():
    """
    Generate or preview a unified career roadmap with custom parameters.
    """
    if not request.is_json and request.content_type != 'application/json':
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Request body must be a valid JSON object."}), 400
    else:
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Invalid JSON format or empty request body."}), 400

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON dictionary."}), 400

    student_id = data.get("student_id")
    if student_id is None:
        return jsonify({"error": "student_id is required."}), 400

    target_role = data.get("target_role") or data.get("role")
    current_skills = data.get("current_skills") or data.get("skills")
    target_skills = data.get("target_skills") or data.get("required_skills")
    opportunity_id = data.get("opportunity_id")

    try:
        roadmap = RoadmapService.build_roadmap(
            student_id=student_id,
            target_role=target_role,
            current_skills=current_skills,
            target_skills=target_skills,
            opportunity_id=opportunity_id,
        )
        return jsonify(roadmap), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to build career roadmap: {str(e)}"}), 500
