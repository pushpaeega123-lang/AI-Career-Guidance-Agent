import pytest
from career.services import PathwayDiscoveryService
from agents.orchestrator import AgentOrchestrator
from agents.specialized_agents import OpportunityPathwayAgent


# =============================================================================
# Unit Tests for PathwayDiscoveryService Logic
# =============================================================================

def test_discovery_exploring_with_profile():
    """Verify exploring student receives explainable pathways matching profile evidence."""
    profile = {
        "education_level": "Undergraduate",
        "subjects": ["Computer Science", "Mathematics"],
        "skills": ["Programming", "Problem Solving"],
        "interests": ["Technology"],
        "work_preferences": ["Working with technology"],
        "career_preferences": ["Private sector"]
    }
    result = PathwayDiscoveryService.discover_pathways({
        "career_direction": "exploring",
        "student_profile": profile
    })
    assert result["status"] == "success"
    assert result["career_direction"] == "exploring"
    assert result["total_pathways"] > 0
    pathways = result["pathways"]
    
    # Software Engineering should be top ranked
    top_pathway = pathways[0]
    assert top_pathway["name"] in ("Software Engineering", "Data Science & Analytics", "Cloud Architecture & DevOps")
    assert "Programming" in str(top_pathway["why_relevant"]) or "Technology" in str(top_pathway["why_relevant"])
    assert "best career" not in top_pathway["why_relevant"].lower()


def test_discovery_known_target_standard_role():
    """Verify known-target student receives targeted pathway details."""
    result = PathwayDiscoveryService.discover_pathways({
        "career_direction": "known",
        "target_role": "Doctor"
    })
    assert result["status"] == "success"
    assert result["career_direction"] == "known"
    assert result["target_role"] == "Doctor"
    assert len(result["pathways"]) == 1
    p = result["pathways"][0]
    assert p["name"] == "Medicine & Healthcare"
    assert "MBBS" in p["education_pathway"]
    assert len(p["sources"]) > 0


def test_discovery_known_target_custom_role():
    """Verify known-target student with unlisted role receives structured pathway without fabricated facts."""
    result = PathwayDiscoveryService.discover_pathways({
        "career_direction": "known",
        "target_role": "Robotics Specialist"
    })
    assert result["status"] == "success"
    assert result["career_direction"] == "known"
    assert result["target_role"] == "Robotics Specialist"
    assert len(result["pathways"]) == 1
    p = result["pathways"][0]
    assert p["name"] == "Robotics Specialist"
    assert "Robotics Specialist" in p["why_relevant"]
    assert len(p["sources"]) > 0


def test_discovery_empty_profile_fallback():
    """Verify empty exploration profile safely returns zero-match state with guidance, not a static list."""
    result = PathwayDiscoveryService.discover_pathways({
        "career_direction": "exploring",
        "student_profile": {}
    })
    assert result["status"] == "success"
    assert result["total_pathways"] == 0
    assert result["pathways"] == []
    assert "add more" in result.get("message", "").lower()


def test_discovery_profile_a_education_people():
    """Test A: Profile with Education interest, Communication skill, and Working with people preference."""
    profile = {
        "education_level": "Class 10",
        "skills": ["Communication"],
        "interests": ["Education"],
        "work_preferences": ["Working with people"],
        "career_preferences": ["Open to multiple options"]
    }
    result = PathwayDiscoveryService.discover_pathways({
        "career_direction": "exploring",
        "student_profile": profile
    })
    assert result["status"] == "success"
    assert result["total_pathways"] > 0
    names = [p["name"] for p in result["pathways"]]
    
    # Relevant pathways must include education or public administration
    assert "Education & Academic Teaching" in names or "Public Administration & Civil Services" in names
    
    # Top pathway check
    top_p = result["pathways"][0]
    assert "Education" in top_p["matched_interests"] or "Communication" in top_p["matched_skills"] or "Working with people" in top_p["matched_work_prefs"]
    # Explanations must contain actual matched evidence
    assert "Communication" in top_p["why_relevant"] or "Education" in top_p["why_relevant"] or "Working with people" in top_p["why_relevant"]
    # No zero-match pathway allowed
    for p in result["pathways"]:
        assert (p.get("matched_skills") or p.get("matched_interests") or p.get("matched_subjects") or p.get("matched_work_prefs"))


