"""
Unit and Integration Tests for Career Guidance Engine (Member 2 - Step 4).
Tests catalogue integrity, profile evaluation, interest intelligence integration,
skill and education alignment, explainability, safety limitations, and REST endpoints.
"""

import json
import pytest
from career.catalogue import CAREER_CATALOGUE, CATALOGUE_BY_ID, CATALOGUE_BY_DOMAIN
from career.services import CareerService
from profile.models import StudentProfile
from profile.services import ProfileService
from profile.interest_intelligence import CAREER_DOMAINS


# ==========================================
# 1. Career Catalogue Tests
# ==========================================

def test_career_catalogue_structure_and_fields():
    """Verify that catalogue loads, is non-empty, and all entries contain required keys."""
    assert len(CAREER_CATALOGUE) > 0
    required_fields = [
        "id", "name", "domain", "description", "related_interests",
        "important_skills", "typical_education", "education_levels_supported", "progression"
    ]
    for career in CAREER_CATALOGUE:
        for field in required_fields:
            assert field in career, f"Missing {field} in career {career.get('id')}"
            assert career[field], f"Field {field} is empty in career {career.get('id')}"


def test_career_catalogue_covers_all_domains():
    """Verify that all standard career domains are represented in the catalogue."""
    represented_domains = set(c["domain"] for c in CAREER_CATALOGUE)
    for domain in CAREER_DOMAINS:
        assert domain in represented_domains, f"Domain '{domain}' not represented in catalogue"


def test_catalogue_service_filtering_and_lookup():
    """Test CareerService.get_career_catalogue and get_career_by_id."""
    # Lookup by valid ID
    sw_dev = CareerService.get_career_by_id("software-developer")
    assert sw_dev is not None
    assert sw_dev["name"] == "Software Developer"
    assert sw_dev["domain"] == "Technology & Software"

    # Lookup by invalid ID
    invalid = CareerService.get_career_by_id("non-existent-career-xyz")
    assert invalid is None

    # Filter by domain
    tech_careers = CareerService.get_career_catalogue(domain="Technology & Software")
    assert len(tech_careers) > 0
    assert all(
        c["domain"] == "Technology & Software" or "Technology & Software" in c.get("related_domains", [])
        for c in tech_careers
    )

    # Legacy alias
    sector_careers = CareerService.get_pathways_by_sector("Data & AI")
    assert len(sector_careers) > 0


# ==========================================
# 2. Profile Integration & Alignment Tests
# ==========================================

def test_guidance_for_complete_profile(app):
    """Test guidance generation for a comprehensive student profile with matching interests, skills, education, and goals."""
    with app.app_context():
        profile, err = ProfileService.create_profile({
            "full_name": "Arjun Sharma",
            "email": "arjun.sharma@example.com",
            "education_level": "Undergraduate",
            "qualification": "B.Tech in Computer Science & Engineering",
            "skills": ["Python", "SQL", "Git", "Data Structures"],
            "interests": ["Python", "Machine Learning", "Artificial Intelligence"],
            "career_goals": "Machine Learning Engineer"
        })
        assert err is None
        assert profile is not None

        guidance, error = CareerService.generate_guidance_for_profile(profile.id)
        assert error is None
        assert guidance["success"] is True
        assert guidance["student_name"] == "Arjun Sharma"
        assert guidance["profile_id"] == profile.id
        assert guidance["total_pathways_evaluated"] == len(CAREER_CATALOGUE)
        assert guidance["matched_pathways_count"] > 0

        # Top pathways should include Data & AI or Tech careers with High Alignment
        career_names = [c["name"] for c in guidance["careers"]]
        assert any("Machine Learning" in name or "Data" in name or "Software" in name for name in career_names)

        top_career = guidance["careers"][0]
        assert top_career["alignment_level"] in ["High Alignment", "Moderate Alignment"]
        assert len(top_career["why_identified"]) >= 3
        assert len(top_career["matched_skills"]) > 0
        assert len(top_career["matched_interests"]) > 0


def test_guidance_missing_profile(app):
    """Test guidance generation for non-existent profile returns clean error."""
    with app.app_context():
        guidance, error = CareerService.generate_guidance_for_profile(999999)
        assert guidance is None
        assert "not found" in error.lower()


# ==========================================
# 3. Incomplete & Edge Case Profile Tests
# ==========================================

