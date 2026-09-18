"""
Unit and Integration Tests for Education Pathway Dashboard UI (Member 2 - Step 7).
Tests dashboard route loading, student profile context, current education display,
multi-stage visual pathway, higher study/specializations, career connections, target career mode,
information gaps, catalogue exploration, error states, and strict neutrality.
"""

import pytest
from profile.services import ProfileService
from education.catalogue import EDUCATION_PATHWAY_CATALOGUE
from career.catalogue import CAREER_CATALOGUE


def test_education_dashboard_route_loads(client):
    """Test that /education/pathways route responds successfully."""
    res = client.get('/education/pathways')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert "Education Pathway Guidance" in html


def test_education_dashboard_valid_profile(client):
    """Test dashboard rendering with complete student profile."""
    # Create profile
    res = client.post('/api/profile', json={
        "full_name": "Siddharth Verma",
        "email": "siddharth@example.com",
        "education_level": "Undergraduate",
        "qualification": "B.Tech in Computer Science",
        "degree_details": {
            "degree_name": "B.Tech",
            "major": "Computer Science",
            "institution": "IIT Hyderabad",
            "gpa": "9.1"
        },
        "skills": ["Python", "Algorithms", "Git"],
        "interests": ["Artificial Intelligence", "Machine Learning"],
        "career_goals": "Machine Learning Engineer"
    })
    assert res.status_code == 201
    profile_id = res.get_json()["profile"]["id"]

    # Request dashboard
    ui_res = client.get(f'/education/pathways/{profile_id}')
    assert ui_res.status_code == 200
    html = ui_res.data.decode('utf-8')

    # 1. Header & Identity
    assert "Siddharth Verma" in html
    assert "Education Pathway Guidance" in html
    assert "Informational Educational Guidance" not in html

    # 2. Current Education Section
    assert "Your Recorded Educational Standing" in html
    assert "Undergraduate" in html
    assert "B.Tech in Computer Science" in html
    assert "IIT Hyderabad" in html
    assert "9.1" in html

    # 3. Core Visual Pathway Flow (Multi-Stage Model)
    assert "Multi-Stage Educational Progression Model" in html
    assert "Stage 1" in html
    assert "Stage 2" in html
    assert "Stage 3" in html
    assert "Stage 4" in html

    # 4. Progression Flow Content (What to Study Next, Skills/Course Needed)
    assert "Higher Study Options" in html
    assert "Specialization Areas" in html
    assert "Admission Prerequisites &amp; Considerations" in html or "Admission Prerequisites & Considerations" in html

    # 5. Career Connections
    assert "Connected Career Pathways" in html

    # 6. Actionable Next Step Section & Streamlined UI (clutter, large catalogues, and long explanations removed)
    assert "What Should I Do Next?" in html
    assert "Explore Complete Education Pathway Catalogue" not in html
    assert "Why This Pathway Was Identified" not in html


def test_education_dashboard_defaults_to_first_profile(client):
    """Test /education/pathways without ID defaults to first available profile."""
    client.post('/api/profile', json={
        "full_name": "First Edu Student",
        "email": "first.edu@example.com",
        "education_level": "Undergraduate",
        "qualification": "B.Sc Physics"
    })

    ui_res = client.get('/education/pathways')
    assert ui_res.status_code == 200
    html = ui_res.data.decode('utf-8')
    assert "First Edu Student" in html
    assert "Your Recorded Educational Standing" in html


def test_education_dashboard_invalid_profile(client):
    """Test /education/pathways/<invalid_id> returns friendly 404 error."""
    ui_res = client.get('/education/pathways/999999')
    assert ui_res.status_code == 404
    html = ui_res.data.decode('utf-8')
    assert "Notice" in html or "not found" in html.lower()


def test_education_dashboard_empty_system_state(client):
    """Test /education/pathways when no profiles exist displays registration prompt."""
    ui_res = client.get('/education/pathways')
    assert ui_res.status_code == 200
    html = ui_res.data.decode('utf-8')
    assert "No Student Profiles Registered" in html or "Create Your Student Profile" in html


def test_education_dashboard_information_gaps_rendered(client):
    """Test that incomplete profile renders information gaps with update action."""
    res = client.post('/api/profile', json={
        "full_name": "Gaps Edu Student",
        "email": "gaps.edu@example.com"
        # Missing qualification, level, skills, interests
    })
    profile_id = res.get_json()["profile"]["id"]

    ui_res = client.get(f'/education/pathways/{profile_id}')
    assert ui_res.status_code == 200
    html = ui_res.data.decode('utf-8')

    assert "Profile Information Gaps &amp; Recommendations" in html or "Profile Information Gaps" in html
    assert "Update Profile to Fill Information Gaps" in html


