import json
import pytest
from app import create_app
from db import db
from profile.models import StudentProfile
from opportunities.services import OpportunityService
from opportunities.models import Opportunity
from career.services import CareerDirectionService

JSON_HEADERS = {"Accept": "application/json"}


@pytest.fixture
def app():
    """Create test application context with in-memory database."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for simulating HTTP sessions and API interactions."""
    return app.test_client()


# =============================================================================
# Unit Tests for OpportunityService
# =============================================================================

def test_opportunity_service_govt_jobs_class_10():
    """Verify OpportunityService returns verified government jobs for Class 10."""
    res = OpportunityService.get_opportunities(category="govt_job", qualification="Class 10")
    assert res["status"] == "success"
    assert res["category"] == "govt_job"
    assert res["qualification"] == "Class 10"
    assert res["total_count"] >= 3
    assert res["has_verified_data"] is True
    
    titles = [opp["title"] for opp in res["opportunities"]]
    assert any("SSC MTS" in t or "Multi-Tasking Staff" in t for t in titles)
    assert any("Railway" in t or "RRB" in t or "Group D" in t for t in titles)
    assert any("Post" in t or "GDS" in t for t in titles)

    # Check required fields
    for opp in res["opportunities"]:
        assert "title" in opp
        assert "qualification" in opp
        assert "exam_selection" in opp
        assert "description" in opp
        assert "source" in opp


def test_opportunity_service_private_jobs_class_10():
    """Verify OpportunityService returns verified private jobs for Class 10."""
    res = OpportunityService.get_opportunities(category="private_job", qualification="Class 10")
    assert res["status"] == "success"
    assert res["category"] == "private_job"
    assert res["qualification"] == "Class 10"
    assert res["total_count"] >= 3
    assert res["has_verified_data"] is True

    for opp in res["opportunities"]:
        assert "title" in opp
        assert "qualification" in opp
        assert "skills" in opp
        assert len(opp["skills"]) > 0
        assert "description" in opp
        assert "source" in opp


def test_opportunity_service_qualification_normalization():
    """Verify diverse qualification formats normalize to standard catalog keys."""
    assert OpportunityService.normalize_qualification("10th Standard") == "Class 10"
    assert OpportunityService.normalize_qualification("Matriculation") == "Class 10"
    assert OpportunityService.normalize_qualification("12th Grade") == "Class 12"
    assert OpportunityService.normalize_qualification("Intermediate / 12th") == "Class 12"
    assert OpportunityService.normalize_qualification("Diploma in Mechanical") == "Diploma"
    assert OpportunityService.normalize_qualification("B.Tech in Computer Science") == "Undergraduate"
    assert OpportunityService.normalize_qualification("Bachelor of Science") == "Undergraduate"


def test_opportunity_service_get_by_type_backwards_compatible():
    """Verify get_opportunities_by_type works without errors."""
    opps = OpportunityService.get_opportunities_by_type("govt_job")
    assert isinstance(opps, list)
    assert len(opps) > 0


# =============================================================================
# Web Routes & HTTP Endpoint Tests
# =============================================================================

def test_start_journey_page_loads(client):
    """Verify GET /start-journey renders HTML with entry choice cards."""
    res = client.get('/start-journey')
    assert res.status_code == 200
    assert b"What do you want to do?" in res.data
    assert b"Continue Education" in res.data
    assert b"Start Working" in res.data
    assert b"Explore education and career pathways" in res.data
    assert b"Explore job opportunities based on your current qualification" in res.data


def test_start_journey_aliases_load(client):
    """Verify aliases /entry-choice and /job-opportunities render cleanly."""
    res1 = client.get('/entry-choice')
    assert res1.status_code == 200
    assert b"What do you want to do?" in res1.data

    res2 = client.get('/job-opportunities')
    assert res2.status_code == 200
    assert b"What do you want to do?" in res2.data


def test_api_get_govt_jobs_endpoint(client):
    """Verify GET /api/opportunities/jobs returns government opportunities."""
    res = client.get('/api/opportunities/jobs?category=govt_job&qualification=Class+10', headers=JSON_HEADERS)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["category"] == "govt_job"
    assert data["qualification"] == "Class 10"
    assert len(data["opportunities"]) >= 3
    assert any("SSC MTS" in opp["title"] for opp in data["opportunities"])


def test_api_get_private_jobs_endpoint(client):
    """Verify GET /api/opportunities/jobs returns private opportunities."""
    res = client.get('/api/opportunities/jobs?category=private_job&qualification=Class+12', headers=JSON_HEADERS)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["category"] == "private_job"
    assert data["qualification"] == "Class 12"
    assert len(data["opportunities"]) >= 3


def test_api_post_jobs_query_endpoint(client):
    """Verify POST /api/opportunities/jobs processes JSON query body."""
    res = client.post('/api/opportunities/jobs', json={
        "category": "govt_job",
        "qualification": "Diploma"
    }, headers=JSON_HEADERS)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["qualification"] == "Diploma"
    assert any("Junior Engineer" in opp["title"] for opp in data["opportunities"])


def test_api_qualification_detection_with_profile(client, app):
    """Verify /api/opportunities/qualification detects student's registered qualification."""
    with app.app_context():
        student = StudentProfile(
            id=10,
            full_name="Priya Sharma",
            email="priya@example.com",
            education_level="Class 12"
        )
        db.session.add(student)
        db.session.commit()

    with client.session_transaction() as sess:
        sess["student_id"] = 10

    res = client.get('/api/opportunities/qualification', headers=JSON_HEADERS)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["is_detected"] is True
    assert data["qualification"] == "Class 12"


# =============================================================================
# State Isolation & Non-Regression Tests
# =============================================================================

def test_state_isolation_start_working_does_not_corrupt_career_state(client):
    """Verify exploring jobs does NOT inject fake career direction, target role, or selected pathway."""
    with client.session_transaction() as sess:
        # Client has no prior career state
        assert "career_direction" not in sess
        assert "target_role" not in sess
        assert "selected_pathway" not in sess

    # Student checks government opportunities
    res_govt = client.get('/api/opportunities/jobs?category=govt_job&qualification=Class+10')
    assert res_govt.status_code == 200

    # Student checks private opportunities
    res_priv = client.get('/api/opportunities/jobs?category=private_job&qualification=Class+10')
    assert res_priv.status_code == 200

    # Verify career direction state remains unset/pure
    res_dir = client.get('/api/career/direction', headers=JSON_HEADERS)
    assert res_dir.status_code == 200
    data = res_dir.get_json()
    assert data["is_set"] is False
    assert data["career_direction"] is None
    assert data["target_role"] is None


def test_continue_education_flow_unaffected(client):
    """Verify that Continue Education option leads directly into existing Career Direction flow."""
    # 1. Student selects known target
    res_post = client.post('/api/career/direction', json={
        "career_direction": "known",
        "target_role": "Software Developer"
    })
    assert res_post.status_code == 200

    # 2. Verify state
    res_get = client.get('/api/career/direction', headers=JSON_HEADERS)
    assert res_get.status_code == 200
    data = res_get.get_json()
    assert data["career_direction"] == "known"
    assert data["target_role"] == "Software Developer"


def test_landing_page_start_journey_link(client):
    """Verify landing page hero links to /start-journey."""
    res = client.get('/')
    assert res.status_code == 200
    assert b'href="/start-journey"' in res.data
