import pytest
from db import db
from planner.models import ActionPlan
from planner.services import PlannerService
from profile.models import StudentProfile


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_student(app):
    """Create a sample student profile in test DB."""
    with app.app_context():
        student = StudentProfile(
            full_name="Alex Chen",
            email="alex.chen@example.com",
            education_level="Bachelor of Technology"
        )
        db.session.add(student)
        db.session.commit()
        student_id = student.id
        return student_id


# =============================================================================
# Unit & Service Tests for Planner
# =============================================================================

def test_milestone_generation_structure():
    """Verify generated milestones contain all required phases, categories, and fields."""
    milestones = PlannerService.generate_milestones(
        target_role="Cloud DevOps Engineer",
        current_skills=["Python", "Linux"],
        skill_gaps=["Docker", "Kubernetes", "Terraform"],
        education_level="Bachelor's",
        timeline_months=6
    )

    assert len(milestones) >= 10

    phases = {m["phase"] for m in milestones}
    assert "immediate" in phases
    assert "short_term" in phases
    assert "medium_term" in phases
    assert "long_term" in phases

    categories = {m["category"] for m in milestones}
    assert "Preparation" in categories
    assert "Skill Development" in categories
    assert "Experience" in categories
    assert "Application" in categories

    for m in milestones:
        assert "id" in m
        assert "title" in m
        assert "description" in m
        assert "priority" in m
        assert "timeframe" in m
        assert m["status"] == "pending"


def test_plan_creation_and_persistence(app, sample_student):
    """Test creating an action plan and verifying DB persistence."""
    with app.app_context():
        plan = PlannerService.create_plan(
            student_id=sample_student,
            target_role="Full-Stack Web Developer",
            current_skills=["HTML", "CSS", "JavaScript"],
            skill_gaps=["React", "Node.js", "Docker"],
            timeline_months=6
        )

        assert plan.id is not None
        assert plan.student_id == sample_student
        assert plan.target_role == "Full-Stack Web Developer"
        assert plan.timeline_months == 6

        plan_dict = plan.to_dict()
        assert plan_dict["total_milestones"] > 0
        assert plan_dict["completed_milestones"] == 0
        assert plan_dict["progress_percentage"] == 0.0
        assert plan_dict["next_recommended_action"] is not None
        assert plan_dict["next_recommended_action"]["id"] == "m1"


def test_plan_retrieval_by_id_and_student(app, sample_student):
    """Test retrieving plan by ID and by student ID."""
    with app.app_context():
        plan1 = PlannerService.create_plan(
            student_id=sample_student,
            target_role="Backend Developer"
        )
        plan2 = PlannerService.create_plan(
            student_id=sample_student,
            target_role="Data Engineer"
        )

        # Retrieve by ID
        fetched = PlannerService.get_plan_by_id(plan1.id)
        assert fetched is not None
        assert fetched.target_role == "Backend Developer"

        # Retrieve by student
        student_plans = PlannerService.get_plans_by_student(sample_student)
        assert len(student_plans) == 2


def test_progress_calculation_and_next_action(app, sample_student):
    """Test accurate progress calculation and dynamic next recommended action."""
    with app.app_context():
        plan = PlannerService.create_plan(
            student_id=sample_student,
            target_role="Site Reliability Engineer"
        )

        initial_progress = plan.calculate_progress()
        assert initial_progress["progress_percentage"] == 0.0
        assert initial_progress["completed_milestones"] == 0
        assert initial_progress["next_recommended_action"]["id"] == "m1"

        # Update first milestone to completed
        PlannerService.update_milestone_status(plan.id, "m1", "completed")
        updated_plan = PlannerService.get_plan_by_id(plan.id)
        prog1 = updated_plan.calculate_progress()

        assert prog1["completed_milestones"] == 1
        expected_pct = round((1 / prog1["total_milestones"]) * 100.0, 2)
        assert prog1["progress_percentage"] == expected_pct
        assert prog1["next_recommended_action"]["id"] == "m2"

        # Update second milestone to in_progress
        PlannerService.update_milestone_status(plan.id, "m2", "in_progress")
        prog2 = PlannerService.get_plan_by_id(plan.id).calculate_progress()
        assert prog2["in_progress_milestones"] == 1
        assert prog2["next_recommended_action"]["id"] == "m2"


