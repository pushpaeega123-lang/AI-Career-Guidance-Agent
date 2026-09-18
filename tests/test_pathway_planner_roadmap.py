import json
import pytest
from app import create_app
from db import db
from profile.models import StudentProfile
from planner.models import ActionPlan
from planner.services import PlannerService
from planner.roadmap import RoadmapService
from career.services import CareerDirectionService, PathwayDiscoveryService, PathwayAnalysisService
from agents.orchestrator import AgentOrchestrator
from agents.specialized_agents import PlannerAgent, RoadmapAgent


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        # Seed test student profile
        student = StudentProfile(
            id=1,
            full_name="Alex Chen",
            email="alex@example.com",
            education_level="Bachelor's",
            skills_json=json.dumps(["Python", "Problem Solving", "Git"]),
            interests_json=json.dumps(["technology", "engineering"]),
        )
        db.session.add(student)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# =============================================================================
# 1. Action Plan Generation from Selected Pathway
# =============================================================================

def test_selected_pathway_creates_action_plan(app):
    """Verify that a selected pathway can generate a personalized action plan."""
    with app.app_context():
        pathway = {
            "id": "cloud-devops",
            "name": "Cloud Architecture & DevOps",
            "industry_sector": "Technology",
            "relevant_skills": ["Programming", "Linux", "Docker", "Kubernetes", "AWS"]
        }
        plan = PlannerService.create_plan(
            student_id=1,
            target_role="Cloud Architecture & DevOps",
            current_skills=["Python", "Git"],
            skill_gaps=["Linux", "Docker", "Kubernetes", "AWS"],
            pathway_data=pathway,
            eligibility_status="ELIGIBLE"
        )
        assert plan.id is not None
        assert plan.target_role == "Cloud Architecture & DevOps"
        milestones = plan.get_milestones()
        assert len(milestones) == 11
        assert any("Linux, Docker" in m["title"] or "Linux, Docker" in m["description"] for m in milestones)


def test_planner_receives_pathway_analysis_context(app):
    """Verify planner incorporates pathway analysis context (skills, education, eligibility)."""
    with app.app_context():
        analysis_context = {
            "selected_pathway": {
                "id": "data-science-analytics",
                "name": "Data Science & Analytics",
                "typical_next_step": "Master SQL and statistical modeling."
            },
            "eligibility": {"status": "ELIGIBLE", "eligible": True},
            "skill_gap": {
                "missing_skills": ["SQL", "Statistics", "Machine Learning"],
                "match_rate": 40.0
            }
        }
        milestones = PlannerService.generate_milestones(
            target_role=analysis_context["selected_pathway"]["name"],
            current_skills=["Python"],
            skill_gaps=analysis_context["skill_gap"]["missing_skills"],
            eligibility_status=analysis_context["eligibility"]["status"],
            pathway_data=analysis_context["selected_pathway"]
        )
        assert len(milestones) == 11
        m3 = next(m for m in milestones if m["id"] == "m3")
        assert "SQL, Statistics, Machine Learning" in m3["title"]


def test_skill_gaps_influence_planner_milestones(app):
    """Verify actual missing skills directly parameterize milestone descriptions."""
    with app.app_context():
        gaps = ["Docker", "Kubernetes", "Terraform", "CI/CD"]
        milestones = PlannerService.generate_milestones(
            target_role="DevOps Engineer",
            current_skills=["Linux"],
            skill_gaps=gaps
        )
        m3 = next(m for m in milestones if m["id"] == "m3")
        assert "Docker, Kubernetes, Terraform, CI/CD" in m3["title"]
        m5 = next(m for m in milestones if m["id"] == "m5")
        assert "Docker" in m5["title"]


# =============================================================================
# 2. Eligibility-Aware Planning
# =============================================================================

def test_not_eligible_produces_prerequisite_milestone(app):
    """Verify NOT_ELIGIBLE creates prerequisite education milestone instead of direct application."""
    with app.app_context():
        milestones = PlannerService.generate_milestones(
            target_role="Medicine & Healthcare",
            current_skills=["Biology"],
            skill_gaps=["Clinical Diagnostics", "Patient Care"],
            eligibility_status="NOT_ELIGIBLE"
        )
        m1 = next(m for m in milestones if m["id"] == "m1")
        assert "Prerequisite Qualification Action" in m1["title"]
        assert m1["category"] == "Education"
        assert m1["priority"] == "High"

        m11 = next(m for m in milestones if m["id"] == "m11")
        assert "Verify Eligibility & Submit Applications" in m11["title"]
        assert "Re-verify eligibility requirements after satisfying prerequisite qualifications" in m11["description"]


