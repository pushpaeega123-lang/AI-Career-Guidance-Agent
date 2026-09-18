import pytest
from profile.services import CareerDiscoveryService, ProfileService
from profile.models import StudentProfile
from agents.orchestrator import AgentOrchestrator
from db import db


# =============================================================================
# Unit Tests for CareerDiscoveryService Logic & Normalization
# =============================================================================

def test_normalize_string_list():
    """Verify list normalization handles diverse formats, whitespace, and deduplication."""
    # List of strings with whitespace and duplicates
    assert CareerDiscoveryService._normalize_string_list(["  Python  ", "Java", "python", "  ", None]) == ["Python", "Java"]

    # Comma-separated string
    assert CareerDiscoveryService._normalize_string_list("Data Analysis, Machine Learning, Python, data analysis") == [
        "Data Analysis", "Machine Learning", "Python"
    ]

    # JSON formatted list string
    assert CareerDiscoveryService._normalize_string_list('["Leadership", "Communication", "leadership"]') == [
        "Leadership", "Communication"
    ]

    # Empty / None inputs
    assert CareerDiscoveryService._normalize_string_list(None) == []
    assert CareerDiscoveryService._normalize_string_list("") == []
    assert CareerDiscoveryService._normalize_string_list([]) == []


def test_validate_exploration_profile_success():
    """Verify valid exploration profile payload is normalized and structured."""
    payload = {
        "education_level": "Undergraduate",
        "subjects": ["Mathematics", "Computer Science"],
        "skills": ["Programming", "Problem Solving"],
        "interests": ["Technology", "AI & Robotics"],
        "work_preferences": ["Working with technology", "Creative work"],
        "career_preferences": ["Private sector", "Entrepreneurship"],
        "additional_information": "Excited about cutting-edge tech startups."
    }
    validated = CareerDiscoveryService.validate_exploration_profile(payload)
    assert validated["education_level"] == "Undergraduate"
    assert len(validated["subjects"]) == 2
    assert len(validated["skills"]) == 2
    assert len(validated["interests"]) == 2
    assert len(validated["work_preferences"]) == 2
    assert len(validated["career_preferences"]) == 2
    assert validated["additional_information"] == "Excited about cutting-edge tech startups."


def test_validate_exploration_profile_education_required():
    """Verify missing or empty education level raises ValueError."""
    with pytest.raises(ValueError) as exc_none:
        CareerDiscoveryService.validate_exploration_profile({
            "skills": ["Programming"],
            "interests": ["Technology"]
        })
    assert "education level is required" in str(exc_none.value).lower()

    with pytest.raises(ValueError) as exc_empty:
        CareerDiscoveryService.validate_exploration_profile({
            "education_level": "   ",
            "skills": ["Programming"]
        })
    assert "education level is required" in str(exc_empty.value).lower()


def test_validate_exploration_profile_requires_skill_or_interest():
    """Verify at least one skill OR interest is required."""
    with pytest.raises(ValueError) as exc:
        CareerDiscoveryService.validate_exploration_profile({
            "education_level": "B.Tech",
            "subjects": ["Mathematics"],
            "skills": [],
            "interests": []
        })
    assert "at least one current skill or interest" in str(exc.value).lower()


def test_validate_exploration_profile_skills_only_or_interests_only():
    """Verify providing only skills or only interests succeeds."""
    # Skills only
    v1 = CareerDiscoveryService.validate_exploration_profile({
        "education_level": "Class 10",
        "skills": ["Communication", "Mathematics"]
    })
    assert v1["skills"] == ["Communication", "Mathematics"]
    assert v1["interests"] == []

    # Interests only
    v2 = CareerDiscoveryService.validate_exploration_profile({
        "education_level": "Intermediate / 12th",
        "interests": ["Healthcare", "Biology"]
    })
    assert v2["interests"] == ["Healthcare", "Biology"]
    assert v2["skills"] == []


def test_validate_exploration_profile_optional_additional_info():
    """Verify additional_information can be omitted and evaluates to None."""
    validated = CareerDiscoveryService.validate_exploration_profile({
        "education_level": "Postgraduate",
        "skills": ["Data Analysis"]
    })
    assert validated["additional_information"] is None


def test_service_save_and_get_exploration_profile():
    """Verify saving to session and retrieving exploration state."""
    session_store = {}
    payload = {
        "education_level": "Diploma",
        "subjects": ["Physics"],
        "skills": ["Problem Solving"],
        "interests": ["Engineering"],
        "work_preferences": ["Working with machines"],
        "career_preferences": ["Government sector"]
    }
    res = CareerDiscoveryService.save_exploration_profile(payload, session_obj=session_store)
    assert res["status"] == "success"
    assert res["career_direction"] == "exploring"
    assert res["target_role"] is None
    assert session_store["career_direction"] == "exploring"
    assert session_store["exploration_profile"]["education_level"] == "Diploma"

    # Retrieve state
    retrieved = CareerDiscoveryService.get_exploration_profile(session_obj=session_store)
    assert retrieved["is_set"] is True
    assert retrieved["career_direction"] == "exploring"
    assert retrieved["student_profile"]["education_level"] == "Diploma"
    assert retrieved["student_profile"]["skills"] == ["Problem Solving"]


def test_service_clear_exploration_profile():
    """Verify clearing exploration profile from session."""
    session_store = {
        "career_direction": "exploring",
        "exploration_profile": {"education_level": "B.Sc", "skills": ["Python"]}
    }
    clear_res = CareerDiscoveryService.clear_exploration_profile(session_obj=session_store)
    assert clear_res["status"] == "success"
    assert "exploration_profile" not in session_store