def test_discovery_profile_b_technology():
    """Test B: Profile with Technology interest, Coding & Mathematics skills, and Working with technology preference."""
    profile = {
        "education_level": "Class 10",
        "skills": ["Mathematics", "Coding"],
        "interests": ["Technology"],
        "work_preferences": ["Working with technology"],
        "career_preferences": ["Private sector"]
    }
    result = PathwayDiscoveryService.discover_pathways({
        "career_direction": "exploring",
        "student_profile": profile
    })
    assert result["status"] == "success"
    assert result["total_pathways"] > 0
    names = [p["name"] for p in result["pathways"]]
    
    # Tech pathways must be discovered
    assert "Software Engineering" in names or "Data Science & Analytics" in names
    top_p = result["pathways"][0]
    assert top_p["name"] in ("Software Engineering", "Data Science & Analytics", "Cloud Architecture & DevOps")
    assert "Coding" in top_p["matched_skills"] or "Mathematics" in top_p["matched_skills"] or "Technology" in top_p["matched_interests"]


def test_discovery_profile_c_healthcare():
    """Test C: Profile with Healthcare interest, Biology & Communication skills, and Helping people preference."""
    profile = {
        "education_level": "Class 10",
        "skills": ["Biology", "Communication"],
        "interests": ["Healthcare"],
        "work_preferences": ["Helping people"]
    }
    result = PathwayDiscoveryService.discover_pathways({
        "career_direction": "exploring",
        "student_profile": profile
    })
    assert result["status"] == "success"
    assert result["total_pathways"] > 0
    names = [p["name"] for p in result["pathways"]]
    
    # Healthcare pathways must be discovered
    assert "Medicine & Healthcare" in names or "Nursing & Allied Health" in names
    top_p = result["pathways"][0]
    assert top_p["name"] in ("Medicine & Healthcare", "Nursing & Allied Health")
    assert "Healthcare" in top_p["matched_interests"] or "Biology" in top_p["matched_skills"] or "Helping people" in top_p["matched_work_prefs"]


def test_discovery_profile_d_no_matching_evidence():
    """Test D: Insufficient or irrelevant matching evidence returns safe zero-match state."""
    profile = {
        "education_level": "Class 10",
        "skills": ["UnrelatedSkillX", "UnknownThingY"],
        "interests": ["RandomZ"],
        "work_preferences": ["None"]
    }
    result = PathwayDiscoveryService.discover_pathways({
        "career_direction": "exploring",
        "student_profile": profile
    })
    assert result["status"] == "success"
    assert result["total_pathways"] == 0
    assert result["pathways"] == []
    assert "add more" in result.get("message", "").lower()


def test_discovery_profile_e_explanation_evidence_correctness():
    """Test E: All returned pathway evidence arrays match submitted profile values."""
    profile = {
        "education_level": "Undergraduate",
        "subjects": ["Physics", "Mathematics"],
        "skills": ["Data Analysis", "Python"],
        "interests": ["Finance", "Technology"],
        "work_preferences": ["Analyzing data", "Solving problems"],
        "career_preferences": ["Private sector"]
    }
    result = PathwayDiscoveryService.discover_pathways({
        "career_direction": "exploring",
        "student_profile": profile
    })
    assert result["status"] == "success"
    assert result["total_pathways"] > 0
    
    for p in result["pathways"]:
        # All matched skills must be in profile skills
        for s in p.get("matched_skills", []):
            assert s in profile["skills"]
        # All matched interests must be in profile interests
        for i in p.get("matched_interests", []):
            assert i in profile["interests"]
        # All matched subjects must be in profile subjects
        for sub in p.get("matched_subjects", []):
            assert sub in profile["subjects"]
        # All matched work prefs must be in profile work_preferences
        for w in p.get("matched_work_prefs", []):
            assert w in profile["work_preferences"]
        # Explanation must be grounded in matched signals
        assert "matched" in p["why_relevant"].lower() or any(term in p["why_relevant"] for term in profile["skills"] + profile["interests"])


