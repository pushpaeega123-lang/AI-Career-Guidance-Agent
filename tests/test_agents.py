import pytest
from agents.orchestrator import AgentOrchestrator
from agents.specialized_agents import (
    EligibilityAgent,
    PlannerAgent,
    RoadmapAgent,
    SkillGapAgent,
)
from db import db
from profile.models import StudentProfile


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def agent_student(app):
    """Create a sample student profile in test DB for agent testing."""
    with app.app_context():
        student = StudentProfile(
            full_name="Marcus Vance",
            email="marcus.vance@example.com",
            education_level="Bachelor of Science"
        )
        db.session.add(student)
        db.session.commit()
        return student.id


# =============================================================================
# Unit Tests for Specialized Agents
# =============================================================================

def test_eligibility_agent_execution():
    """Verify EligibilityAgent processes task and produces structured response."""
    agent = EligibilityAgent()
    task_input = {
        "student_profile": {"education_level": "Bachelor's", "skills": ["Python"]},
        "opportunity": {"min_education": "Bachelor's", "required_skills": ["Python"]}
    }
    result = agent.process_task(task_input)
    assert result["status"] == "success"
    assert result["agent"] == "EligibilityAgent"
    assert result["data"]["status"] == "ELIGIBLE"
    assert "explanation" in result


def test_skill_gap_agent_execution():
    """Verify SkillGapAgent processes task and produces match metrics."""
    agent = SkillGapAgent()
    task_input = {
        "current_skills": ["Python", "SQL"],
        "target_skills": ["Python", "SQL", "Docker", "Kubernetes"]
    }
    result = agent.process_task(task_input)
    assert result["status"] == "success"
    assert result["agent"] == "SkillGapAgent"
    assert result["data"]["match_rate"] == 50.0
    assert result["data"]["gap_percentage"] == 50.0
    assert len(result["data"]["missing_skills"]) == 2


def test_planner_agent_execution_with_and_without_student(app, agent_student):
    """Verify PlannerAgent generates milestones with standalone and persistent modes."""
    agent = PlannerAgent()

    # Standalone mode (no student_id)
    res_standalone = agent.process_task({
        "target_role": "Backend Engineer",
        "current_skills": ["Python"]
    })
    assert res_standalone["status"] == "success"
    assert res_standalone["data"]["total_milestones"] > 0
    assert res_standalone["data"]["student_id"] is None

    # Persistent mode (with valid student_id in DB context)
    with app.app_context():
        res_persisted = agent.process_task({
            "student_id": agent_student,
            "target_role": "DevOps Engineer"
        })
        assert res_persisted["status"] == "success"
        assert res_persisted["data"]["student_id"] == agent_student
        assert res_persisted["data"]["id"] is not None


def test_roadmap_agent_execution(app, agent_student):
    """Verify RoadmapAgent synthesizes 6-stage roadmap for student."""
    agent = RoadmapAgent()
    with app.app_context():
        result = agent.process_task({
            "student_id": agent_student,
            "target_role": "AI Engineer"
        })
        assert result["status"] == "success"
        assert result["agent"] == "RoadmapAgent"
        assert len(result["data"]["stages"]) == 6


# =============================================================================
# Unit Tests for AgentOrchestrator
# =============================================================================

def test_orchestrator_intent_detection():
    """Verify deterministic intent detection across explicit and keyword queries."""
    orch = AgentOrchestrator()

    # Explicit intent in context
    assert orch.detect_intent(None, {"intent": "eligibility"}) == "eligibility"
    assert orch.detect_intent(None, {"intent": "skill_gap"}) == "skill_gap"
    assert orch.detect_intent(None, {"intent": "planner"}) == "planner"
    assert orch.detect_intent(None, {"intent": "roadmap"}) == "roadmap"

    # Natural language keyword queries
    assert orch.detect_intent("Am I eligible for this job opportunity?") == "eligibility"
    assert orch.detect_intent("What is my skill gap for software engineer?") == "skill_gap"
    assert orch.detect_intent("Create an action plan and milestones for me") == "planner"
    assert orch.detect_intent("Show me my full career roadmap") == "roadmap"
    assert orch.detect_intent("How do I become a Data Scientist?") == "comprehensive_guidance"

    # Ambiguous / unclear
    assert orch.detect_intent("Hello") == "clarification"
    assert orch.detect_intent("") == "clarification"
    assert orch.detect_intent(None) == "clarification"