def test_missing_optional_data_defaults(app, sample_student):
    """Verify plan creation works cleanly when optional data is omitted."""
    with app.app_context():
        plan = PlannerService.create_plan(
            student_id=sample_student,
            target_role="AI Engineer"
            # No current_skills, skill_gaps, education_level, or timeline passed
        )
        assert plan.id is not None
        assert plan.timeline_months == 6
        assert len(plan.get_milestones()) > 0


def test_invalid_student_id_raises_error(app):
    """Verify creating plan with non-existent student ID raises ValueError."""
    with app.app_context():
        with pytest.raises(ValueError) as exc_info:
            PlannerService.create_plan(
                student_id=99999,
                target_role="Cybersecurity Analyst"
            )
        assert "not found" in str(exc_info.value).lower()


def test_empty_career_goal_raises_error(app, sample_student):
    """Verify creating plan with empty/whitespace target role raises ValueError."""
    with app.app_context():
        with pytest.raises(ValueError) as exc_info:
            PlannerService.create_plan(
                student_id=sample_student,
                target_role=""
            )
        assert "empty" in str(exc_info.value).lower()


# =============================================================================
# API Route Integration Tests
# =============================================================================

def test_api_planner_health(client):
    """Verify GET /api/planner/health endpoint."""
    response = client.get('/api/planner/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["module"] == "personalized_action_planner"


def test_api_planner_create_success(client, sample_student):
    """Verify POST /api/planner/create returns 201 Created and full plan."""
    payload = {
        "student_id": sample_student,
        "target_role": "Full-Stack Engineer",
        "current_skills": ["Python", "Flask"],
        "skill_gaps": ["React", "Docker"],
        "timeline_months": 6
    }
    response = client.post('/api/planner/create', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["target_role"] == "Full-Stack Engineer"
    assert "milestones" in data
    assert "progress_percentage" in data
    assert "next_recommended_action" in data


def test_api_planner_create_invalid_payload(client):
    """Verify POST /api/planner/create with missing/invalid inputs returns 400."""
    # Missing student_id
    res1 = client.post('/api/planner/create', json={"target_role": "Architect"})
    assert res1.status_code == 400

    # Empty target_role
    res2 = client.post('/api/planner/create', json={"student_id": 1, "target_role": ""})
    assert res2.status_code == 400

    # Non-JSON content
    res3 = client.post('/api/planner/create', data="invalid", content_type="text/plain")
    assert res3.status_code == 400


def test_api_planner_get_plan_and_student_plans(client, sample_student):
    """Verify GET /api/planner/plan/<id> and GET /api/planner/student/<id>."""
    # Create plan first
    create_res = client.post('/api/planner/create', json={
        "student_id": sample_student,
        "target_role": "DevOps Specialist"
    })
    plan_id = create_res.get_json()["id"]

    # Retrieve plan by ID
    get_res = client.get(f'/api/planner/plan/{plan_id}')
    assert get_res.status_code == 200
    assert get_res.get_json()["id"] == plan_id

    # Retrieve by non-existent ID
    get_404 = client.get('/api/planner/plan/999999')
    assert get_404.status_code == 404

    # Retrieve by student ID
    student_res = client.get(f'/api/planner/student/{sample_student}')
    assert student_res.status_code == 200
    assert student_res.get_json()["count"] >= 1


def test_api_planner_update_milestone_status(client, sample_student):
    """Verify PATCH /api/planner/plan/<id>/milestone/<id> updates status and progress."""
    create_res = client.post('/api/planner/create', json={
        "student_id": sample_student,
        "target_role": "MLOps Engineer"
    })
    plan_id = create_res.get_json()["id"]

    # Update m1 to completed
    update_res = client.patch(f'/api/planner/plan/{plan_id}/milestone/m1', json={
        "status": "completed"
    })
    assert update_res.status_code == 200
    data = update_res.get_json()
    assert data["completed_milestones"] == 1
    assert data["progress_percentage"] > 0.0


def test_api_planner_demo_route(client):
    """Verify GET /api/planner/demo loads the dashboard template."""
    response = client.get('/api/planner/demo')
    assert response.status_code == 200
    assert b"Personalized Career Action Planner" in response.data