def test_profile_sensitivity_changing_requirements_changes_recommendations():
    """Test Section 11: Changing the student profile genuinely changes the discovered pathways, scores, and explanations."""
    # Profile A: Education & People
    profile_a = {
        "education_level": "Class 10",
        "skills": ["Communication"],
        "interests": ["Education"],
        "work_preferences": ["Working with people"]
    }
    res_a = PathwayDiscoveryService.discover_pathways({
        "career_direction": "exploring",
        "student_profile": profile_a
    })

    # Profile B: Tech & Coding
    profile_b = {
        "education_level": "Class 10",
        "skills": ["Coding", "Mathematics"],
        "interests": ["Technology"],
        "work_preferences": ["Working with technology"]
    }
    res_b = PathwayDiscoveryService.discover_pathways({
        "career_direction": "exploring",
        "student_profile": profile_b
    })

    # Profile C: Healthcare & Biology
    profile_c = {
        "education_level": "Class 10",
        "skills": ["Biology"],
        "interests": ["Healthcare"],
        "work_preferences": ["Helping people"]
    }
    res_c = PathwayDiscoveryService.discover_pathways({
        "career_direction": "exploring",
        "student_profile": profile_c
    })

    names_a = [p["name"] for p in res_a["pathways"]]
    names_b = [p["name"] for p in res_b["pathways"]]
    names_c = [p["name"] for p in res_c["pathways"]]

    # Top pathway must differ between distinctly different profiles
    assert names_a[0] != names_b[0]
    assert names_b[0] != names_c[0]
    assert names_a[0] != names_c[0]

    # Matched evidence must differ
    assert res_a["pathways"][0]["matched_interests"] != res_b["pathways"][0]["matched_interests"]


def test_discovery_exploring_branch_isolation():
    """Test G: Exploring branch must have target_role=None and selected_pathway=None before selection."""
    session_store = {
        "career_direction": "exploring",
        "target_role": "Lawyer"  # Stale target role from a previous session
    }
    # Discovery should ignore stale target_role in exploring mode
    result = PathwayDiscoveryService.discover_pathways({
        "career_direction": "exploring",
        "student_profile": {
            "education_level": "Class 10",
            "skills": ["Coding"],
            "interests": ["Technology"]
        }
    }, session_obj=session_store)
    
    assert result["career_direction"] == "exploring"
    # Discovered pathways should be based on student profile (Tech), not the stale "Lawyer"
    names = [p["name"] for p in result["pathways"]]
    assert "Software Engineering" in names
    assert "Law & Legal Practice" not in names[:1]


def test_pathway_structure_completeness():
    """Verify every pathway object has all required structured fields."""
    result = PathwayDiscoveryService.discover_pathways({
        "career_direction": "exploring",
        "student_profile": {
            "education_level": "Class 10",
            "interests": ["Healthcare", "Biology"],
            "skills": ["Communication"]
        }
    })
    for p in result["pathways"]:
        assert "id" in p
        assert "name" in p
        assert "type" in p
        assert "industry_sector" in p
        assert "overview" in p
        assert "relevance" in p
        assert "why_relevant" in p
        assert "education_pathway" in p
        assert "next_step" in p
        assert "sources" in p
        assert isinstance(p["sources"], list)
        for s in p["sources"]:
            assert "name" in s
            assert "url" in s
            assert "verified_at" in s


