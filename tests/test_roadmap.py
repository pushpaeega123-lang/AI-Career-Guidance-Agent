import json
import pytest
from db import db
from opportunities.models import Opportunity
from planner.roadmap import RoadmapService
from planner.services import PlannerService
from profile.models import StudentProfile


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def student_with_full_journey(app):
    """Create a sample student with action plan and opportunities in test DB."""
    with app.app_context():
        # 1. Student Profile
        student = StudentProfile(
            full_name="Samantha Ray",
            email="samantha.ray@example.com",
            education_level="Bachelor of Technology in CS",
            interests_json=json.dumps(["Cloud Architecture", "DevOps"])
        )
        db.session.add(student)
        db.session.commit()

        # 2. Sample Opportunity
        opp = Opportunity(
            title="Junior DevOps Engineer",
            organization="CloudTech Innovations",
            opportunity_type="job",
            deadline="2026-12-31"
        )
        db.session.add(opp)
        db.session.commit()

        # 3. Action Plan
        plan = PlannerService.create_plan(
            student_id=student.id,
            target_role="Cloud & DevOps Engineer",
            current_skills=["Linux", "Python", "Git"],
            skill_gaps=["Docker", "Kubernetes", "AWS"],
            timeline_months=6
        )

        # Mark first milestone completed
        PlannerService.update_milestone_status(plan.id, "m1", "completed")

        return {
            "student_id": student.id,
            "plan_id": plan.id,
            "opp_id": opp.id
        }


@pytest.fixture
def student_minimal(app):
    """Create a minimal student profile with no action plan or skills."""
    with app.app_context():
        student = StudentProfile(
            full_name="Jordan Lee",
            email="jordan.lee@example.com"
            # No education_level, no interests
        )
        db.session.add(student)
        db.session.commit()
        return student.id


# =============================================================================
# Unit & Service Tests for Roadmap
# =============================================================================

def test_complete_roadmap_generation(app, student_with_full_journey):
    """Verify complete roadmap builds successfully connecting all 6 stages."""
    student_id = student_with_full_journey["student_id"]

    with app.app_context():
        roadmap = RoadmapService.build_roadmap(
            student_id=student_id,
            current_skills=["Linux", "Python", "Git"],
            target_skills=["Linux", "Python", "Git", "Docker", "Kubernetes", "AWS"]
        )

        assert roadmap["student_id"] == student_id
        assert roadmap["student_name"] == "Samantha Ray"
        assert roadmap["career_goal"] == "Cloud & DevOps Engineer"
        assert roadmap["education_level"] == "Bachelor of Technology in CS"
        assert roadmap["roadmap_progress_percentage"] > 0.0
        assert roadmap["next_recommended_action"] is not None

        stages = roadmap["stages"]
        assert len(stages) == 6

        stage_ids = [s["stage_id"] for s in stages]
        assert "profile_foundation" in stage_ids
        assert "career_goal" in stage_ids
        assert "education_pathway" in stage_ids
        assert "skills_assessment" in stage_ids
        assert "opportunities_eligibility" in stage_ids
        assert "action_plan_milestones" in stage_ids


def test_roadmap_missing_data_graceful_handling(app, student_minimal):
    """Verify missing data attributes show 'Information not available' without failing."""
    with app.app_context():
        roadmap = RoadmapService.build_roadmap(student_id=student_minimal)

        assert roadmap["student_id"] == student_minimal
        assert roadmap["student_name"] == "Jordan Lee"
        assert roadmap["education_level"] == "Information not available"
        assert roadmap["career_goal"] == "Information not available"

        stages = {s["stage_id"]: s for s in roadmap["stages"]}

        # Stage 1
        assert stages["profile_foundation"]["data"]["current_education"] == "Information not available"
        assert stages["profile_foundation"]["data"]["interests"] == "Information not available"

        # Stage 2
        assert stages["career_goal"]["data"]["target_role"] == "Information not available"
        assert stages["career_goal"]["status"] == "pending"

        # Stage 4
        assert stages["skills_assessment"]["data"]["current_skills"] == "Information not available"
        assert stages["skills_assessment"]["status"] == "pending"


def test_invalid_student_id_raises_value_error(app):
    """Verify build_roadmap raises ValueError for non-existent student."""
    with app.app_context():
        with pytest.raises(ValueError) as exc_info:
            RoadmapService.build_roadmap(student_id=99999)
        assert "not found" in str(exc_info.value).lower()


def test_roadmap_progress_calculation(app, student_with_full_journey):
    """Verify progress changes appropriately when milestones or stages are completed."""
    student_id = student_with_full_journey["student_id"]
    plan_id = student_with_full_journey["plan_id"]

    with app.app_context():
        rm1 = RoadmapService.build_roadmap(student_id=student_id)
        initial_progress = rm1["roadmap_progress_percentage"]

        # Complete more milestones in action plan
        PlannerService.update_milestone_status(plan_id, "m2", "completed")
        PlannerService.update_milestone_status(plan_id, "m3", "completed")

        rm2 = RoadmapService.build_roadmap(student_id=student_id)
        updated_progress = rm2["roadmap_progress_percentage"]

        assert updated_progress > initial_progress


# =============================================================================
# Integration & API Tests for Roadmap
# =============================================================================

def test_api_get_student_roadmap(client, student_with_full_journey):
    """Verify GET /api/planner/roadmap/<student_id> endpoint returns 200 and roadmap."""
    student_id = student_with_full_journey["student_id"]
    response = client.get(f'/api/planner/roadmap/{student_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data["student_id"] == student_id
    assert "stages" in data
    assert len(data["stages"]) == 6


def test_api_get_student_roadmap_not_found(client):
    """Verify GET /api/planner/roadmap/99999 returns 404."""
    response = client.get('/api/planner/roadmap/999999')
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_api_post_custom_roadmap(client, student_with_full_journey):
    """Verify POST /api/planner/roadmap generates custom roadmap with parameters."""
    student_id = student_with_full_journey["student_id"]
    payload = {
        "student_id": student_id,
        "target_role": "Lead Architect",
        "current_skills": ["Python", "AWS"],
        "target_skills": ["Python", "AWS", "Kubernetes", "Distributed Systems"]
    }
    response = client.post('/api/planner/roadmap', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["career_goal"] == "Lead Architect"


def test_api_roadmap_view_route(client):
    """Verify GET /api/planner/roadmap/view renders the visual roadmap template."""
    response = client.get('/api/planner/roadmap/view')
    assert response.status_code == 200
    assert b"Unified Career Journey Roadmap" in response.data