def test_needs_verification_produces_documentation_milestone(app):
    """Verify NEEDS_VERIFICATION creates credential verification & documentation milestone."""
    with app.app_context():
        milestones = PlannerService.generate_milestones(
            target_role="Civil & Infrastructure Engineering",
            current_skills=["Mathematics"],
            skill_gaps=["Structural Mechanics"],
            eligibility_status="NEEDS_VERIFICATION"
        )
        m1 = next(m for m in milestones if m["id"] == "m1")
        assert "Prerequisite Verification & Documentation" in m1["title"]
        assert m1["category"] == "Preparation"


def test_eligible_produces_standard_pathway_setup_milestone(app):
    """Verify ELIGIBLE creates baseline setup and fast-track preparation."""
    with app.app_context():
        milestones = PlannerService.generate_milestones(
            target_role="Software Engineering",
            current_skills=["Python", "Git"],
            skill_gaps=["Databases"],
            eligibility_status="ELIGIBLE"
        )
        m1 = next(m for m in milestones if m["id"] == "m1")
        assert "Baseline Assessment & Pathway Setup" in m1["title"]
        assert m1["category"] == "Preparation"


# =============================================================================
# 3. Persistence & Duplicate Plan Prevention
# =============================================================================

def test_planner_reuses_existing_persistence(app):
    """Verify ActionPlan database table is reused for plan storage."""
    with app.app_context():
        initial_count = ActionPlan.query.count()
        plan = PlannerService.create_plan(
            student_id=1,
            target_role="Backend Developer",
            skill_gaps=["FastAPI", "PostgreSQL"]
        )
        assert ActionPlan.query.count() == initial_count + 1
        fetched = PlannerService.get_plan_by_id(plan.id)
        assert fetched is not None
        assert fetched.target_role == "Backend Developer"


def test_no_duplicate_plan_created_when_reuse_existing_is_true(app):
    """Verify reuse_existing=True returns existing plan without creating a duplicate record."""
    with app.app_context():
        plan1 = PlannerService.create_plan(
            student_id=1,
            target_role="Cloud Engineer",
            skill_gaps=["AWS", "Docker"]
        )
        plan2 = PlannerService.create_plan(
            student_id=1,
            target_role="Cloud Engineer",
            skill_gaps=["AWS", "Docker"],
            reuse_existing=True
        )
        assert plan1.id == plan2.id


# =============================================================================
# 4. Roadmap Integration & Progress Sync
# =============================================================================

def test_roadmap_consumes_planner_data(app):
    """Verify roadmap consumes active plan milestones and reflects target pathway."""
    with app.app_context():
        plan = PlannerService.create_plan(
            student_id=1,
            target_role="Cloud Architecture & DevOps",
            skill_gaps=["Linux", "Docker", "Kubernetes"]
        )
        pathway = {
            "id": "cloud-devops",
            "name": "Cloud Architecture & DevOps",
            "industry_sector": "Technology"
        }
        roadmap = RoadmapService.build_roadmap(
            student_id=1,
            pathway_data=pathway,
            eligibility_result={"status": "ELIGIBLE", "eligible": True},
            skill_gap_result={"matching_skills": ["Git"], "missing_skills": ["Docker", "Kubernetes"], "match_rate": 33.3, "gap_percentage": 66.7}
        )
        assert roadmap["career_goal"] == "Cloud Architecture & DevOps"
        assert roadmap["active_plan_id"] == plan.id
        s6 = next(s for s in roadmap["stages"] if s["stage_id"] == "action_plan_milestones")
        assert s6["data"]["total_milestones"] == 11


def test_roadmap_reflects_milestone_progress_update(app):
    """Verify completing a milestone in ActionPlan updates the roadmap calculated progress."""
    with app.app_context():
        plan = PlannerService.create_plan(
            student_id=1,
            target_role="AI Engineer",
            skill_gaps=["PyTorch", "MLOps"]
        )
        initial_roadmap = RoadmapService.build_roadmap(student_id=1)
        initial_pct = initial_roadmap["roadmap_progress_percentage"]

        # Complete first two milestones
        PlannerService.update_milestone_status(plan.id, "m1", "completed")
        PlannerService.update_milestone_status(plan.id, "m2", "completed")

        updated_roadmap = RoadmapService.build_roadmap(student_id=1)
        updated_pct = updated_roadmap["roadmap_progress_percentage"]

        assert updated_pct > initial_pct
        s6 = next(s for s in updated_roadmap["stages"] if s["stage_id"] == "action_plan_milestones")
        assert s6["data"]["completed_milestones"] == 2


# =============================================================================
# 5. Missing Data & Safe Fallbacks
# =============================================================================

def test_missing_pathway_handled_safely(app):
    """Verify roadmap handles missing pathway without throwing unhandled exceptions."""
    with app.app_context():
        roadmap = RoadmapService.build_roadmap(student_id=1)
        assert roadmap["student_name"] == "Alex Chen"
        assert "stages" in roadmap
        assert len(roadmap["stages"]) == 6


