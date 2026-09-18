import pytest
from career.services import CareerDirectionService
from agents.orchestrator import AgentOrchestrator


# =============================================================================
# Unit Tests for CareerDirectionService
# =============================================================================

def test_service_known_target_success():
    """Verify known career direction stores target role correctly."""
    session_store = {}
    res = CareerDirectionService.set_direction(
        direction="known",
        target_role="Data Scientist",
        session_obj=session_store
    )
    assert res["status"] == "success"
    assert res["career_direction"] == "known"
    assert res["target_role"] == "Data Scientist"
    assert session_store["career_direction"] == "known"
    assert session_store["target_role"] == "Data Scientist"

    # Verify getter
    state = CareerDirectionService.get_direction(session_obj=session_store)
    assert state["is_set"] is True
    assert state["career_direction"] == "known"
    assert state["target_role"] == "Data Scientist"


def test_service_known_target_empty_role_rejected():
    """Verify known direction with empty/whitespace role raises ValueError."""
    session_store = {}
    with pytest.raises(ValueError) as exc_none:
        CareerDirectionService.set_direction(direction="known", target_role=None, session_obj=session_store)
    assert "required" in str(exc_none.value).lower()

    with pytest.raises(ValueError) as exc_empty:
        CareerDirectionService.set_direction(direction="known", target_role="   ", session_obj=session_store)
    assert "required" in str(exc_empty.value).lower()


def test_service_exploring_success():
    """Verify exploring direction succeeds without requiring a target role."""
    session_store = {"target_role": "Previous Role"}
    res = CareerDirectionService.set_direction(
        direction="exploring",
        target_role=None,
        session_obj=session_store
    )
    assert res["status"] == "success"
    assert res["career_direction"] == "exploring"
    assert res["target_role"] is None
    assert session_store["career_direction"] == "exploring"
    assert session_store["target_role"] is None

    # Verify getter
    state = CareerDirectionService.get_direction(session_obj=session_store)
    assert state["is_set"] is True
    assert state["career_direction"] == "exploring"
    assert state["target_role"] is None


def test_service_invalid_direction_rejected():
    """Verify invalid directions are rejected with clear ValueError."""
    session_store = {}
    with pytest.raises(ValueError) as exc_invalid:
        CareerDirectionService.set_direction(direction="undecided", session_obj=session_store)
    assert "invalid career direction" in str(exc_invalid.value).lower()

    with pytest.raises(ValueError) as exc_none:
        CareerDirectionService.set_direction(direction=None, session_obj=session_store)
    assert "required" in str(exc_none.value).lower()


def test_service_clear_direction():
    """Verify clearing direction resets session state."""
    session_store = {"career_direction": "known", "target_role": "Architect"}
    res = CareerDirectionService.clear_direction(session_obj=session_store)
    assert res["status"] == "success"
    assert res["is_set"] is False
    assert "career_direction" not in session_store
    assert "target_role" not in session_store


# =============================================================================
# HTTP API & Web Route Integration Tests
# =============================================================================

def test_get_career_direction_page_loads(client):
    """Verify GET /career-direction and /api/career/direction render HTML template."""
    res1 = client.get('/career-direction')
    assert res1.status_code == 200
    assert b"Let's understand your career direction" in res1.data
    assert b"I know my target career" in res1.data
    assert b"I'm still exploring" in res1.data

    res2 = client.get('/api/career/direction')
    assert res2.status_code == 200
    assert b"Let's understand your career direction" in res2.data


