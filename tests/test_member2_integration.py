"""
Member 2 Final Integration and Quality-Polish Test Suite.
Verifies the complete end-to-end flow:
Student Profile -> Interest Intelligence -> Career Guidance -> Education Pathways
including cross-module navigation, API contract consistency, incomplete profiles,
unknown interests, and usability constraints.
"""

import json
import pytest
from profile.models import StudentProfile
from profile.services import ProfileService
from career.catalogue import CAREER_CATALOGUE
from education.catalogue import EDUCATION_PATHWAY_CATALOGUE


def test_complete_student_end_to_end_journey(client):
    """
    Test 1: Complete student end-to-end workflow:
    1. Create complete profile
    2. Analyze interests via Interest Intelligence
    3. Retrieve Career Guidance
    4. Retrieve Education Pathways
    5. Filter Education Pathways by Target Career
    6. Verify cross-module links and profile ID preservation
    """
    profile_payload = {
        "full_name": "Integration Student",
        "email": "integration.student@university.edu",
        "education_level": "Undergraduate",
        "qualification": "B.Tech in Computer Science & Engineering",
        "degree_details": {
            "degree_name": "B.Tech",
            "major": "Computer Science & Engineering",
            "institution": "National Institute of Technology",
            "gpa": "9.2"
        },
        "skills": ["Python", "Machine Learning", "SQL", "Flask", "Docker"],
        "interests": ["Artificial Intelligence", "Cloud Computing"],
        "career_goals": "Machine Learning Engineer",
        "location": "Bengaluru, Karnataka",
        "preferred_locations": ["Bengaluru", "Hyderabad", "Remote"],
        "preferences": {
            "work_mode": "Hybrid",
            "higher_study": "Open to Higher Studies"
        }
    }

    # Step 1: Create Profile
    res_create = client.post('/api/profile', json=profile_payload)
    assert res_create.status_code == 201
    profile_data = res_create.get_json()["profile"]
    p_id = profile_data["id"]
    assert profile_data["full_name"] == "Integration Student"

    # Step 2: Analyze Interests
    res_intel = client.post('/api/profile/interests/analyze', json={"profile_id": p_id})
    assert res_intel.status_code == 200
    intel_data = res_intel.get_json()
    assert "Data & AI" in intel_data["domain_summary"]
    assert "Technology & Software" in intel_data["domain_summary"]
    assert len(intel_data["interests"]) >= 2

    # Step 3: View Career Guidance API & UI
    res_career_api = client.get(f'/api/career/guidance/{p_id}')
    assert res_career_api.status_code == 200
    career_data = res_career_api.get_json()
    assert career_data["success"] is True
    assert career_data["profile_id"] == p_id
    assert len(career_data["careers"]) > 0
    # Top career should match student's goal & domain
    career_names = [c["name"] for c in career_data["careers"]]
    assert any("Machine Learning" in name for name in career_names)

    res_career_ui = client.get(f'/career/guidance/{p_id}')
    assert res_career_ui.status_code == 200
    assert b"Integration Student" in res_career_ui.data
    assert b"Machine Learning" in res_career_ui.data

    # Step 4: View Education Pathways API & UI
    res_edu_api = client.get(f'/api/education/pathways/{p_id}')
    assert res_edu_api.status_code == 200
    edu_data = res_edu_api.get_json()
    assert edu_data["success"] is True
    assert edu_data["profile_id"] == p_id
    assert len(edu_data["pathways"]) > 0

    res_edu_ui = client.get(f'/education/pathways/{p_id}')
    assert res_edu_ui.status_code == 200
    assert b"Integration Student" in res_edu_ui.data
    assert b"Undergraduate" in res_edu_ui.data

    # Step 5: Filter Education Pathways by Target Career
    res_target_edu = client.get(f'/education/pathways/{p_id}?career_id=machine-learning-engineer')
    assert res_target_edu.status_code == 200
    assert b"Machine Learning &amp; AI Engineer" in res_target_edu.data or b"Machine Learning" in res_target_edu.data
    assert b"Clear Target Career" in res_target_edu.data

    # Step 6: Verify top-level profile routes
    res_profile_direct = client.get(f'/profile/{p_id}')
    assert res_profile_direct.status_code == 200
    assert b"Integration Student" in res_profile_direct.data