def test_missing_student_profile_handled_safely(app):
    """Verify non-existent student raises a clean ValueError."""
    with app.app_context():
        with pytest.raises(ValueError) as exc_info:
            RoadmapService.build_roadmap(student_id=999)
        assert "Student with ID 999 not found" in str(exc_info.value)


def test_missing_analysis_handled_safely_in_api(client):
    """Verify POST /api/career/pathways/action-plan handles unselected pathway safely."""
    res = client.post('/api/career/pathways/action-plan', json={})
    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data or "message" in data


# =============================================================================
# 6. Specialized Agents & Multi-Agent Orchestration
# =============================================================================

def test_planner_agent_processes_task_with_structured_output(app):
    """Verify PlannerAgent returns structured schema required by acceptance criteria."""
    with app.app_context():
        agent = PlannerAgent()
        res = agent.process_task({
            "student_id": 1,
            "target_role": "Data Scientist",
            "skill_gaps": ["Pandas", "Scikit-Learn"]
        })
        assert res["status"] == "success"
        assert res["agent"] == "PlannerAgent"
        assert res["action"] == "create_action_plan"
        assert res["plan_id"] is not None
        assert res["milestone_count"] == 11
        assert "next_action" in res


def test_roadmap_agent_processes_task_with_structured_output(app):
    """Verify RoadmapAgent returns structured schema required by acceptance criteria."""
    with app.app_context():
        PlannerService.create_plan(student_id=1, target_role="Data Scientist")
        agent = RoadmapAgent()
        res = agent.process_task({
            "student_id": 1,
            "target_role": "Data Scientist"
        })
        assert res["status"] == "success"
        assert res["agent"] == "RoadmapAgent"
        assert res["action"] == "generate_roadmap"
        assert res["stage_count"] == 6
        assert "progress" in res


def test_orchestrator_routes_planner_and_roadmap_sequence(app):
    """Verify AgentOrchestrator routes natural queries to PlannerAgent and RoadmapAgent."""
    with app.app_context():
        orchestrator = AgentOrchestrator()

        # Route action plan request
        plan_res = orchestrator.route_request("Create my action plan for Cloud Engineer", context={"student_id": 1})
        assert plan_res["status"] == "success"
        assert plan_res["intent"] == "planner"
        assert plan_res["agent_used"] == "PlannerAgent"

        # Route roadmap request
        rm_res = orchestrator.route_request("Show my roadmap", context={"student_id": 1})
        assert rm_res["status"] == "success"
        assert rm_res["intent"] == "roadmap"
        assert rm_res["agent_used"] == "RoadmapAgent"


# =============================================================================
# 7. End-to-End API Integration & UI Routes
# =============================================================================

def test_api_create_pathway_action_plan_flow(client):
    """Verify complete session-based API flow from selection to action plan creation."""
    # 1. Set career direction
    res = client.post('/api/career/direction', json={"career_direction": "known", "target_role": "Cloud Architect"})
    assert res.status_code == 200

    # 2. Select pathway
    res = client.post('/api/career/pathways/select', json={"pathway_id": "cloud-devops", "pathway_name": "Cloud Architecture & DevOps"})
    assert res.status_code == 200

    # 3. Create action plan derived from selected pathway
    res = client.post('/api/career/pathways/action-plan', json={"student_id": 1})
    assert res.status_code == 201
    plan_data = res.get_json()
    assert plan_data["target_role"] == "Cloud Architecture & DevOps"
    assert len(plan_data["milestones"]) == 11

    # 4. Fetch roadmap
    res = client.get('/api/career/pathways/roadmap')
    assert res.status_code == 200
    rm_data = res.get_json()
    assert rm_data["career_goal"] == "Cloud Architecture & DevOps"
    assert rm_data["active_plan_id"] == plan_data["id"]


def test_ui_routes_load_cleanly(client):
    """Verify /planner and /roadmap pages render successfully."""
    res_planner = client.get('/planner')
    assert res_planner.status_code == 200
    html_planner = res_planner.get_data(as_text=True)
    assert "Personalized Career Action Planner" in html_planner
    assert "Step 5: Action Plan" in html_planner

    res_roadmap = client.get('/roadmap')
    assert res_roadmap.status_code == 200
    html_roadmap = res_roadmap.get_data(as_text=True)
    assert "Unified Career Journey Roadmap" in html_roadmap
    assert "Step 6: Career Roadmap" in html_roadmap


def test_health_endpoints_remain_functional(client):
    """Verify all health endpoints across modules remain healthy."""
    for mod in ['career', 'planner', 'eligibility', 'skill-gap', 'profile', 'agents']:
        res = client.get(f'/api/{mod}/health')
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "healthy"