def test_guidance_for_empty_profile(app):
    """Test an empty/minimal profile produces exploratory guidance without crashing."""
    with app.app_context():
        profile, err = ProfileService.create_profile({
            "full_name": "Minimal Student",
            "email": "minimal@example.com"
        })
        assert err is None

        guidance, error = CareerService.generate_guidance_for_profile(profile.id)
        assert error is None
        assert guidance["success"] is True
        assert len(guidance["careers"]) > 0

        # Verify limitations are explicitly articulated
        limitations = guidance["guidance_limitations"]
        assert any("no interests" in lim.lower() for lim in limitations)
        assert any("no technical or professional skills" in lim.lower() for lim in limitations)
        assert any("education level" in lim.lower() for lim in limitations)
        assert any("no stated career goal" in lim.lower() for lim in limitations)

        # Confirm pathways provide exploratory guidance without fake match data
        first_career = guidance["careers"][0]
        assert first_career["alignment_level"] == "Exploratory Alignment"


def test_guidance_with_unknown_interests(app):
    """Test that novel or unmapped interests are handled safely without crashing."""
    with app.app_context():
        profile, err = ProfileService.create_profile({
            "full_name": "Novel Interest Student",
            "email": "novel@example.com",
            "interests": ["Quantum Cryptography Knitting", "Sub-orbital Gardening"]
        })
        assert err is None

        guidance, error = CareerService.generate_guidance_for_profile(profile.id)
        assert error is None
        assert guidance["success"] is True
        
        # Verify unknown interests recorded in interest intelligence & limitations
        intel = guidance["interest_intelligence"]
        assert len(intel["unmapped_interests"]) == 2
        limitations = " ".join(guidance["guidance_limitations"])
        assert "Quantum Cryptography Knitting" in limitations or "not indexed" in limitations


def test_guidance_with_skills_no_interests(app):
    """Test that skills alone can surface relevant pathways when interests are empty."""
    with app.app_context():
        profile, err = ProfileService.create_profile({
            "full_name": "Practical Mechanic",
            "email": "mechanic@example.com",
            "skills": ["Hardware Diagnostics", "Network Cabling", "Troubleshooting"]
        })
        assert err is None

        guidance, error = CareerService.generate_guidance_for_profile(profile.id)
        assert error is None
        assert guidance["success"] is True

        career_ids = [c["id"] for c in guidance["careers"]]
        assert "systems-network-technician" in career_ids


def test_guidance_career_goal_influence(app):
    """Test that stated career goals influence alignment level and explanations."""
    with app.app_context():
        profile, err = ProfileService.create_profile({
            "full_name": "Aspiring Lawyer",
            "email": "lawyer@example.com",
            "career_goals": "Legal Advocate and Corporate Lawyer"
        })
        assert err is None

        guidance, error = CareerService.generate_guidance_for_profile(profile.id)
        assert error is None
        assert guidance["success"] is True

        career_names = [c["name"] for c in guidance["careers"]]
        assert any("Lawyer" in name or "Legal" in name for name in career_names)

        legal_career = next(c for c in guidance["careers"] if "Lawyer" in c["name"])
        why_text = " ".join(legal_career["why_identified"])
        assert "Legal Advocate" in why_text or "goal" in why_text.lower()


# ==========================================
# 4. Explainability & No Unsupported Precision Tests
# ==========================================

def test_explainability_no_unsupported_precision(app):
    """Verify that no fake percentages or certainty guarantees are produced."""
    with app.app_context():
        profile, err = ProfileService.create_profile({
            "full_name": "Test Explainable",
            "email": "explainable@example.com",
            "interests": ["Python", "Web Development"],
            "skills": ["HTML/CSS", "JavaScript"],
            "education_level": "Undergraduate",
            "qualification": "B.Sc Computer Science"
        })
        assert err is None

        guidance, error = CareerService.generate_guidance_for_profile(profile.id)
        assert error is None

        raw_json = json.dumps(guidance).lower()

        # Prohibited terms according to specification
        assert "% match" not in raw_json
        assert "perfect career" not in raw_json
        assert "guarantee" not in raw_json
        assert "you will succeed" not in raw_json

        # Verified explainable factor keys are present for each career
        for c in guidance["careers"]:
            factors = c["alignment_factors"]
            assert "interest_alignment" in factors
            assert "skill_alignment" in factors
            assert "education_alignment" in factors
            assert "goal_alignment" in factors
            assert len(c["why_identified"]) >= 3
            assert c["alignment_level"] in ["High Alignment", "Moderate Alignment", "Exploratory Alignment"]


# ==========================================
# 5. REST API Endpoints Tests
# ==========================================