def test_cross_module_navigation_links(client):
    """
    Test 2: Verify cross-module links maintain profile context:
    - Profile UI contains links to Career Guidance and Education Pathways with p_id
    - Career Guidance contains link to Education Pathways with p_id
    - Education Pathways contains link to Career Guidance with p_id
    """
    res = client.post('/api/profile', json={
        "full_name": "Nav Student",
        "email": "nav.student@example.com",
        "education_level": "Undergraduate",
        "skills": ["Python"]
    })
    p_id = res.get_json()["profile"]["id"]

    # Profile UI check
    res_p = client.get(f'/api/profile/ui/{p_id}')
    assert res_p.status_code == 200
    assert f'/career/guidance/{p_id}'.encode() in res_p.data
    assert f'/education/pathways/{p_id}'.encode() in res_p.data

    # Career Guidance UI check
    res_c = client.get(f'/career/guidance/{p_id}')
    assert res_c.status_code == 200
    assert f'/education/pathways/{p_id}'.encode() in res_c.data
    assert f'/api/profile/ui/{p_id}'.encode() in res_c.data

    # Education Pathways UI check
    res_e = client.get(f'/education/pathways/{p_id}')
    assert res_e.status_code == 200
    assert f'/career/guidance/{p_id}'.encode() in res_e.data
    assert f'/api/profile/ui/{p_id}'.encode() in res_e.data


def test_incomplete_profile_handling_across_all_modules(client):
    """
    Test 3: Incomplete profile (missing education, skills, interests, goals):
    - Profile UI renders without error
    - Interest Intelligence returns empty structure without crashing
    - Career Guidance surfaces limitations instead of crashing
    - Education Pathways surfaces information gaps instead of crashing
    - No synthetic precision or fake metrics introduced
    """
    res = client.post('/api/profile', json={
        "full_name": "Incomplete Student",
        "email": "incomplete@example.com"
        # No education, qualification, skills, interests, goals
    })
    p_id = res.get_json()["profile"]["id"]

    # 1. Profile UI
    res_p = client.get(f'/api/profile/ui/{p_id}')
    assert res_p.status_code == 200
    assert b"Not provided yet" in res_p.data

    # 2. Interest Intelligence
    res_intel = client.post('/api/profile/interests/analyze', json={"profile_id": p_id})
    assert res_intel.status_code == 200
    assert res_intel.get_json()["interests"] == []

    # 3. Career Guidance API & UI
    res_c_api = client.get(f'/api/career/guidance/{p_id}')
    assert res_c_api.status_code == 200
    c_data = res_c_api.get_json()
    assert len(c_data["guidance_limitations"]) >= 3
    # Check that limitations mention missing fields
    limitations_text = " ".join(c_data["guidance_limitations"]).lower()
    assert "no interests" in limitations_text
    assert "no technical or professional skills" in limitations_text
    assert "education level" in limitations_text

    res_c_ui = client.get(f'/career/guidance/{p_id}')
    assert res_c_ui.status_code == 200
    assert b"Profile Information Gaps &amp; Enhancement Tips" in res_c_ui.data

    # 4. Education Pathways API & UI
    res_e_api = client.get(f'/api/education/pathways/{p_id}')
    assert res_e_api.status_code == 200
    e_data = res_e_api.get_json()
    assert len(e_data["information_gaps"]) >= 3
    gaps_text = " ".join(e_data["information_gaps"]).lower()
    assert "education level has not been recorded" in gaps_text
    assert "no technical or practical skills" in gaps_text

    res_e_ui = client.get(f'/education/pathways/{p_id}')
    assert res_e_ui.status_code == 200
    assert b"Profile Information Gaps &amp; Recommendations" in res_e_ui.data
    assert b"Education level not recorded" in res_e_ui.data


