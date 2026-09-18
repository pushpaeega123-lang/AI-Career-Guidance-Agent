"""
Unit and Integration Tests for Education Pathway Guidance (Member 2 - Step 6).
Tests education catalogue integrity, profile-connected recommendations, target career
customization (?career_id=...), incomplete profile handling, explainability, neutrality,
and REST endpoints.
"""

import json
import pytest
from education.catalogue import EDUCATION_PATHWAY_CATALOGUE, PATHWAY_BY_ID, PATHWAYS_BY_LEVEL
from education.services import EducationService
from profile.services import ProfileService
from profile.models import StudentProfile


# ==========================================
# 1. Education Catalogue Tests
# ==========================================

def test_education_catalogue_loads_and_has_required_fields():
    """Verify that the Education Pathway Catalogue loads with valid schema."""
    assert len(EDUCATION_PATHWAY_CATALOGUE) > 0
    required_keys = [
        "id", "title", "current_education_level", "possible_next_step",
        "higher_study_options", "specialization_options", "related_career_ids",
        "relevant_domains", "relevant_interests", "useful_skills", "explanation",
        "admission_prerequisites", "limitations"
    ]
    for pathway in EDUCATION_PATHWAY_CATALOGUE:
        for key in required_keys:
            assert key in pathway, f"Missing key '{key}' in pathway {pathway.get('id')}"
            assert pathway[key], f"Field '{key}' is empty in pathway {pathway.get('id')}"


def test_education_catalogue_covers_key_educational_levels():
    """Verify pathways exist across all foundational progression tiers."""
    levels = set(p["current_education_level"] for p in EDUCATION_PATHWAY_CATALOGUE)
    assert "Higher Secondary" in levels
    assert "Diploma" in levels
    assert "Undergraduate" in levels
    assert "Postgraduate" in levels


def test_individual_catalogue_pathway_retrieval():
    """Test retrieving a single pathway by ID and 404 behavior for invalid ID."""
    valid_id = "undergrad-cs-to-mtech-ms"
    pathway = EducationService.get_pathway_by_id(valid_id)
    assert pathway is not None
    assert pathway["id"] == valid_id
    assert "M.Tech" in pathway["possible_next_step"]

    invalid_pathway = EducationService.get_pathway_by_id("non-existent-pathway-12345")
    assert invalid_pathway is None


def test_catalogue_filtering_by_level_and_domain():
    """Test filtering catalogue by education level and domain."""
    # Filter by level
    undergrad_pathways = EducationService.get_education_catalogue(education_level="Undergraduate")
    assert len(undergrad_pathways) > 0
    assert all(
        p["current_education_level"] == "Undergraduate" or "undergraduate" in p["possible_next_step"].lower()
        for p in undergrad_pathways
    )

    # Filter by domain
    tech_pathways = EducationService.get_education_catalogue(domain="Technology & Software")
    assert len(tech_pathways) > 0
    assert all(
        "Technology & Software" in p.get("relevant_domains", [])
        for p in tech_pathways
    )

    # Combined filter
    combo = EducationService.get_education_catalogue(education_level="Undergraduate", domain="Technology & Software")
    assert len(combo) > 0


# ==========================================
# 2. Profile Integration & Recommendation Tests
# ==========================================

def test_valid_profile_receives_education_pathway_guidance(app):
    """Test that a valid student profile receives structured educational guidance."""
    with app.app_context():
        profile, err = ProfileService.create_profile({
            "full_name": "Rohan Gupta",
            "email": "rohan.gupta@example.com",
            "education_level": "Undergraduate",
            "qualification": "B.Tech in Computer Science & Engineering",
            "skills": ["Python", "Data Structures", "Algorithms", "Git"],
            "interests": ["Python", "Artificial Intelligence", "Machine Learning"],
            "career_goals": "Machine Learning Engineer"
        })
        assert err is None
        assert profile is not None

        guidance, error = EducationService.get_pathways_for_profile(profile.id)
        assert error is None
        assert guidance["success"] is True
        assert guidance["student_name"] == "Rohan Gupta"
        assert guidance["profile_id"] == profile.id
        assert guidance["pathways_count"] > 0
        assert len(guidance["pathways"]) > 0

        # Top pathway should align with undergraduate computing/AI
        top_p = guidance["pathways"][0]
        assert top_p["current_education_level"] == "Undergraduate"
        assert len(top_p["why_identified"]) >= 3
        assert len(top_p["career_connections"]) > 0