def test_orchestrator_route_single_agents(app, agent_student):
    """Verify orchestrator routes to each individual agent correctly."""
    orch = AgentOrchestrator()

    # 1. Eligibility
    res_elig = orch.route_request("Check eligibility", {
        "student_profile": {"education_level": "Bachelor's"},
        "opportunity": {"min_education": "Bachelor's"}
    })
    assert res_elig["intent"] == "eligibility"
    assert res_elig["agent_used"] == "EligibilityAgent"
    assert res_elig["status"] == "success"

    # 2. Skill Gap
    res_sg = orch.route_request("Analyze skill gap", {
        "current_skills": ["Python"],
        "target_skills": ["Python", "Docker"]
    })
    assert res_sg["intent"] == "skill_gap"
    assert res_sg["agent_used"] == "SkillGapAgent"
    assert res_sg["status"] == "success"

    # 3. Planner
    res_plan = orch.route_request("Generate action plan", {
        "target_role": "Frontend Developer"
    })
    assert res_plan["intent"] == "planner"
    assert res_plan["agent_used"] == "PlannerAgent"
    assert res_plan["status"] == "success"

    # 4. Roadmap
    with app.app_context():
        res_rm = orch.route_request("Show career roadmap", {
            "student_id": agent_student
        })
        assert res_rm["intent"] == "roadmap"
        assert res_rm["agent_used"] == "RoadmapAgent"
        assert res_rm["status"] == "success"


def test_orchestrator_clarification_response():
    """Verify unclear request returns structured clarification response."""
    orch = AgentOrchestrator()
    res = orch.route_request("Hello!", {})
    assert res["intent"] == "clarification"
    assert res["status"] == "clarification_needed"
    assert res["result"] is None
    assert "Please specify" in res["explanation"]


def test_orchestrator_multi_agent_workflow(app, agent_student):
    """Verify multi-agent workflow coordinates SkillGap, Planner, and Roadmap agents."""
    orch = AgentOrchestrator()

    with app.app_context():
        res = orch.route_request("How do I become a Cloud Engineer?", {
            "student_id": agent_student,
            "target_role": "Cloud Engineer",
            "current_skills": ["Linux", "Bash"],
            "target_skills": ["Linux", "Bash", "Docker", "Kubernetes", "AWS"]
        })

        assert res["intent"] == "comprehensive_guidance"
        assert "MultiAgentCoordination" in res["agent_used"]
        assert res["status"] == "success"

        result = res["result"]
        assert "skill_gap" in result
        assert "action_plan" in result
        assert "roadmap" in result
        assert result["skill_gap"]["match_rate"] > 0
        assert result["action_plan"]["total_milestones"] > 0
        assert len(result["roadmap"]["stages"]) == 6


def test_orchestrator_agent_failure_handling():
    """Verify orchestrator catches agent execution errors safely."""
    orch = AgentOrchestrator()

    # Planner without target_role
    res = orch.route_request(None, {"intent": "planner"})
    assert res["status"] == "error"
    assert len(res["errors"]) > 0


# =============================================================================
# API Route Integration Tests
# =============================================================================

def test_api_agents_health(client):
    """Verify GET /api/agents/health endpoint."""
    response = client.get('/api/agents/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["module"] == "agent_orchestrator"


def test_api_agents_orchestrate_success(client, agent_student):
    """Verify POST /api/agents/orchestrate endpoint."""
    payload = {
        "query": "How do I transition to a DevOps Engineer?",
        "context": {
            "student_id": agent_student,
            "target_role": "DevOps Engineer",
            "current_skills": ["Linux", "Python"]
        }
    }
    response = client.post('/api/agents/orchestrate', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] in ("success", "partial_success")
    assert "explanation" in data
    assert "result" in data


def test_api_agents_orchestrate_invalid_body(client):
    """Verify POST /api/agents/orchestrate with non-json returns 400."""
    response = client.post('/api/agents/orchestrate', data="not json", content_type="text/plain")
    assert response.status_code == 400


def test_api_agents_demo_route(client):
    """Verify GET /api/agents/demo renders assistant template."""
    response = client.get('/api/agents/demo')
    assert response.status_code == 200
    assert b"Intelligent Career Agent Assistant" in response.data