def test_api_post_known_target_success(client):
    """Verify POST /api/career/direction with known target role."""
    payload = {
        "career_direction": "known",
        "target_role": "Doctor"
    }
    response = client.post('/api/career/direction', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["career_direction"] == "known"
    assert data["target_role"] == "Doctor"

    # Verify subsequent GET with Accept: application/json returns the state
    get_res = client.get('/api/career/direction', headers={"Accept": "application/json"})
    assert get_res.status_code == 200
    state = get_res.get_json()
    assert state["is_set"] is True
    assert state["career_direction"] == "known"
    assert state["target_role"] == "Doctor"


def test_api_post_known_target_empty_rejected(client):
    """Verify POST /api/career/direction with empty target role returns 400."""
    payload_empty = {
        "career_direction": "known",
        "target_role": ""
    }
    response = client.post('/api/career/direction', json=payload_empty)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_api_post_exploring_success(client):
    """Verify POST /api/career/direction with exploring direction."""
    payload = {
        "career_direction": "exploring"
    }
    response = client.post('/api/career/direction', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["career_direction"] == "exploring"
    assert data["target_role"] is None

    # Verify subsequent GET
    get_res = client.get('/api/career/direction?format=json')
    assert get_res.status_code == 200
    state = get_res.get_json()
    assert state["career_direction"] == "exploring"
    assert state["target_role"] is None


def test_api_post_invalid_direction_rejected(client):
    """Verify POST with invalid direction returns 400."""
    response = client.post('/api/career/direction', json={"career_direction": "random_value"})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_api_career_health_endpoint(client):
    """Verify GET /api/career/health is intact."""
    response = client.get('/api/career/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["module"] == "career_pathway_guidance"


def test_agent_orchestrator_integration_with_direction():
    """Verify AgentOrchestrator accepts context with career_direction state."""
    orch = AgentOrchestrator()

    # Known direction context
    res_known = orch.route_request("How do I become a Software Engineer?", {
        "career_direction": "known",
        "target_role": "Software Engineer",
        "current_skills": ["Python", "Git"]
    })
    assert res_known["status"] == "success"
    assert "Software Engineer" in str(res_known["result"])

    # Exploring direction context
    res_exploring = orch.route_request("I am exploring careers", {
        "career_direction": "exploring",
        "current_skills": ["Problem Solving", "Mathematics"]
    })
    assert res_exploring["status"] in ("success", "clarification_needed")


# =============================================================================
# State Transition & Branch Isolation Test Cases (Cases 1 - 10)
# =============================================================================

def test_transition_known_to_exploring_clears_target_and_stale_pathway(client):
    """Test 1 & 3: Known target 'Lawyer' -> switch to exploring -> target_role becomes None."""
    # 1. Establish known target 'Lawyer'
    post_res1 = client.post('/api/career/direction', json={
        "career_direction": "known",
        "target_role": "Lawyer"
    })
    assert post_res1.status_code == 200
    assert post_res1.get_json()["target_role"] == "Lawyer"

    # Select target pathway
    client.post('/api/career/pathways/select', json={"pathway_id": "public-service-govt", "pathway_name": "Public Administration & Law"})

    # 2. Switch direction to exploring
    post_res2 = client.post('/api/career/direction', json={
        "career_direction": "exploring"
    })
    assert post_res2.status_code == 200
    assert post_res2.get_json()["career_direction"] == "exploring"
    assert post_res2.get_json()["target_role"] is None

    # 3. Verify GET /api/career/direction strictly returns target_role: None
    get_res = client.get('/api/career/direction?format=json')
    assert get_res.status_code == 200
    data = get_res.get_json()
    assert data["career_direction"] == "exploring"
    assert data["target_role"] is None

    # 4. Verify selected pathway is cleared
    sel_res = client.get('/api/career/pathways/selected')
    assert sel_res.get_json()["is_selected"] is False
    assert sel_res.get_json()["selected_pathway"] is None


def test_exploring_discovery_returns_multiple_pathways_without_stale_target(client):
    """Test 4 & 5: Exploring flow returns multiple pathways without any stale target goal."""
    # 1. Start with known target 'Lawyer'
    client.post('/api/career/direction', json={
        "career_direction": "known",
        "target_role": "Lawyer"
    })

    # 2. Switch to exploring and submit exploration profile (Class 10, Communication, Education)
    client.post('/api/profile/discovery', json={
        "education_level": "Class 10",
        "skills": ["Communication"],
        "interests": ["Education"],
        "work_preferences": ["Working with people"],
        "career_preferences": ["Open to multiple options"]
    })

    # 3. Request pathway discovery
    path_res = client.get('/api/career/pathways', headers={"Accept": "application/json"})
    assert path_res.status_code == 200
    p_data = path_res.get_json()
    assert p_data["status"] == "success"
    assert p_data["career_direction"] == "exploring"
    assert p_data["target_role"] is None
    assert p_data["total_pathways"] > 1
    assert len(p_data["pathways"]) >= 2
    # Ensure 'Lawyer' is not declared as the target
    assert "Lawyer" not in [p["name"] for p in p_data["pathways"]]
    for p in p_data["pathways"]:
        assert "why_relevant" in p


def test_exploring_pathway_selection_sets_downstream_target_and_deselection_clears(client):
    """Test 6: Exploring -> student selects one pathway -> downstream target established."""
    # Setup exploration profile
    client.post('/api/profile/discovery', json={
        "education_level": "Class 10",
        "skills": ["Communication"],
        "interests": ["Education"]
    })

    # Select Education pathway
    sel_res = client.post('/api/career/pathways/select', json={
        "pathway_id": "education-teaching",
        "pathway_name": "Education & Academic Teaching"
    })
    assert sel_res.status_code == 200
    assert sel_res.get_json()["selected_pathway"]["id"] == "education-teaching"

    # Verify fit analysis receives the selected pathway
    fit_res = client.get('/api/career/pathways/analysis', headers={"Accept": "application/json"})
    assert fit_res.status_code == 200
    fit_data = fit_res.get_json()
    assert fit_data["status"] == "success"
    assert fit_data["selected_pathway"]["id"] == "education-teaching"
    assert fit_data["target_role"] == "Education & Academic Teaching"

    # Deselect pathway
    del_res = client.delete('/api/career/pathways/selected')
    assert del_res.status_code == 200

    # Fit analysis now requests clarification rather than using stale target
    fit_res2 = client.get('/api/career/pathways/analysis', headers={"Accept": "application/json"})
    assert fit_res2.get_json()["status"] == "clarification_needed"


def test_known_target_discovery_remains_target_specific(client):
    """Test 7: Known target -> pathway discovery returns target-specific single pathway."""
    client.post('/api/career/direction', json={
        "career_direction": "known",
        "target_role": "Doctor"
    })

    res = client.get('/api/career/pathways', headers={"Accept": "application/json"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["career_direction"] == "known"
    assert data["target_role"] == "Doctor"
    assert data["total_pathways"] == 1
    assert data["pathways"][0]["name"] == "Medicine & Healthcare"


def test_new_session_isolation_does_not_inherit_previous_target(app):
    """Test 8: Distinct client session does not inherit another session's target."""
    client1 = app.test_client()
    client2 = app.test_client()

    client1.post('/api/career/direction', json={
        "career_direction": "known",
        "target_role": "Lawyer"
    })

    # Client 2 starts clean
    res2 = client2.get('/api/career/direction?format=json')
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert data2["career_direction"] is None
    assert data2["target_role"] is None