def test_unknown_and_novel_interests_handling(client):
    """
    Test 4: Unmapped/unknown interests:
    - Original terms preserved
    - Classified as unmapped/novel
    - Career Guidance does not crash and surfaces limitation
    - Education Pathways does not crash and surfaces gap
    """
    res = client.post('/api/profile', json={
        "full_name": "Novel Interest Student",
        "email": "novel.interests@example.com",
        "interests": ["Astrobiology", "Quantum Origami", "Python"]
    })
    p_id = res.get_json()["profile"]["id"]

    # Interest Intelligence
    res_intel = client.post('/api/profile/interests/analyze', json={"profile_id": p_id})
    assert res_intel.status_code == 200
    intel = res_intel.get_json()
    assert "Astrobiology" in intel["unmapped_interests"] or "Quantum Origami" in intel["unmapped_interests"]

    # Career Guidance
    res_c = client.get(f'/api/career/guidance/{p_id}')
    assert res_c.status_code == 200
    c_data = res_c.get_json()
    assert c_data["success"] is True
    # Verify unmapped interests are highlighted in limitations
    limits = " ".join(c_data["guidance_limitations"])
    assert "Astrobiology" in limits or "Quantum Origami" in limits

    # Education Pathways
    res_e = client.get(f'/api/education/pathways/{p_id}')
    assert res_e.status_code == 200
    e_data = res_e.get_json()
    assert e_data["success"] is True
    gaps = " ".join(e_data["information_gaps"])
    assert "Astrobiology" in gaps or "Quantum Origami" in gaps


def test_api_contract_consistency(client):
    """
    Test 5: Verify strict API contract compliance across all Member 2 endpoints:
    - Profile JSON contract
    - Career Guidance JSON contract
    - Education Pathways JSON contract
    """
    res_create = client.post('/api/profile', json={
        "full_name": "Contract Test",
        "email": "contract@example.com",
        "education_level": "Undergraduate",
        "qualification": "B.Sc Computer Science",
        "skills": ["Python", "SQL"],
        "interests": ["Data Science"]
    })
    p_id = res_create.get_json()["profile"]["id"]

    # Check Career Guidance Schema
    c_res = client.get(f'/api/career/guidance/{p_id}')
    c_json = c_res.get_json()
    assert "success" in c_json
    assert "profile_id" in c_json
    assert "student_name" in c_json
    assert "domains" in c_json
    assert "profile_summary" in c_json
    assert "careers" in c_json
    for c in c_json["careers"]:
        assert "id" in c
        assert "name" in c
        assert "domain" in c
        assert "alignment_level" in c
        assert "why_identified" in c
        assert "matched_skills" in c
        assert "recommended_skill_development" in c

    # Check Education Pathways Schema
    e_res = client.get(f'/api/education/pathways/{p_id}')
    e_json = e_res.get_json()
    assert "success" in e_json
    assert "profile_id" in e_json
    assert "student_name" in e_json
    assert "current_education" in e_json
    assert "pathways" in e_json
    assert "career_connections" in e_json
    for p in e_json["pathways"]:
        assert "id" in p
        assert "title" in p
        assert "current_education_level" in p
        assert "possible_next_step" in p
        assert "higher_study_options" in p
        assert "specialization_options" in p
        assert "why_identified" in p
        assert "career_connections" in p


def test_no_unsupported_precision_or_guarantees_anywhere(client):
    """
    Test 6: Verify strict adherence to informational neutrality:
    - No fake percentages (e.g. 94% match)
    - No guaranteed job / guaranteed admission language
    """
    res = client.post('/api/profile', json={
        "full_name": "Neutrality Student",
        "email": "neutrality@example.com",
        "education_level": "Diploma",
        "qualification": "Diploma in Mechanical Engineering",
        "skills": ["CAD"],
        "interests": ["Robotics"]
    })
    p_id = res.get_json()["profile"]["id"]

    # Check Career Guidance UI
    res_c = client.get(f'/career/guidance/{p_id}')
    content_c = res_c.data.decode('utf-8').lower()
    assert "% match" not in content_c
    assert "guaranteed admission" not in content_c
    assert "guaranteed job" not in content_c
    assert "perfect career" not in content_c

    # Check Education Pathways UI
    res_e = client.get(f'/education/pathways/{p_id}')
    content_e = res_e.data.decode('utf-8').lower()
    assert "% match" not in content_e
    assert "guaranteed admission" not in content_e
    assert "guaranteed job" not in content_e
    assert "guarantee of admission" not in content_e or "does not constitute a guarantee of admission" in content_e