def test_pathway_selection_and_retrieval():
    """Verify selecting a pathway persists in session and can be retrieved and cleared."""
    session_store = {}

    # 1. Select pathway
    res = PathwayDiscoveryService.select_pathway(
        pathway_id="software-engineering",
        pathway_name="Software Engineering",
        session_obj=session_store
    )
    assert res["status"] == "success"
    assert res["selected_pathway"]["id"] == "software-engineering"
    assert res["selected_pathway"]["name"] == "Software Engineering"
    assert session_store["selected_pathway"]["id"] == "software-engineering"
    assert session_store["target_role"] == "Software Engineering"

    # 2. Get selected pathway
    get_res = PathwayDiscoveryService.get_selected_pathway(session_obj=session_store)
    assert get_res["is_selected"] is True
    assert get_res["selected_pathway"]["name"] == "Software Engineering"

    # 3. Clear selected pathway
    clear_res = PathwayDiscoveryService.clear_selected_pathway(session_obj=session_store)
    assert clear_res["status"] == "success"
    assert clear_res["is_selected"] is False
    assert "selected_pathway" not in session_store


def test_pathway_shortlist_toggle():
    """Verify shortlisting pathways toggles IDs in session."""
    session_store = {}

    # Add to shortlist
    res1 = PathwayDiscoveryService.toggle_shortlist("data-science-analytics", session_obj=session_store)
    assert res1["is_shortlisted"] is True
    assert "data-science-analytics" in res1["shortlisted_pathways"]

    # Add second
    res2 = PathwayDiscoveryService.toggle_shortlist("cloud-devops", session_obj=session_store)
    assert res2["is_shortlisted"] is True
    assert len(res2["shortlisted_pathways"]) == 2

    # Remove first
    res3 = PathwayDiscoveryService.toggle_shortlist("data-science-analytics", session_obj=session_store)
    assert res3["is_shortlisted"] is False
    assert "data-science-analytics" not in res3["shortlisted_pathways"]
    assert "cloud-devops" in res3["shortlisted_pathways"]


# =============================================================================
# Web Route & HTTP API Integration Tests
# =============================================================================

def test_get_pathway_discovery_page_loads(client):
    """Verify GET /pathway-discovery and GET /career-pathways load HTML."""
    res1 = client.get('/pathway-discovery')
    assert res1.status_code == 200
    assert b"Career Pathways To Explore" in res1.data
    assert b"Active Exploration Context" in res1.data

    res2 = client.get('/career-pathways')
    assert res2.status_code == 200

    res3 = client.get('/api/career/pathways')
    assert res3.status_code == 200