def test_api_career_health(client):
    """Test GET /api/career/health returns healthy."""
    res = client.get('/api/career/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["module"] == "career_pathway_guidance"


def test_api_career_catalogue_list(client):
    """Test GET /api/career/catalogue returns catalogue and available domains."""
    res = client.get('/api/career/catalogue')
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["total"] == len(CAREER_CATALOGUE)
    assert len(data["available_domains"]) >= 14
    assert len(data["careers"]) == len(CAREER_CATALOGUE)


def test_api_career_catalogue_filter_by_domain(client):
    """Test GET /api/career/catalogue?domain=Healthcare."""
    res = client.get('/api/career/catalogue?domain=Healthcare')
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["total"] > 0
    for c in data["careers"]:
        assert c["domain"] == "Healthcare" or "Healthcare" in c.get("related_domains", [])


def test_api_career_catalogue_detail(client):
    """Test GET /api/career/catalogue/<career_id> for valid and invalid career IDs."""
    # Valid
    res = client.get('/api/career/catalogue/software-developer')
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["career"]["id"] == "software-developer"
    assert "progression" in data["career"]

    # Invalid (404)
    res_404 = client.get('/api/career/catalogue/invalid-career-999')
    assert res_404.status_code == 404
    data_404 = res_404.get_json()
    assert data_404["success"] is False
    assert "not found" in data_404["error"].lower()


def test_api_career_guidance_for_profile(client):
    """Test GET /api/career/guidance/<profile_id> end-to-end via client."""
    # Create profile first
    create_res = client.post('/api/profile', json={
        "full_name": "API Test Student",
        "email": "apitest@example.com",
        "education_level": "Undergraduate",
        "qualification": "B.Com Accounting",
        "interests": ["Accounting & Finance", "Financial Analysis"],
        "skills": ["Excel", "Financial Modeling"]
    })
    assert create_res.status_code == 201
    profile_id = create_res.get_json()["profile"]["id"]

    # Request career guidance
    res = client.get(f'/api/career/guidance/{profile_id}')
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["profile_id"] == profile_id
    assert data["student_name"] == "API Test Student"
    assert "careers" in data
    assert len(data["careers"]) > 0

    # Ensure Finance/Commerce career is at the top
    top_career = data["careers"][0]
    assert top_career["domain"] == "Finance & Commerce"
    assert top_career["alignment_level"] == "High Alignment"


def test_api_career_guidance_missing_profile(client):
    """Test GET /api/career/guidance/<profile_id> with invalid ID returns 404."""
    res = client.get('/api/career/guidance/888888')
    assert res.status_code == 404
    data = res.get_json()
    assert data["success"] is False
    assert "not found" in data["error"].lower()


def test_api_career_guidance_invalid_route_param(client):
    """Test GET /api/career/guidance/<invalid> returns 404."""
    res = client.get('/api/career/guidance/invalid-string-id')
    assert res.status_code == 404


def test_guidance_response_full_contract(app):
    """Verify all fields required by Step 4 specification are present in response."""
    with app.app_context():
        profile, err = ProfileService.create_profile({
            "full_name": "Contract Verification Student",
            "email": "contract@example.com",
            "education_level": "Undergraduate",
            "qualification": "B.Tech Information Technology",
            "skills": ["Python", "Algorithms", "Git"],
            "interests": ["Python", "Web Development"],
            "career_goals": "Software Developer"
        })
        assert err is None

        guidance, error = CareerService.generate_guidance_for_profile(profile.id)
        assert error is None
        assert guidance["success"] is True
        assert "profile_id" in guidance
        assert "domains" in guidance
        assert "careers" in guidance

        for career in guidance["careers"]:
            assert "name" in career
            assert "domain" in career
            assert "description" in career
            assert "why_identified" in career
            assert isinstance(career["why_identified"], list)
            assert "related_interests" in career
            assert "relevant_skills" in career
            assert "education_considerations" in career
            assert "important_skills" in career
            assert "progression" in career


def test_guidance_education_levels_reflection(app):
    """Test that student education levels (e.g. Diploma vs Undergraduate) are appropriately reflected."""
    with app.app_context():
        # Case A: Diploma student
        p_diploma, _ = ProfileService.create_profile({
            "full_name": "Diploma Tech Student",
            "email": "diploma@example.com",
            "education_level": "Diploma",
            "qualification": "Diploma in Mechanical Engineering",
            "skills": ["CAD Drafting", "Component Assembly"],
            "interests": ["Mechanical Engineering"]
        })
        g_diploma, _ = CareerService.generate_guidance_for_profile(p_diploma.id)
        assert g_diploma["success"] is True
        mech_career = next(c for c in g_diploma["careers"] if "Mechanical" in c["name"])
        edu_why = [w for w in mech_career["why_identified"] if "Education connection" in w]
        assert len(edu_why) > 0
        assert "Diploma" in edu_why[0]


def test_guidance_multiple_interests_across_domains(app):
    """Test that diverse multi-domain interests surface pathways from corresponding domains."""
    with app.app_context():
        profile, _ = ProfileService.create_profile({
            "full_name": "Interdisciplinary Student",
            "email": "interdisciplinary@example.com",
            "interests": ["Civil Engineering", "Graphic Design", "Medicine"],
            "skills": ["Site Surveying", "Photoshop"]
        })
        guidance, _ = CareerService.generate_guidance_for_profile(profile.id)
        assert guidance["success"] is True

        domains_detected = guidance["interest_intelligence"]["detected_domains"]
        assert "Engineering" in domains_detected
        assert "Design & Creative" in domains_detected
        assert "Healthcare" in domains_detected

        matched_domains = set(c["domain"] for c in guidance["careers"])
        assert "Engineering" in matched_domains or "Design & Creative" in matched_domains


# ==========================================
# 6. Career Guidance UI Dashboard Tests (Step 5)
# ==========================================

def test_career_guidance_ui_valid_profile(client):
    """Test Career Guidance UI dashboard loads successfully for a valid profile."""
    # Create profile
    res = client.post('/api/profile', json={
        "full_name": "Dev Dashboard Student",
        "email": "dashboard.student@example.com",
        "education_level": "Undergraduate",
        "qualification": "B.Tech in Artificial Intelligence",
        "skills": ["Python", "PyTorch", "SQL", "Git"],
        "interests": ["Artificial Intelligence", "Machine Learning"],
        "career_goals": "Machine Learning Engineer"
    })
    assert res.status_code == 201
    profile_id = res.get_json()["profile"]["id"]

    # Request UI dashboard
    ui_res = client.get(f'/career/guidance/{profile_id}')
    assert ui_res.status_code == 200
    html = ui_res.data.decode('utf-8')

    # 1. Header & Identity
    assert "Dev Dashboard Student" in html
    assert "Career Pathway Guidance" in html
    assert "Informational Decision-Support" not in html
    assert "Member 2" not in html

    # 2. Main Target Career & Short Reason
    assert "Main Target Career" in html
    assert "Machine Learning &amp; AI Engineer" in html or "Machine Learning & AI Engineer" in html
    assert "Matches your career goal and current skills." in html

    # 3. Target Career Skills (Missing Skills)
    assert "Target Career Skills to Learn (Missing Skills)" in html

    # 4. Jobs Based on Current Skills
    assert "Jobs Based on Your Current Skills" in html
    assert "Python" in html
    assert "Matching Skills:" in html

    # 5. What To Do Next
    assert "What To Do Next" in html

    # 6. Verify removed sections (Simplified UI)
    assert "Why This Pathway Was Identified" not in html
    assert "Explore Complete Career Catalogue" not in html


def test_career_guidance_ui_invalid_profile(client):
    """Test Career Guidance UI with invalid profile ID returns 404 and friendly error."""
    ui_res = client.get('/career/guidance/999999')
    assert ui_res.status_code == 404
    html = ui_res.data.decode('utf-8')
    assert "Profile Unavailable" in html or "not found" in html.lower()


def test_career_guidance_ui_empty_system_state(client):
    """Test Career Guidance UI when no profiles exist shows clean registration prompt."""
    ui_res = client.get('/career/guidance')
    assert ui_res.status_code == 200
    html = ui_res.data.decode('utf-8')
    assert "No Student Profiles Registered" in html or "Create Your Student Profile" in html


def test_career_guidance_ui_defaults_to_first_profile(client):
    """Test /career/guidance without ID defaults to first profile when profiles exist."""
    # Create profile
    client.post('/api/profile', json={
        "full_name": "First Default Student",
        "email": "first.default@example.com",
        "education_level": "Undergraduate",
        "qualification": "B.Sc Computer Science",
        "interests": ["Python", "Web Development"]
    })

    ui_res = client.get('/career/guidance')
    assert ui_res.status_code == 200
    html = ui_res.data.decode('utf-8')
    assert "First Default Student" in html
    assert "Career Pathway Guidance" in html


def test_career_guidance_ui_limitations_rendered(client):
    """Test that guidance limitations and profile gaps are prominently displayed."""
    # Create partial profile (no skills, no education)
    res = client.post('/api/profile', json={
        "full_name": "Gaps Student",
        "email": "gaps@example.com",
        "interests": ["Cybersecurity"]
    })
    profile_id = res.get_json()["profile"]["id"]

    ui_res = client.get(f'/career/guidance/{profile_id}')
    assert ui_res.status_code == 200
    html = ui_res.data.decode('utf-8')
    assert "Profile Information Gaps &amp; Enhancement Tips" in html or "Profile Information Gaps" in html
    assert "Update Profile to Fill Information Gaps" in html


def test_career_guidance_ui_no_unsupported_precision(client):
    """Verify that no fake percentage scores or certainty guarantees appear in dashboard HTML."""
    res = client.post('/api/profile', json={
        "full_name": "Neutrality Student",
        "email": "neutrality@example.com",
        "interests": ["Data Science", "Python"],
        "skills": ["SQL", "Python"]
    })
    profile_id = res.get_json()["profile"]["id"]

    ui_res = client.get(f'/career/guidance/{profile_id}')
    assert ui_res.status_code == 200
    html = ui_res.data.decode('utf-8').lower()

    assert "% match" not in html
    assert "perfect career" not in html
    assert "guaranteed job" not in html
    assert "you will succeed" not in html


def test_career_guidance_ui_blueprint_alias(client):
    """Verify /api/career/ui/<id> works identically to /career/guidance/<id>."""
    res = client.post('/api/profile', json={
        "full_name": "Alias Student",
        "email": "alias@example.com",
        "interests": ["Civil Engineering"]
    })
    profile_id = res.get_json()["profile"]["id"]

    ui_res = client.get(f'/api/career/ui/{profile_id}')
    assert ui_res.status_code == 200
    html = ui_res.data.decode('utf-8')
    assert "Alias Student" in html


def test_simplified_career_guidance_machine_learning_engineer_goal(client):
    """
    Verify:
    1. Machine Learning Engineer goal displayed clearly as main target career.
    2. Jobs based on current skills (e.g. Python, SQL, Pandas, NumPy) show ONLY matching jobs.
    3. Non-matching jobs (e.g. Civil Engineer, Registered Nurse) are NOT shown as current matches.
    4. Target career missing skills shown simply.
    5. Reason is one short sentence, no large 'Why this path was identified'.
    6. Only relevant education step shown, no large catalogue.
    """
    res = client.post('/api/profile', json={
        "full_name": "ML Target Student",
        "email": "ml.target@example.com",
        "education_level": "Undergraduate",
        "qualification": "B.Tech Computer Science",
        "skills": ["Python", "SQL", "Pandas", "NumPy"],
        "career_goals": "Machine Learning Engineer"
    })
    assert res.status_code == 201
    profile_id = res.get_json()["profile"]["id"]

    ui_res = client.get(f'/career/guidance/{profile_id}')
    assert ui_res.status_code == 200
    html = ui_res.data.decode('utf-8')

    # 1. Career Goal: clearly shown as main target career
    assert "Main Target Career" in html
    assert "Machine Learning &amp; AI Engineer" in html or "Machine Learning & AI Engineer" in html
    assert "Machine Learning Engineer" in html

    # 2. Short reason: one short sentence
    assert "Matches your career goal and current skills." in html
    assert "Why This Pathway Was Identified" not in html

    # 3. Target Career Skills: missing skills shown
    assert "Target Career Skills to Learn (Missing Skills)" in html
    assert "Model Deployment &amp; MLOps" in html or "Model Deployment & MLOps" in html or "Linear Algebra" in html

    # 4. Jobs Based on Current Skills: only matching jobs
    assert "Jobs Based on Your Current Skills" in html
    assert "Data Scientist" in html
    assert "Data Analyst" in html
    # Non-matching careers must NOT be shown as skill matches
    assert "Civil Engineer" not in html
    assert "Registered Nurse" not in html
    assert "Commercial Pilot" not in html

    # 5. Education Step: relevant step only, no large catalogue
    assert "Relevant Education Step" in html
    assert "Undergraduate degree meets the standard educational baseline" in html
    assert "Explore Complete Career Catalogue" not in html


def test_simplified_career_guidance_empty_skills_handled_safely(client):
    """Verify that a student with no skills sees a prompt to add skills and no false job recommendations."""
    res = client.post('/api/profile', json={
        "full_name": "No Skills Student",
        "email": "noskills@example.com",
        "education_level": "Undergraduate",
        "skills": [],
        "career_goals": "Data Scientist"
    })
    assert res.status_code == 201
    profile_id = res.get_json()["profile"]["id"]

    ui_res = client.get(f'/career/guidance/{profile_id}')
    assert ui_res.status_code == 200
    html = ui_res.data.decode('utf-8')

    assert "No Jobs Match Current Skills Yet" in html
    assert "Add Skills to Your Profile" in html
    assert "Why This Pathway Was Identified" not in html
    assert "Explore Complete Career Catalogue" not in html