def test_education_dashboard_target_career_mode(client):
    """Test exploring education pathways for a selected target career (?career_id=...)."""
    res = client.post('/api/profile', json={
        "full_name": "Target Career Student",
        "email": "target.career@example.com",
        "education_level": "Undergraduate",
        "qualification": "B.Tech in Artificial Intelligence"
    })
    profile_id = res.get_json()["profile"]["id"]

    # Target: software-developer
    ui_res = client.get(f'/education/pathways/{profile_id}?career_id=software-developer')
    assert ui_res.status_code == 200
    html = ui_res.data.decode('utf-8')

    assert "Target Career: Software Developer" in html
    assert "Clear Target Career (View All Pathways)" in html


def test_education_dashboard_invalid_career_target(client):
    """Test targeting an invalid career ID returns 404 error state."""
    res = client.post('/api/profile', json={
        "full_name": "Target Error Student",
        "email": "target.error@example.com"
    })
    profile_id = res.get_json()["profile"]["id"]

    ui_res = client.get(f'/education/pathways/{profile_id}?career_id=non-existent-career')
    assert ui_res.status_code == 404
    html = ui_res.data.decode('utf-8')
    assert "not found in catalogue" in html.lower()


def test_education_dashboard_blueprint_alias(client):
    """Test /api/education/ui/<id> works identically to /education/pathways/<id>."""
    res = client.post('/api/profile', json={
        "full_name": "Alias Edu Student",
        "email": "alias.edu@example.com",
        "education_level": "Diploma",
        "qualification": "Diploma in Mechanical Engineering"
    })
    profile_id = res.get_json()["profile"]["id"]

    ui_res = client.get(f'/api/education/ui/{profile_id}')
    assert ui_res.status_code == 200
    html = ui_res.data.decode('utf-8')
    assert "Alias Edu Student" in html
    assert "Diploma" in html


def test_education_dashboard_no_unsupported_precision(client):
    """Verify that no fake percentage scores or certainty guarantees appear in HTML."""
    res = client.post('/api/profile', json={
        "full_name": "Strict Neutrality Student",
        "email": "strict.neutrality@example.com",
        "education_level": "Undergraduate",
        "qualification": "B.Com Finance"
    })
    profile_id = res.get_json()["profile"]["id"]

    ui_res = client.get(f'/education/pathways/{profile_id}')
    assert ui_res.status_code == 200
    html = ui_res.data.decode('utf-8').lower()

    assert "% match" not in html
    assert "perfect pathway" not in html
    assert "guaranteed admission" not in html
    assert "100% suitable" not in html
    assert "you will succeed" not in html


def test_simplified_education_pathways_progression_flow(client):
    """
    Verify:
    1. Only the relevant education pathway based on student's current qualification is shown.
    2. Clearly shows the 4-step progression:
       Current Education → What to Study Next → Skills / Courses Needed → Career Connection.
    3. Actionable 'What Should I Do Next?' section is prominent.
    4. Unrelated pathways, large catalogues, repeated cards, and long explanations are removed.
    """
    res = client.post('/api/profile', json={
        "full_name": "Priya Sharma",
        "email": "priya.sharma@example.com",
        "education_level": "Undergraduate",
        "qualification": "B.Tech Computer Science",
        "degree_details": {
            "degree_name": "B.Tech",
            "institution": "National Institute of Technology",
            "gpa": "8.8"
        },
        "skills": ["Python", "SQL", "Pandas"],
        "career_goals": "Machine Learning Engineer"
    })
    assert res.status_code == 201
    profile_id = res.get_json()["profile"]["id"]

    ui_res = client.get(f'/education/pathways/{profile_id}')
    assert ui_res.status_code == 200
    html = ui_res.data.decode('utf-8')

    # 1. Shows 4-step progression clearly
    assert "Current Education" in html
    assert "What to Study Next" in html
    assert "Skills / Courses Needed" in html
    assert "Career Connection" in html

    # 2. Shows student's current qualification & standing
    assert "B.Tech Computer Science" in html
    assert "National Institute of Technology" in html

    # 3. Actionable Next Step: What Should I Do Next?
    assert "What Should I Do Next?" in html
    assert "Check Eligibility &amp; Criteria" in html or "Check Eligibility & Criteria" in html
    assert "Prepare Core Topics" in html

    # 4. Large catalogue, clutter, and verbose explanations removed
    assert "Explore Complete Education Pathway Catalogue" not in html
    assert "Why This Pathway Was Identified" not in html

