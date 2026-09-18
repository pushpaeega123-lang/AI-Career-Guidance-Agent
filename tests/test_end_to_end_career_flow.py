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
from agents.specialized_agents import (
    EligibilityAgent,
    OpportunityPathwayAgent,
    PathwayAnalysisAgent,
    PlannerAgent,
    RoadmapAgent,
    SkillGapAgent,
)

JSON_HEADERS = {"Accept": "application/json"}


@pytest.fixture
def app():
    """Create test application context with in-memory database."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        # Seed standard test student
        student = StudentProfile(
            id=1,
            full_name="Alex Chen",
            email="alex.chen@example.com",
            education_level="B.Tech",
            skills_json=json.dumps(["Python", "Problem Solving", "Git"]),
            interests_json=json.dumps(["technology", "engineering", "ai"]),
        )
        db.session.add(student)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for simulating HTTP sessions and API interactions."""
    return app.test_client()


# =============================================================================
# Branch A: Known Target Career Flow (Tests 1-9)
# =============================================================================

def test_known_target_mode_selection(client):
    """1. Student chooses known-target mode with target role."""
    res = client.post('/api/career/direction', json={
        "career_direction": "known",
        "target_role": "Cloud Engineer"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["career_direction"] == "known"
    assert data["target_role"] == "Cloud Engineer"


def test_known_target_stored_in_state(client):
    """2. Target role is stored and retrievable from workflow state."""
    client.post('/api/career/direction', json={
        "career_direction": "known",
        "target_role": "Doctor"
    })
    res = client.get('/api/career/direction', headers=JSON_HEADERS)
    assert res.status_code == 200
    data = res.get_json()
    assert data["is_set"] is True
    assert data["career_direction"] == "known"
    assert data["target_role"] == "Doctor"


def test_known_target_pathway_resolution(client):
    """3. Target pathway is resolved directly for declared target role."""
    client.post('/api/career/direction', json={
        "career_direction": "known",
        "target_role": "Cloud Engineer"
    })
    res = client.get('/api/career/pathways', headers=JSON_HEADERS)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["career_direction"] == "known"
    assert data["total_pathways"] == 1
    assert data["target_role"] == "Cloud Engineer"
    assert len(data["pathways"]) == 1
    assert "Cloud" in data["pathways"][0]["name"]


def test_known_target_pathway_fit_analysis(client):
    """4. Pathway fit analysis evaluates student profile against target pathway."""
    client.post('/api/career/direction', json={
        "career_direction": "known",
        "target_role": "Software Engineer"
    })
    res = client.get('/api/career/pathways/analysis', headers=JSON_HEADERS)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["selected_pathway"] is not None
    assert "Software Engineering" in data["selected_pathway"]["name"]
    assert "eligibility" in data
    assert "skill_gap" in data


def test_known_target_eligibility_execution(client):
    """5. Eligibility engine executes and produces deterministic status and criteria."""
    client.post('/api/career/direction', json={
        "career_direction": "known",
        "target_role": "Software Engineer"
    })
    res = client.get('/api/career/pathways/analysis', headers=JSON_HEADERS)
    assert res.status_code == 200
    elig = res.get_json()["eligibility"]
    assert elig["status"] in ("ELIGIBLE", "NEEDS_VERIFICATION", "NOT_ELIGIBLE")
    assert isinstance(elig["satisfied_criteria"], list)
    assert isinstance(elig["reasons"], list)


def test_known_target_skill_gap_execution(client):
    """6. Skill gap engine compares current student skills against target pathway requirements."""
    client.post('/api/career/direction', json={
        "career_direction": "known",
        "target_role": "Software Engineer"
    })
    res = client.get('/api/career/pathways/analysis', headers=JSON_HEADERS)
    assert res.status_code == 200
    sg = res.get_json()["skill_gap"]
    assert "match_rate" in sg
    assert "gap_percentage" in sg
    assert isinstance(sg["matching_skills"], list)
    assert isinstance(sg["missing_skills"], list)
    assert isinstance(sg["learning_areas"], list)


def test_known_target_planner_creation(client):
    """7. Personalized action plan is created directly from pathway fit analysis."""
    client.post('/api/career/direction', json={
        "career_direction": "known",
        "target_role": "Cloud Engineer"
    })
    client.get('/api/career/pathways/analysis', headers=JSON_HEADERS)
    res = client.post('/api/career/pathways/action-plan', json={"reuse_existing": True})
    assert res.status_code == 201
    plan = res.get_json()
    assert plan["id"] is not None
    assert "Cloud" in plan["target_role"]
    assert plan["total_milestones"] > 0
    assert len(plan["milestones"]) > 0


def test_known_target_roadmap_generation(client):
    """8. Career roadmap is synthesized connecting profile, target, skills, and action plan."""
    client.post('/api/career/direction', json={
        "career_direction": "known",
        "target_role": "Cloud Engineer"
    })
    client.get('/api/career/pathways/analysis', headers=JSON_HEADERS)
    client.post('/api/career/pathways/action-plan', json={"reuse_existing": True})

    res = client.get('/api/career/pathways/roadmap', headers=JSON_HEADERS)
    assert res.status_code == 200
    roadmap = res.get_json()
    assert roadmap["student_name"] == "Alex Chen"
    assert "Cloud" in roadmap["career_goal"]
    assert len(roadmap["stages"]) == 6
    assert roadmap["roadmap_progress_percentage"] >= 0


def test_known_target_progress_tracking(client):
    """9. Milestone progress updates are tracked and reflected in the plan and roadmap."""
    client.post('/api/career/direction', json={
        "career_direction": "known",
        "target_role": "Software Engineer"
    })
    client.get('/api/career/pathways/analysis', headers=JSON_HEADERS)
    res_plan = client.post('/api/career/pathways/action-plan', json={"reuse_existing": True})
    plan_id = res_plan.get_json()["id"]

    # Mark milestone m1 as completed
    res_update = client.patch(f'/api/planner/plan/{plan_id}/milestone/m1', json={"status": "completed"})
    assert res_update.status_code == 200
    updated_plan = res_update.get_json()
    assert updated_plan["completed_milestones"] >= 1
    assert updated_plan["progress_percentage"] > 0


# =============================================================================
# Branch B: Exploring Student Flow (Tests 10-17)
# =============================================================================

def test_exploring_mode_selection(client):
    """10. Student chooses exploring mode."""
    res = client.post('/api/career/direction', json={
        "career_direction": "exploring"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["career_direction"] == "exploring"
    assert data["target_role"] is None


def test_exploring_questionnaire_storage(client):
    """11. Discovery questionnaire structured profile is stored."""
    payload = {
        "education_level": "B.Tech",
        "subjects": ["Computer Science", "Mathematics"],
        "skills": ["Python", "Problem Solving", "Git"],
        "interests": ["Technology", "AI", "Research"],
        "work_preferences": ["Working with technology", "Creative work"],
        "career_preferences": ["Private Sector", "Open to multiple options"]
    }
    res = client.post('/api/profile/discovery', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["is_completed"] is True


def test_exploring_multiple_pathways_returned(client):
    """12. Exploring student receives multiple explainable pathways without universal 'best career' claim."""
    client.post('/api/career/direction', json={"career_direction": "exploring"})
    client.post('/api/profile/discovery', json={
        "education_level": "B.Tech",
        "subjects": ["Computer Science", "Mathematics"],
        "skills": ["Python", "Problem Solving"],
        "interests": ["Technology", "AI"]
    })

    res = client.get('/api/career/pathways', headers=JSON_HEADERS)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["total_pathways"] >= 2
    for p in data["pathways"]:
        assert "why_relevant" in p
        # Verify neutral explainable wording (no 'best career' claim)
        assert "best career" not in p["why_relevant"].lower()
        assert "education_pathway" in p
        assert "sources" in p


def test_exploring_student_selects_pathway(client):
    """13. Exploring student can select a pathway from discovered options."""
    res = client.post('/api/career/pathways/select', json={
        "pathway_id": "cloud-devops",
        "pathway_name": "Cloud Architecture & DevOps"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["selected_pathway"]["id"] == "cloud-devops"
    assert data["selected_pathway"]["name"] == "Cloud Architecture & DevOps"


def test_exploring_selected_pathway_persists(client):
    """14. Selected pathway persists in session across subsequent requests."""
    client.post('/api/career/pathways/select', json={
        "pathway_id": "data-science-analytics",
        "pathway_name": "Data Science & Analytics"
    })
    res = client.get('/api/career/pathways/selected', headers=JSON_HEADERS)
    assert res.status_code == 200
    data = res.get_json()
    assert data["is_selected"] is True
    assert data["selected_pathway"]["id"] == "data-science-analytics"


def test_exploring_pathway_fit_analysis(client):
    """15. Pathway analysis evaluates fit for student's explicitly selected pathway."""
    client.post('/api/career/pathways/select', json={
        "pathway_id": "data-science-analytics",
        "pathway_name": "Data Science & Analytics"
    })
    res = client.get('/api/career/pathways/analysis', headers=JSON_HEADERS)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["selected_pathway"]["name"] == "Data Science & Analytics"
    assert data["eligibility"] is not None
    assert data["skill_gap"] is not None


def test_exploring_planner_creation(client):
    """16. Action plan is generated for the student's selected pathway."""
    client.post('/api/career/pathways/select', json={
        "pathway_id": "data-science-analytics",
        "pathway_name": "Data Science & Analytics"
    })
    client.get('/api/career/pathways/analysis', headers=JSON_HEADERS)
    res = client.post('/api/career/pathways/action-plan', json={"reuse_existing": True})
    assert res.status_code == 201
    plan = res.get_json()
    assert plan["target_role"] == "Data Science & Analytics"
    assert plan["total_milestones"] > 0


def test_exploring_roadmap_generation(client):
    """17. Complete roadmap is generated for the student's selected exploration pathway."""
    client.post('/api/career/pathways/select', json={
        "pathway_id": "data-science-analytics",
        "pathway_name": "Data Science & Analytics"
    })
    client.get('/api/career/pathways/analysis', headers=JSON_HEADERS)
    client.post('/api/career/pathways/action-plan', json={"reuse_existing": True})

    res = client.get('/api/career/pathways/roadmap', headers=JSON_HEADERS)
    assert res.status_code == 200
    roadmap = res.get_json()
    assert roadmap["career_goal"] == "Data Science & Analytics"
    assert len(roadmap["stages"]) == 6


# =============================================================================
# Safety, Validation & Edge States (Tests 18-24)
# =============================================================================

def test_safety_no_pathway_returns_clarification(client):
    """18. When no pathway is selected in exploring mode, analysis returns safe clarification."""
    client.post('/api/career/direction', json={"career_direction": "exploring"})
    client.delete('/api/career/pathways/selected')

    res = client.get('/api/career/pathways/analysis', headers=JSON_HEADERS)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "clarification_needed"
    assert data["selected_pathway"] is None
    assert "select a career pathway" in data["message"].lower()


def test_safety_no_profile_handles_gracefully(app):
    """19. Safe behavior when student profile has missing or empty attributes (returns safe zero-match state)."""
    with app.app_context():
        res = PathwayDiscoveryService.discover_pathways({"career_direction": "exploring", "exploration_profile": {}})
        assert res["status"] == "success"
        assert res["total_pathways"] == 0
        assert res["pathways"] == []
        assert "add more" in res["message"].lower()


def test_safety_no_analysis_planner_response(client):
    """20. Creating a pathway action plan without selecting a pathway returns 400."""
    client.post('/api/career/direction', json={"career_direction": "exploring"})
    client.delete('/api/career/pathways/selected')

    res = client.post('/api/career/pathways/action-plan', json={})
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "error"
    assert "select a pathway first" in data["message"].lower()


def test_safety_no_planner_roadmap_fallback(app):
    """21. Generating roadmap without an existing plan produces a safe informative roadmap."""
    with app.app_context():
        roadmap = RoadmapService.build_roadmap(student_id=1, target_role="Software Engineer")
        assert roadmap["student_id"] == 1
        assert len(roadmap["stages"]) == 6
        assert roadmap["career_goal"] == "Software Engineer"


def test_safety_needs_verification_preserved(app):
    """22. Incomplete or unverified qualifications preserve NEEDS_VERIFICATION."""
    with app.app_context():
        agent = EligibilityAgent()
        res = agent.process_task({
            "student_profile": {"education_level": "Undergraduate"},
            "opportunity": {"min_education": "Master of Science", "required_skills": ["C++"]}
        })
        assert res["status"] == "success"
        assert res["data"]["status"] in ("NEEDS_VERIFICATION", "NOT_ELIGIBLE")


def test_safety_not_eligible_handling(app):
    """23. NOT_ELIGIBLE status produces prerequisite milestones without misleading actions."""
    with app.app_context():
        milestones = PlannerService.generate_milestones(
            target_role="Medical Specialist",
            current_skills=["Biology"],
            skill_gaps=["MBBS", "Clinical Practice"],
            eligibility_status="NOT_ELIGIBLE"
        )
        assert len(milestones) > 0
        # Phase 1 milestone must focus on addressing missing prerequisites
        m1 = milestones[0]
        assert "Prerequisite" in m1["title"] or "Requirement" in m1["title"] or "Foundational" in m1["title"]


def test_safety_target_pathway_conflict_detection(client):
    """24. Declared target role vs conflicting selected pathway is detected and flagged."""
    client.post('/api/career/direction', json={
        "career_direction": "known",
        "target_role": "Doctor"
    })
    # Select completely conflicting pathway (Software Engineering)
    client.post('/api/career/pathways/select', json={
        "pathway_id": "software-engineering",
        "pathway_name": "Software Engineering"
    })

    res = client.get('/api/career/pathways/analysis', headers=JSON_HEADERS)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "conflict_detected"
    assert "Conflict detected" in data["error"]


# =============================================================================
# Agentic Behavior & Orchestration (Tests 25-30)
# =============================================================================

def test_orchestrator_routes_pathway_discovery():
    """25. Orchestrator routes pathway discovery queries to OpportunityPathwayAgent."""
    orch = AgentOrchestrator()
    queries = [
        "pathways for me",
        "what careers can I explore?",
        "I don't know what career to choose"
    ]
    for q in queries:
        res = orch.route_request(q, {})
        assert res["intent"] == "pathway_discovery"
        assert res["agent_used"] == "OpportunityPathwayAgent"
        assert "OpportunityPathwayAgent" in res["agents_executed"]
        assert res["status"] == "success"


def test_orchestrator_routes_pathway_analysis():
    """26. Orchestrator routes pathway analysis queries to PathwayAnalysisAgent."""
    orch = AgentOrchestrator()
    queries = [
        "analyze my selected pathway",
        "pathway fit",
        "check my pathway"
    ]
    for q in queries:
        res = orch.route_request(q, {
            "selected_pathway": {"id": "cloud-devops", "name": "Cloud Architecture & DevOps"},
            "student_profile": {"skills": ["Python"]}
        })
        assert res["intent"] == "pathway_fit"
        assert res["agent_used"] == "PathwayAnalysisAgent"
        assert "PathwayAnalysisAgent" in res["agents_executed"]
        assert res["status"] == "success"


def test_orchestrator_routes_planner():
    """27. Orchestrator routes action planning queries to PlannerAgent."""
    orch = AgentOrchestrator()
    queries = [
        "create my action plan",
        "what should I do next?"
    ]
    for q in queries:
        res = orch.route_request(q, {"target_role": "DevOps Engineer"})
        assert res["intent"] == "planner"
        assert res["agent_used"] == "PlannerAgent"
        assert "PlannerAgent" in res["agents_executed"]
        assert res["status"] == "success"


def test_orchestrator_routes_roadmap(app):
    """28. Orchestrator routes roadmap queries to RoadmapAgent."""
    orch = AgentOrchestrator()
    with app.app_context():
        queries = [
            "show my roadmap",
            "show my career journey"
        ]
        for q in queries:
            res = orch.route_request(q, {"student_id": 1, "target_role": "Software Engineer"})
            assert res["intent"] == "roadmap"
            assert res["agent_used"] == "RoadmapAgent"
            assert "RoadmapAgent" in res["agents_executed"]
            assert res["status"] == "success"


def test_orchestrator_multi_agent_sequence_execution(app):
    """29. Orchestrator executes coordinated multi-agent workflow across specialized agents."""
    orch = AgentOrchestrator()
    with app.app_context():
        context = {
            "student_id": 1,
            "target_role": "Cloud Architecture & DevOps",
            "selected_pathway": {
                "id": "cloud-devops",
                "name": "Cloud Architecture & DevOps",
                "industry_sector": "Technology"
            },
            "current_skills": ["Python", "Linux"],
            "target_skills": ["Linux", "Docker", "Kubernetes", "AWS"]
        }
        res = orch.route_request("How do I transition to Cloud Architecture & DevOps?", context)
        assert res["status"] == "success"
        assert res["intent"] == "comprehensive_guidance"
        assert "MultiAgentCoordination" in res["agent_used"]
        assert len(res["agents_executed"]) >= 3
        assert "PlannerAgent" in res["agents_executed"]
        assert "RoadmapAgent" in res["agents_executed"]
        assert res["result"] is not None


def test_orchestrator_agents_executed_information(app):
    """30. Agent execution metadata is accurate and truthful."""
    orch = AgentOrchestrator()
    with app.app_context():
        context = {
            "student_id": 1,
            "target_role": "Data Scientist",
            "current_skills": ["Python", "SQL"]
        }
        res = orch.route_request("How do I become a Data Scientist?", context)
        assert "agents_executed" in res
        assert isinstance(res["agents_executed"], list)
        assert "SkillGapAgent" in res["agents_executed"]
        assert "PlannerAgent" in res["agents_executed"]
        assert "RoadmapAgent" in res["agents_executed"]
        assert "explanation" in res
        assert "recommended_next_action" in res


# =============================================================================
# Regression & Health Verification (Tests 31-32)
# =============================================================================

def test_regression_all_health_endpoints(client):
    """31. All modular component health endpoints are fully functional."""
    health_endpoints = [
        '/api/profile/health',
        '/api/career/health',
        '/api/education/health',
        '/api/opportunities/health',
        '/api/eligibility/health',
        '/api/skill-gap/health',
        '/api/planner/health',
        '/api/notifications/health',
        '/api/agents/health'
    ]
    for ep in health_endpoints:
        res = client.get(ep)
        assert res.status_code == 200, f"Health endpoint {ep} failed with status {res.status_code}"
        data = res.get_json()
        assert data["status"] == "healthy", f"Endpoint {ep} returned non-healthy status: {data}"


def test_regression_page_routes_load_cleanly(client):
    """32. All UI page routes render without errors."""
    page_routes = [
        '/',
        '/career-direction',
        '/career-discovery',
        '/pathway-discovery',
        '/pathway-analysis',
        '/planner',
        '/roadmap',
        '/api/agents/demo'
    ]
    for route in page_routes:
        res = client.get(route)
        assert res.status_code == 200, f"UI route {route} failed with status {res.status_code}"
        assert len(res.data) > 0


def test_exact_lawyer_to_exploring_workflow_bug_reproduction(client):
    """
    33. Specifically verify the user-reported scenario:
    1. Choose known target 'Lawyer'
    2. Switch to 'I\'m still exploring'
    3. Complete exploration profile (Class 10, Communication, Education)
    4. Open pathway discovery
    5. Confirm 'Lawyer' is completely absent from declared goal/title/pathways unless explicitly selected
    6. Confirm multiple pathways are displayed for exploration
    7. Select one pathway (Education & Academic Teaching)
    8. Confirm only the selected pathway proceeds to Eligibility -> Skill Gap -> Planner -> Roadmap
    9. Verify no stale state remains
    """
    # 1. Known target 'Lawyer'
    res_known = client.post('/api/career/direction', json={
        "career_direction": "known",
        "target_role": "Lawyer"
    })
    assert res_known.status_code == 200
    assert res_known.get_json()["target_role"] == "Lawyer"

    # 2. Switch to "I'm still exploring"
    res_exploring = client.post('/api/career/direction', json={
        "career_direction": "exploring"
    })
    assert res_exploring.status_code == 200
    assert res_exploring.get_json()["career_direction"] == "exploring"
    assert res_exploring.get_json()["target_role"] is None

    # 3. Complete exploration profile
    res_prof = client.post('/api/profile/discovery', json={
        "education_level": "Class 10",
        "skills": ["Communication"],
        "interests": ["Education"],
        "work_preferences": ["Working with people"],
        "career_preferences": ["Open to multiple options"]
    })
    assert res_prof.status_code == 200
    assert res_prof.get_json()["target_role"] is None

    # 4. Open pathway discovery
    res_pathways = client.get('/api/career/pathways', headers=JSON_HEADERS)
    assert res_pathways.status_code == 200
    p_data = res_pathways.get_json()

    # 5. Confirm "Lawyer" is absent from target_role & multiple pathways returned
    assert p_data["career_direction"] == "exploring"
    assert p_data["target_role"] is None
    assert p_data["total_pathways"] >= 2
    pathway_names = [p["name"] for p in p_data["pathways"]]
    assert "Lawyer" not in pathway_names
    assert "Education & Academic Teaching" in pathway_names

    # 6. Select Education pathway
    res_select = client.post('/api/career/pathways/select', json={
        "pathway_id": "education-teaching",
        "pathway_name": "Education & Academic Teaching"
    })
    assert res_select.status_code == 200
    assert res_select.get_json()["selected_pathway"]["name"] == "Education & Academic Teaching"

    # 7. Pathway fit analysis receives ONLY the selected pathway
    res_fit = client.get('/api/career/pathways/analysis', headers=JSON_HEADERS)
    assert res_fit.status_code == 200
    fit_data = res_fit.get_json()
    assert fit_data["status"] == "success"
    assert fit_data["selected_pathway"]["id"] == "education-teaching"
    assert fit_data["target_role"] == "Education & Academic Teaching"

    # 8. Create action plan using selected pathway
    res_plan = client.post('/api/career/pathways/action-plan', json={"student_id": 1})
    assert res_plan.status_code in (200, 201)
    plan_data = res_plan.get_json()
    assert plan_data["target_role"] == "Education & Academic Teaching"
    assert plan_data["total_milestones"] > 0
    assert "Lawyer" not in str(plan_data)

    # 9. Synthesize roadmap using selected pathway
    res_roadmap = client.get('/api/planner/roadmap/1', headers=JSON_HEADERS)
    assert res_roadmap.status_code == 200
    roadmap_data = res_roadmap.get_json()
    assert roadmap_data["career_goal"] == "Education & Academic Teaching"
    assert "Lawyer" not in str(roadmap_data)