def test_complete_profile_produces_relevant_pathways_and_connections(app):
    """Test complete profile populates career connections, skills, and specializations."""
    with app.app_context():
        profile, err = ProfileService.create_profile({
            "full_name": "Neha Joshi",
            "email": "neha.joshi@example.com",
            "education_level": "Undergraduate",
            "qualification": "B.Com in Accounting and Finance",
            "degree_details": {
                "degree_name": "B.Com",
                "major": "Finance & Taxation",
                "institution": "Delhi University"
            },
            "skills": ["Financial Modeling", "Auditing", "Excel"],
            "interests": ["Accounting & Finance", "Financial Analysis"],
            "career_goals": "Chartered Financial Analyst"
        })
        assert err is None

        guidance, error = EducationService.get_pathways_for_profile(profile.id)
        assert error is None
        assert guidance["success"] is True

        # Check that commerce/finance pathway is prioritized
        pathway_titles = [p["title"] for p in guidance["pathways"]]
        assert any("Commerce" in t or "Finance" in t or "Management" in t for t in pathway_titles)

        # Check career connections
        career_names = [c["name"] for c in guidance["career_connections"]]
        assert any("Accountant" in name or "Financial" in name for name in career_names)


# ==========================================
# 3. Career-Specific Education Guidance (?career_id=...)
# ==========================================

def test_valid_career_id_produces_career_specific_guidance(app):
    """Test that specifying career_id tailors education pathways toward that target career."""
    with app.app_context():
        profile, err = ProfileService.create_profile({
            "full_name": "Targeted Student",
            "email": "targeted@example.com",
            "education_level": "Undergraduate",
            "qualification": "B.Sc in Computing"
        })
        assert err is None

        # Query with target career: machine-learning-engineer
        guidance, error = EducationService.get_pathways_for_profile(
            profile_id=profile.id,
            career_id="machine-learning-engineer"
        )
        assert error is None
        assert guidance["success"] is True
        assert guidance["selected_career"] is not None
        assert guidance["selected_career"]["id"] == "machine-learning-engineer"
        assert "Machine Learning" in guidance["selected_career"]["name"]

        # Pathways should connect to the target career
        for p in guidance["pathways"]:
            why_text = " ".join(p["why_identified"])
            assert "Machine Learning" in why_text or "Data & AI" in why_text or "target" in why_text.lower()


def test_invalid_career_id_returns_clean_error(app):
    """Test that querying with an invalid career_id returns an appropriate error."""
    with app.app_context():
        profile, err = ProfileService.create_profile({
            "full_name": "Test Student",
            "email": "test.err@example.com"
        })
        assert err is None

        guidance, error = EducationService.get_pathways_for_profile(
            profile_id=profile.id,
            career_id="invalid-career-slug-xyz"
        )
        assert guidance is None
        assert "not found in catalogue" in error.lower()


def test_missing_profile_returns_404_error(app):
    """Test that requesting education pathways for non-existent profile returns error."""
    with app.app_context():
        guidance, error = EducationService.get_pathways_for_profile(999999)
        assert guidance is None
        assert "not found" in error.lower()


# ==========================================
# 4. Incomplete & Safe Edge Case Tests
# ==========================================

def test_incomplete_profile_handled_safely(app):
    """Test profile with no education or skills returns guidance safely with explicit gaps."""
    with app.app_context():
        profile, err = ProfileService.create_profile({
            "full_name": "Empty Edu Student",
            "email": "empty.edu@example.com"
        })
        assert err is None

        guidance, error = EducationService.get_pathways_for_profile(profile.id)
        assert error is None
        assert guidance["success"] is True
        assert len(guidance["pathways"]) > 0

        # Verify information gaps are explicitly captured
        gaps = guidance["information_gaps"]
        assert any("education level has not been recorded" in g.lower() for g in gaps)
        assert any("qualification information is incomplete" in g.lower() for g in gaps)
        assert any("no technical or practical skills" in g.lower() for g in gaps)
        assert any("no academic or career interests" in g.lower() for g in gaps)


def test_unknown_interests_do_not_crash_service(app):
    """Test that novel/unmapped interests are preserved and surfaced in information gaps."""
    with app.app_context():
        profile, err = ProfileService.create_profile({
            "full_name": "Novel Interest Edu",
            "email": "novel.edu@example.com",
            "interests": ["Underwater Basket Weaving", "Exoplanet Landscaping"]
        })
        assert err is None

        guidance, error = EducationService.get_pathways_for_profile(profile.id)
        assert error is None
        assert guidance["success"] is True

        gaps = " ".join(guidance["information_gaps"])
        assert "Underwater Basket Weaving" in gaps or "could not be mapped" in gaps


# ==========================================
# 5. Explainability & Strict Neutrality Tests
# ==========================================

