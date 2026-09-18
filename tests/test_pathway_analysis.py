import pytest
from app import create_app
from db import db
from career.services import CareerDirectionService, PathwayDiscoveryService, PathwayAnalysisService
from eligibility.services import EligibilityService
from skill_gap.services import SkillGapService
from agents.orchestrator import AgentOrchestrator
from agents.specialized_agents import PathwayAnalysisAgent


@pytest.fixture
def app():
    """Create test application context with in-memory SQLite database."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# =============================================================================
# Unit Tests for PathwayAnalysisService
# =============================================================================

def test_selected_pathway_fit_analysis_exploring_student():
    """Verify combined eligibility + skill gap fit analysis for exploring student who selected a pathway."""
    session_dict = {}
    
    # 1. Simulate exploration profile in session
    session_dict["career_direction"] = "exploring"
    session_dict["exploration_profile"] = {
        "education_level": "Bachelor of Technology",
        "skills": ["Python", "Problem Solving", "Git"],
        "interests": ["Technology"],
        "subjects": ["Computer Science"]
    }
    
    # 2. Select Software Engineering pathway
    PathwayDiscoveryService.select_pathway("software-engineering", session_obj=session_dict)
    
    # 3. Analyze pathway fit
    result = PathwayAnalysisService.analyze_pathway_fit(session_obj=session_dict)
    
    assert result["status"] == "success"
    assert result["analysis_status"] == "complete"
    assert result["career_direction"] == "exploring"
    assert result["selected_pathway"]["id"] == "software-engineering"
    assert result["selected_pathway"]["name"] == "Software Engineering"
    
    # Verify Eligibility Engine was reused and evaluated
    assert "eligibility" in result
    assert result["eligibility"]["status"] in ("ELIGIBLE", "NOT_ELIGIBLE", "NEEDS_VERIFICATION")
    assert len(result["eligibility"]["satisfied_criteria"]) > 0
    
    # Verify Skill Gap Engine was reused and evaluated
    assert "skill_gap" in result
    assert "match_rate" in result["skill_gap"]
    assert "Problem Solving" in result["skill_gap"]["matching_skills"] or "Git" in result["skill_gap"]["matching_skills"]
    assert result["next_step"] == "Continue to Personalized Action Plan"
    assert "factual_summary" in result
    assert "perfect" not in result["factual_summary"].lower()
    assert "best career" not in result["factual_summary"].lower()


def test_selected_pathway_fit_analysis_known_target_student():
    """Verify known-target student pathway analysis works consistently."""
    session_dict = {}
    CareerDirectionService.set_direction("known", target_role="Doctor", session_obj=session_dict)
    
    # Analyze pathway fit without explicit prior selection (auto-resolves consistent pathway)
    result = PathwayAnalysisService.analyze_pathway_fit(session_obj=session_dict)
    
    assert result["status"] == "success"
    assert result["career_direction"] == "known"
    assert result["selected_pathway"]["id"] == "healthcare-medicine"
    assert "eligibility" in result
    assert "skill_gap" in result


def test_no_selected_pathway_handled_safely():
    """Verify exploring student with no selected pathway receives safe clarification without crashing."""
    session_dict = {
        "career_direction": "exploring",
        "exploration_profile": {
            "education_level": "Bachelor's",
            "skills": ["Python"],
            "interests": ["Technology"]
        }
    }
    
    result = PathwayAnalysisService.analyze_pathway_fit(session_obj=session_dict)
    
    assert result["status"] == "clarification_needed"
    assert result["is_selected"] is False
    assert result["selected_pathway"] is None
    assert "select a career pathway" in result["message"].lower()


def test_missing_profile_information_handled_safely():
    """Verify empty student profile produces explainable NEEDS_VERIFICATION status."""
    session_dict = {
        "career_direction": "exploring",
        "exploration_profile": {}
    }
    PathwayDiscoveryService.select_pathway("cloud-devops", session_obj=session_dict)
    
    result = PathwayAnalysisService.analyze_pathway_fit(session_obj=session_dict)
    
    assert result["status"] == "success"
    # Empty education produces NEEDS_VERIFICATION in EligibilityEngine
    assert result["eligibility"]["status"] == "NEEDS_VERIFICATION"
    assert len(result["eligibility"]["unverified_criteria"]) > 0
    assert result["skill_gap"]["match_rate"] == 0.0


def test_target_pathway_conflict_detection():
    """Verify conflict between declared target role and selected pathway is detected."""
    # Conflict: Target is Doctor, but selected pathway is Civil Engineering
    is_conflict, msg = PathwayAnalysisService.check_target_pathway_conflict(
        target_role="Doctor",
        pathway={"id": "civil-engineering", "name": "Civil & Infrastructure Engineering", "industry_sector": "Engineering"}
    )
    assert is_conflict is True
    assert "Conflict detected" in msg
    assert "Doctor" in msg

    # Non-conflict: Target Doctor with Healthcare pathway
    no_conflict, _ = PathwayAnalysisService.check_target_pathway_conflict(
        target_role="Doctor",
        pathway={"id": "healthcare-medicine", "name": "Medicine & Healthcare", "industry_sector": "Healthcare"}
    )
    assert no_conflict is False


def test_analyze_fit_detects_conflict_in_state():
    """Verify analyze_pathway_fit returns conflict status when target_role and selected_pathway mismatch."""
    session_dict = {
        "career_direction": "known",
        "target_role": "Doctor",
        "selected_pathway": {
            "id": "software-engineering",
            "name": "Software Engineering",
            "industry_sector": "Technology"
        }
    }
    result = PathwayAnalysisService.analyze_pathway_fit(session_obj=session_dict)
    assert result["status"] == "conflict_detected"
    assert "Conflict detected" in result["error"]


def test_custom_payload_direct_analysis():
    """Verify analyze_pathway_fit on direct custom context payload."""
    payload = {
        "career_direction": "exploring",
        "student_profile": {
            "education_level": "Bachelor of Technology",
            "degree": "Computer Science",
            "skills": ["Linux", "Docker", "Kubernetes", "AWS", "Programming", "Problem Solving"]
        },
        "selected_pathway": {
            "id": "cloud-devops",
            "name": "Cloud Architecture & DevOps",
            "industry_sector": "Technology"
        }
    }
    
    result = PathwayAnalysisService.analyze_pathway_fit(context=payload)
    
    assert result["status"] == "success"
    assert result["eligibility"]["status"] in ("ELIGIBLE", "NEEDS_VERIFICATION")
    assert result["skill_gap"]["match_rate"] > 70.0
    assert result["skill_gap"]["gap_percentage"] < 30.0


# =============================================================================
# Agent & Orchestrator Integration Tests
# =============================================================================

def test_pathway_analysis_agent_direct_execution():
    """Verify PathwayAnalysisAgent processes input and returns structured schema."""
    agent = PathwayAnalysisAgent()
    assert agent.agent_name == "PathwayAnalysisAgent"
    
    task_input = {
        "career_direction": "known",
        "target_role": "Software Engineer",
        "student_profile": {
            "education_level": "Bachelor of Technology",
            "skills": ["Programming", "Problem Solving", "Git", "Databases"]
        },
        "selected_pathway": {
            "id": "software-engineering",
            "name": "Software Engineering"
        }
    }
    res = agent.process_task(task_input)
    assert res["status"] == "success"
    assert res["agent"] == "PathwayAnalysisAgent"
    assert "data" in res
    assert "explanation" in res
    assert "Software Engineering" in res["explanation"]


def test_orchestrator_pathway_fit_intent_detection():
    """Verify AgentOrchestrator detects pathway_fit intent from query and context."""
    orch = AgentOrchestrator()
    
    # Query detection
    assert orch.detect_intent("Analyze my selected Cloud Engineer pathway") == "pathway_fit"
    assert orch.detect_intent("Analyze my Doctor pathway") == "pathway_fit"
    assert orch.detect_intent("Please evaluate my selected pathway fit") == "pathway_fit"
    assert orch.detect_intent(None, context={"intent": "pathway_fit"}) == "pathway_fit"
    assert orch.detect_intent(None, context={"intent": "pathway_analysis"}) == "pathway_fit"


def test_orchestrator_routes_selected_pathway_analysis(client):
    """Verify Orchestrator routes pathway fit analysis request with natural language."""
    orch = AgentOrchestrator()
    
    context = {
        "career_direction": "exploring",
        "student_profile": {
            "education_level": "Bachelor's",
            "skills": ["Python", "Problem Solving"]
        },
        "selected_pathway": {
            "id": "software-engineering",
            "name": "Software Engineering"
        }
    }
    
    routed = orch.route_request("Analyze my selected Software Engineering pathway", context=context)
    
    assert routed["status"] == "success"
    assert routed["intent"] == "pathway_fit"
    assert routed["agent_used"] == "PathwayAnalysisAgent"
    assert routed["result"] is not None
    assert routed["result"]["selected_pathway"]["name"] == "Software Engineering"
    assert "Action Plan" in routed["recommended_next_action"]


def test_orchestrator_routes_unselected_pathway_to_safe_clarification():
    """Verify Orchestrator returns clarification when no pathway is selected."""
    orch = AgentOrchestrator()
    
    context = {
        "career_direction": "exploring",
        "student_profile": {"education_level": "Bachelor's", "skills": ["Python"]}
    }
    
    routed = orch.route_request("Analyze my selected pathway", context=context)
    
    assert routed["status"] == "clarification_needed"
    assert routed["intent"] == "pathway_fit"
    assert "select a career pathway" in routed["explanation"].lower()


# =============================================================================
# REST API and Route Layer Tests
# =============================================================================

def test_api_get_pathway_analysis_html_page_loads(client):
    """Verify GET /pathway-analysis loads the HTML page."""
    res = client.get('/pathway-analysis')
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Pathway Fit" in html
    assert "Eligibility Evaluation" in html
    assert "Skill Gap Analysis" in html
    assert "Step 4: Pathway Fit Analysis" in html


def test_api_get_pathway_analysis_json(client):
    """Verify GET /api/career/pathways/analysis returns JSON payload."""
    with client.session_transaction() as sess:
        sess["career_direction"] = "exploring"
        sess["exploration_profile"] = {
            "education_level": "Bachelor of Technology",
            "skills": ["Python", "Problem Solving"]
        }
        sess["selected_pathway"] = {
            "id": "software-engineering",
            "name": "Software Engineering",
            "industry_sector": "Technology"
        }
    
    res = client.get('/api/career/pathways/analysis', headers={'Accept': 'application/json'})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["selected_pathway"]["id"] == "software-engineering"
    assert "eligibility" in data
    assert "skill_gap" in data


def test_api_post_analyze_pathway_fit(client):
    """Verify POST /api/career/pathways/analyze executes fit evaluation."""
    payload = {
        "career_direction": "known",
        "target_role": "Cloud Architect",
        "student_profile": {
            "education_level": "Bachelor of Technology",
            "skills": ["Linux", "Docker", "AWS", "Python"]
        },
        "selected_pathway": {
            "id": "cloud-devops",
            "name": "Cloud Architecture & DevOps",
            "industry_sector": "Technology"
        }
    }
    
    res = client.post('/api/career/pathways/analyze', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["selected_pathway"]["name"] == "Cloud Architecture & DevOps"
    assert data["skill_gap"]["match_rate"] > 0


def test_eligibility_engine_is_reused():
    """Verify EligibilityService.check_eligibility is directly utilized and returns expected criteria."""
    student = {"education_level": "Bachelor's", "skills": ["Python"]}
    opp = {"min_education": "Bachelor's", "required_skills": ["Python"]}
    direct_res = EligibilityService.check_eligibility(student, opp)
    
    context = {
        "student_profile": student,
        "selected_pathway": {
            "id": "custom",
            "name": "Custom",
            "requirements": opp
        }
    }
    fit_res = PathwayAnalysisService.analyze_pathway_fit(context=context)
    
    assert fit_res["eligibility"]["status"] == direct_res["status"]
    assert fit_res["eligibility"]["satisfied_criteria"] == direct_res["satisfied_criteria"]


def test_skill_gap_engine_is_reused():
    """Verify SkillGapService.analyze_gap is directly utilized and returns expected match calculations."""
    curr = ["Python", "Flask"]
    req = ["Python", "Flask", "Docker", "AWS"]
    direct_gap = SkillGapService.analyze_gap(curr, req)
    
    context = {
        "student_profile": {"skills": curr, "education_level": "Bachelor's"},
        "selected_pathway": {
            "id": "custom",
            "name": "Custom",
            "requirements": {"required_skills": req, "min_education": "Bachelor's"}
        }
    }
    fit_res = PathwayAnalysisService.analyze_pathway_fit(context=context)
    
    assert fit_res["skill_gap"]["match_rate"] == direct_gap["match_rate"]
    assert fit_res["skill_gap"]["matching_skills"] == direct_gap["matching_skills"]
    assert fit_res["skill_gap"]["missing_skills"] == direct_gap["missing_skills"]


def test_eligibility_status_validity():
    """Verify eligibility status remains strictly one of ELIGIBLE, NOT_ELIGIBLE, NEEDS_VERIFICATION."""
    for edu in ["Bachelor's", "High School", None]:
        context = {
            "student_profile": {"education_level": edu, "skills": ["Python"]},
            "selected_pathway": {"id": "software-engineering", "name": "Software Engineering"}
        }
        res = PathwayAnalysisService.analyze_pathway_fit(context=context)
        assert res["eligibility"]["status"] in ("ELIGIBLE", "NOT_ELIGIBLE", "NEEDS_VERIFICATION")


def test_all_health_endpoints_remain_functional(client):
    """Verify all health check endpoints across modules remain healthy."""
    endpoints = [
        "/api/career/health",
        "/api/eligibility/health",
        "/api/skill-gap/health",
        "/api/planner/health",
        "/api/agents/health"
    ]
    for ep in endpoints:
        res = client.get(ep)
        assert res.status_code == 200
        data = res.get_json()
        assert data.get("status") == "healthy"