def test_service_database_persistence(app):
    """Verify saving exploration profile updates existing StudentProfile record if student_id provided."""
    with app.app_context():
        student = StudentProfile(
            full_name="Elena Rostova",
            email="elena.rostova@example.com",
            education_level="Class 10"
        )
        db.session.add(student)
        db.session.commit()
        s_id = student.id

        payload = {
            "education_level": "B.Tech",
            "subjects": ["Computer Science", "Mathematics"],
            "skills": ["Python", "Algorithms"],
            "interests": ["Technology", "AI"],
            "work_preferences": ["Working with technology"],
            "career_preferences": ["Private sector"],
            "additional_information": "Looking to specialize in Machine Learning."
        }

        CareerDiscoveryService.save_exploration_profile(payload, student_id=s_id)

        # Query updated student
        updated = db.session.get(StudentProfile, s_id)
        assert updated.education_level == "B.Tech"
        d = updated.to_dict()

        assert "Python" in d["skills"]
        assert "Technology" in d["interests"]
        assert d["additional_information"] == "Looking to specialize in Machine Learning."


# =============================================================================
# Web Route & HTTP API Integration Tests
# =============================================================================

def test_get_career_discovery_page_loads(client):
    """Verify GET /career-discovery and GET /api/profile/discovery load questionnaire HTML."""
    res1 = client.get('/career-discovery')
    assert res1.status_code == 200
    assert b"Career Discovery Questionnaire" in res1.data
    assert b"Your Education Level" in res1.data
    assert b"Your Current Skills" in res1.data
    assert b"Your Interests" in res1.data

    res2 = client.get('/api/profile/discovery')
    assert res2.status_code == 200
    assert b"Career Discovery Questionnaire" in res2.data


def test_api_get_career_discovery_json(client):
    """Verify GET /api/profile/discovery with JSON header returns structured state."""
    response = client.get('/api/profile/discovery', headers={"Accept": "application/json"})
    assert response.status_code == 200
    data = response.get_json()
    assert "status" in data
    assert "student_profile" in data


def test_api_post_discovery_success(client):
    """Verify POST /api/profile/discovery with valid payload returns 200 and saves state."""
    payload = {
        "education_level": "B.Sc",
        "subjects": ["Biology", "Chemistry"],
        "skills": ["Data Analysis", "Research"],
        "interests": ["Healthcare", "Research"],
        "work_preferences": ["Research/problem solving"],
        "career_preferences": ["Higher education/research"],
        "additional_information": "Aiming for clinical research roles."
    }
    response = client.post('/api/profile/discovery', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["career_direction"] == "exploring"
    assert data["student_profile"]["education_level"] == "B.Sc"
    assert "Research" in data["student_profile"]["skills"]

    # Verify state retrieved via subsequent GET
    get_res = client.get('/api/profile/discovery?format=json')
    assert get_res.status_code == 200
    state = get_res.get_json()
    assert state["is_set"] is True
    assert state["student_profile"]["education_level"] == "B.Sc"


def test_api_post_discovery_missing_education_rejected(client):
    """Verify POST /api/profile/discovery without education level returns 400."""
    payload = {
        "skills": ["Communication"],
        "interests": ["Business"]
    }
    response = client.post('/api/profile/discovery', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "education level is required" in data["error"].lower()


def test_api_post_discovery_missing_skills_and_interests_rejected(client):
    """Verify POST /api/profile/discovery without skills or interests returns 400."""
    payload = {
        "education_level": "Undergraduate",
        "subjects": ["Arts"],
        "skills": [],
        "interests": []
    }
    response = client.post('/api/profile/discovery', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_api_post_discovery_form_data_success(client):
    """Verify POST /api/profile/discovery with form data works correctly."""
    form_data = {
        "education_level": "B.Com",
        "skills[]": ["Data Analysis", "Mathematics"],
        "interests[]": ["Finance", "Business"],
        "career_preferences": "Private sector"
    }
    response = client.post('/api/profile/discovery', data=form_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["student_profile"]["education_level"] == "B.Com"


def test_api_delete_discovery_state(client):
    """Verify DELETE /api/profile/discovery clears exploration profile."""
    # First save
    client.post('/api/profile/discovery', json={"education_level": "B.A", "interests": ["Media"]})

    # Clear
    del_res = client.delete('/api/profile/discovery')
    assert del_res.status_code == 200
    assert del_res.get_json()["status"] == "success"

    # Verify cleared
    get_res = client.get('/api/profile/discovery?format=json')
    assert get_res.get_json()["is_set"] is False


def test_agent_orchestrator_integration_with_exploration_profile():
    """Verify AgentOrchestrator accepts context with structured exploration profile."""
    orch = AgentOrchestrator()

    context = {
        "career_direction": "exploring",
        "target_role": None,
        "student_profile": {
            "education_level": "Undergraduate",
            "subjects": ["Computer Science", "Mathematics"],
            "skills": ["Programming", "Problem Solving"],
            "interests": ["Technology", "AI"],
            "work_preferences": ["Working with technology"],
            "career_preferences": ["Private sector"],
            "additional_information": "Exploring software and data careers."
        }
    }

    # Query for guidance
    res = orch.route_request("I am exploring career options in technology", context)
    assert res["status"] in ("success", "clarification_needed")