def test_explainability_and_no_unsupported_precision(app):
    """Verify that no fake percentages or certainty guarantees are produced."""
    with app.app_context():
        profile, err = ProfileService.create_profile({
            "full_name": "Neutrality Check",
            "email": "neutrality.check@example.com",
            "education_level": "Undergraduate",
            "qualification": "B.Tech Computer Science",
            "skills": ["Python", "SQL"],
            "interests": ["Python", "Cloud Computing"]
        })
        assert err is None

        guidance, error = EducationService.get_pathways_for_profile(profile.id)
        assert error is None

        raw_json = json.dumps(guidance).lower()

        # Prohibited certainty language
        assert "% match" not in raw_json
        assert "guaranteed" not in raw_json
        assert "perfect pathway" not in raw_json
        assert "100% suitable" not in raw_json
        assert "you will succeed" not in raw_json

        # Verified factual explainability
        for p in guidance["pathways"]:
            assert len(p["why_identified"]) >= 2
            assert p["admission_prerequisites"]
            assert len(p["limitations"]) > 0


# ==========================================
# 6. REST API Endpoints Tests
# ==========================================

def test_api_education_health(client):
    """Test GET /api/education/health returns healthy."""
    res = client.get('/api/education/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["module"] == "education_pathway_guidance"


def test_api_education_catalogue_list(client):
    """Test GET /api/education/catalogue returns catalogue and available levels."""
    res = client.get('/api/education/catalogue')
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["total"] == len(EDUCATION_PATHWAY_CATALOGUE)
    assert len(data["available_levels"]) >= 4
    assert len(data["pathways"]) == len(EDUCATION_PATHWAY_CATALOGUE)


def test_api_education_catalogue_filter(client):
    """Test GET /api/education/catalogue with ?education_level=Diploma."""
    res = client.get('/api/education/catalogue?education_level=Diploma')
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["total"] > 0
    assert all(
        p["current_education_level"] == "Diploma" or "diploma" in p["possible_next_step"].lower()
        for p in data["pathways"]
    )


def test_api_education_catalogue_detail(client):
    """Test GET /api/education/catalogue/<pathway_id> for valid and invalid pathway IDs."""
    # Valid
    res = client.get('/api/education/catalogue/diploma-to-btech-lateral')
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["pathway"]["id"] == "diploma-to-btech-lateral"

    # Invalid (404)
    res_404 = client.get('/api/education/catalogue/invalid-pathway-id-999')
    assert res_404.status_code == 404
    data_404 = res_404.get_json()
    assert data_404["success"] is False
    assert "not found" in data_404["error"].lower()


def test_api_education_pathways_for_profile(client):
    """Test GET /api/education/pathways/<profile_id> via client."""
    # Create profile
    res_create = client.post('/api/profile', json={
        "full_name": "API Edu Student",
        "email": "api.edu@example.com",
        "education_level": "Undergraduate",
        "qualification": "B.Tech Mechanical Engineering",
        "interests": ["Mechanical Engineering", "Robotics"],
        "skills": ["CAD", "Thermodynamics"]
    })
    assert res_create.status_code == 201
    profile_id = res_create.get_json()["profile"]["id"]

    # Call education pathways API
    res = client.get(f'/api/education/pathways/{profile_id}')
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["profile_id"] == profile_id
    assert data["student_name"] == "API Edu Student"
    assert "pathways" in data
    assert len(data["pathways"]) > 0
    assert "current_education" in data
    assert "career_connections" in data
    assert "information_gaps" in data
    assert "limitations" in data


def test_api_education_pathways_with_career_id(client):
    """Test GET /api/education/pathways/<profile_id>?career_id=software-developer."""
    res_create = client.post('/api/profile', json={
        "full_name": "Career Targeted Edu",
        "email": "career.targeted@example.com",
        "education_level": "Higher Secondary",
        "qualification": "12th Grade (PCM)",
        "interests": ["Python", "Web Development"]
    })
    assert res_create.status_code == 201
    profile_id = res_create.get_json()["profile"]["id"]

    res = client.get(f'/api/education/pathways/{profile_id}?career_id=software-developer')
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["selected_career"]["id"] == "software-developer"
    assert len(data["pathways"]) > 0


def test_api_education_pathways_missing_profile(client):
    """Test GET /api/education/pathways/999999 returns 404."""
    res = client.get('/api/education/pathways/999999')
    assert res.status_code == 404
    data = res.get_json()
    assert data["success"] is False
    assert "not found" in data["error"].lower()


def test_api_education_pathways_invalid_career_id(client):
    """Test GET /api/education/pathways/<profile_id>?career_id=invalid returns 404."""
    res_create = client.post('/api/profile', json={
        "full_name": "Invalid Career Query",
        "email": "invalid.career@example.com"
    })
    profile_id = res_create.get_json()["profile"]["id"]

    res = client.get(f'/api/education/pathways/{profile_id}?career_id=non-existent-career')
    assert res.status_code == 404
    data = res.get_json()
    assert data["success"] is False
    assert "not found in catalogue" in data["error"].lower()