def test_api_get_pathways_json(client):
    """Verify GET /api/career/pathways with JSON header returns structured pathways."""
    response = client.get('/api/career/pathways', headers={"Accept": "application/json"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "pathways" in data
    assert isinstance(data["pathways"], list)


def test_api_post_discover_pathways(client):
    """Verify POST /api/career/pathways/discover returns custom discovery results."""
    payload = {
        "career_direction": "exploring",
        "student_profile": {
            "education_level": "B.Com",
            "interests": ["Finance", "Business"],
            "skills": ["Mathematics", "Data Analysis"],
            "career_preferences": ["Private sector"]
        }
    }
    response = client.post('/api/career/pathways/discover', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["total_pathways"] > 0
    top_p = data["pathways"][0]
    assert "Banking & Financial Analysis" in [p["name"] for p in data["pathways"][:2]]


def test_api_post_select_pathway_and_get_selected(client):
    """Verify POST /api/career/pathways/select and GET /api/career/pathways/selected."""
    payload = {
        "pathway_id": "civil-engineering",
        "pathway_name": "Civil & Infrastructure Engineering"
    }
    sel_res = client.post('/api/career/pathways/select', json=payload)
    assert sel_res.status_code == 200
    data = sel_res.get_json()
    assert data["status"] == "success"
    assert data["selected_pathway"]["id"] == "civil-engineering"

    # Verify retrieval
    get_res = client.get('/api/career/pathways/selected')
    assert get_res.status_code == 200
    get_data = get_res.get_json()
    assert get_data["is_selected"] is True
    assert get_data["selected_pathway"]["id"] == "civil-engineering"

    # Clear
    del_res = client.delete('/api/career/pathways/selected')
    assert del_res.status_code == 200
    assert del_res.get_json()["status"] == "success"


def test_api_post_shortlist_toggle(client):
    """Verify POST /api/career/pathways/shortlist toggles item."""
    res1 = client.post('/api/career/pathways/shortlist', json={"pathway_id": "creative-design"})
    assert res1.status_code == 200
    assert res1.get_json()["is_shortlisted"] is True

    res2 = client.post('/api/career/pathways/shortlist', json={"pathway_id": "creative-design"})
    assert res2.status_code == 200
    assert res2.get_json()["is_shortlisted"] is False


# =============================================================================
# Agent & Orchestrator Integration Tests
# =============================================================================

def test_opportunity_pathway_agent_execution():
    """Verify OpportunityPathwayAgent processes task directly."""
    agent = OpportunityPathwayAgent()
    task_input = {
        "career_direction": "exploring",
        "student_profile": {
            "education_level": "Undergraduate",
            "interests": ["Technology"],
            "skills": ["Programming"]
        }
    }
    result = agent.process_task(task_input)
    assert result["status"] == "success"
    assert result["agent"] == "OpportunityPathwayAgent"
    assert "explanation" in result
    assert result["data"]["total_pathways"] > 0


def test_orchestrator_pathway_discovery_routing():
    """Verify AgentOrchestrator routes natural language and explicit discovery tasks."""
    orch = AgentOrchestrator()

    # 1. Explicit intent in context
    res_explicit = orch.route_request(None, {
        "intent": "pathway_discovery",
        "career_direction": "exploring",
        "student_profile": {"education_level": "B.Tech", "skills": ["Python"]}
    })
    assert res_explicit["intent"] == "pathway_discovery"
    assert res_explicit["agent_used"] == "OpportunityPathwayAgent"
    assert res_explicit["status"] == "success"

    # 2. Natural language query
    res_nl = orch.route_request("Discover career pathways for my profile", {
        "career_direction": "exploring",
        "student_profile": {"education_level": "Class 12", "interests": ["Healthcare"]}
    })
    assert res_nl["intent"] == "pathway_discovery"
    assert res_nl["agent_used"] == "OpportunityPathwayAgent"
    assert res_nl["status"] == "success"


def test_pathway_selection_missing_id_rejected():
    """Verify selecting a pathway without ID raises ValueError."""
    with pytest.raises(ValueError) as exc:
        PathwayDiscoveryService.select_pathway(pathway_id="")
    assert "required" in str(exc.value).lower()


def test_career_service_get_pathways_by_sector():
    """Verify CareerService.get_pathways_by_sector returns sector matching pathways."""
    from career.services import CareerService
    tech_pathways = CareerService.get_pathways_by_sector("Technology")
    assert len(tech_pathways) >= 2
    for p in tech_pathways:
        assert p["industry_sector"] == "Technology"

    empty_res = CareerService.get_pathways_by_sector("")
    assert empty_res == []


def test_api_post_select_pathway_missing_id_rejected(client):
    """Verify POST /api/career/pathways/select without ID returns 400."""
    res = client.post('/api/career/pathways/select', json={"pathway_id": ""})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_orchestrator_pathway_discovery_known_target():
    """Verify AgentOrchestrator routes known target discovery."""
    orch = AgentOrchestrator()
    res = orch.route_request("Explore pathways for Software Engineer", {
        "intent": "pathway_discovery",
        "career_direction": "known",
        "target_role": "Software Engineer"
    })
    assert res["status"] == "success"
    assert res["agent_used"] == "OpportunityPathwayAgent"
    assert len(res["result"]["pathways"]) == 1

