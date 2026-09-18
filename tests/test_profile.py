import json
import pytest
from profile.models import StudentProfile
from profile.services import ProfileService

def test_create_profile_success(client):
    """Test successful creation of a student profile with full details."""
    payload = {
        "full_name": "Pushpa Eega",
        "email": "pushpa@example.com",
        "education_level": "Undergraduate",
        "qualification": "B.Tech Computer Science & Engineering",
        "degree_details": {
            "degree_name": "B.Tech",
            "major": "CSE - Artificial Intelligence",
            "institution": "JNTU Hyderabad",
            "gpa": "8.8"
        },
        "diploma_details": {
            "stream": "Computer Engineering",
            "institution": "Govt Polytechnic"
        },
        "pg_details": {
            "degree_name": "M.Tech",
            "specialization": "Data Science"
        },
        "skills": ["Python", "SQL", "Flask", "Machine Learning", "Docker"],
        "interests": ["Artificial Intelligence", "Cloud Computing", "Web Development"],
        "career_goals": "AI Engineer & Technical Architect",
        "location": "Hyderabad, Telangana",
        "preferred_locations": ["Hyderabad", "Bengaluru", "Remote"],
        "preferences": {
            "work_mode": "Hybrid"
        }
    }

    res = client.post('/api/profile', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["status"] == "success"
    assert "profile" in data
    profile = data["profile"]
    assert profile["full_name"] == "Pushpa Eega"
    assert profile["email"] == "pushpa@example.com"
    assert profile["education_level"] == "Undergraduate"
    assert profile["qualification"] == "B.Tech Computer Science & Engineering"
    assert "Python" in profile["skills"]
    assert "Artificial Intelligence" in profile["interests"]
    assert profile["degree_details"]["major"] == "CSE - Artificial Intelligence"
    assert profile["diploma_details"]["stream"] == "Computer Engineering"
    assert profile["pg_details"]["degree_name"] == "M.Tech"
    assert profile["location"] == "Hyderabad, Telangana"
    assert "Remote" in profile["preferred_locations"]
    assert profile["preferences"]["work_mode"] == "Hybrid"

def test_create_profile_missing_name(client):
    """Test profile creation fails when full_name is missing."""
    payload = {
        "email": "noname@example.com"
    }
    res = client.post('/api/profile', json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "error"
    assert "Full name is required" in data["message"]

def test_create_profile_missing_email(client):
    """Test profile creation fails when email is missing."""
    payload = {
        "full_name": "No Email Student"
    }
    res = client.post('/api/profile', json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "error"
    assert "valid email address is required" in data["message"]

def test_create_profile_invalid_email(client):
    """Test profile creation fails when email format is invalid."""
    payload = {
        "full_name": "Invalid Email",
        "email": "not-an-email"
    }
    res = client.post('/api/profile', json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "error"
    assert "valid email" in data["message"].lower()

def test_create_profile_duplicate_email(client):
    """Test profile creation fails when email already exists."""
    payload = {
        "full_name": "Student First",
        "email": "duplicate@example.com"
    }
    res1 = client.post('/api/profile', json=payload)
    assert res1.status_code == 201

    payload_dup = {
        "full_name": "Student Second",
        "email": "duplicate@example.com"
    }
    res2 = client.post('/api/profile', json=payload_dup)
    assert res2.status_code == 400
    data2 = res2.get_json()
    assert data2["status"] == "error"
    assert "already exists" in data2["message"]

def test_get_profile_by_id(client):
    """Test retrieving a profile by ID."""
    # Create profile
    payload = {
        "full_name": "Retrieval Test",
        "email": "retrieve@example.com",
        "skills": ["Flask", "Pytest"]
    }
    create_res = client.post('/api/profile', json=payload)
    p_id = create_res.get_json()["profile"]["id"]

    # Fetch by ID
    get_res = client.get(f'/api/profile/{p_id}')
    assert get_res.status_code == 200
    profile = get_res.get_json()["profile"]
    assert profile["id"] == p_id
    assert profile["full_name"] == "Retrieval Test"
    assert profile["skills"] == ["Flask", "Pytest"]

def test_get_profile_not_found(client):
    """Test retrieving non-existent profile returns 404."""
    res = client.get('/api/profile/99999')
    assert res.status_code == 404
    data = res.get_json()
    assert data["status"] == "error"
    assert "not found" in data["message"].lower()

def test_get_profile_by_email(client):
    """Test retrieving profile using email query parameter."""
    payload = {
        "full_name": "Email Query Student",
        "email": "query@example.com"
    }
    client.post('/api/profile', json=payload)

    # Query with email
    res = client.get('/api/profile/by-email?email=query@example.com')
    assert res.status_code == 200
    data = res.get_json()
    assert data["profile"]["full_name"] == "Email Query Student"

    # Missing email param
    res_bad = client.get('/api/profile/by-email')
    assert res_bad.status_code == 400

    # Nonexistent email
    res_none = client.get('/api/profile/by-email?email=notfound@example.com')
    assert res_none.status_code == 404

def test_update_profile_success(client):
    """Test updating existing profile fields."""
    payload = {
        "full_name": "Initial Name",
        "email": "update_me@example.com",
        "skills": ["Python"],
        "career_goals": "Junior Developer"
    }
    create_res = client.post('/api/profile', json=payload)
    p_id = create_res.get_json()["profile"]["id"]

    # Update
    update_payload = {
        "full_name": "Updated Name",
        "skills": ["Python", "TensorFlow", "FastAPI"],
        "career_goals": "Senior AI Architect",
        "location": "Bengaluru",
        "education_level": "Postgraduate"
    }
    update_res = client.put(f'/api/profile/{p_id}', json=update_payload)
    assert update_res.status_code == 200
    updated_data = update_res.get_json()["profile"]
    assert updated_data["full_name"] == "Updated Name"
    assert "TensorFlow" in updated_data["skills"]
    assert updated_data["career_goals"] == "Senior AI Architect"
    assert updated_data["location"] == "Bengaluru"
    assert updated_data["education_level"] == "Postgraduate"

def test_update_profile_duplicate_email_conflict(client):
    """Test update fails if attempting to change email to another existing user's email."""
    client.post('/api/profile', json={"full_name": "User One", "email": "user1@example.com"})
    res2 = client.post('/api/profile', json={"full_name": "User Two", "email": "user2@example.com"})
    user2_id = res2.get_json()["profile"]["id"]

    # Try updating User Two's email to User One's email
    conflict_res = client.put(f'/api/profile/{user2_id}', json={"email": "user1@example.com"})
    assert conflict_res.status_code == 400
    data = conflict_res.get_json()
    assert "already exists" in data["message"]

def test_update_profile_not_found(client):
    """Test update returns 404 when profile ID does not exist."""
    res = client.put('/api/profile/88888', json={"full_name": "Ghost"})
    assert res.status_code == 404

def test_list_profiles(client):
    """Test listing profiles."""
    client.post('/api/profile', json={"full_name": "Listing A", "email": "a@example.com"})
    client.post('/api/profile', json={"full_name": "Listing B", "email": "b@example.com"})

    res = client.get('/api/profile/all?limit=10')
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["count"] >= 2

def test_delete_profile(client):
    """Test deleting a student profile."""
    create_res = client.post('/api/profile', json={"full_name": "To Delete", "email": "delete@example.com"})
    p_id = create_res.get_json()["profile"]["id"]

    del_res = client.delete(f'/api/profile/{p_id}')
    assert del_res.status_code == 200

    # Verify deleted
    get_res = client.get(f'/api/profile/{p_id}')
    assert get_res.status_code == 404

def test_profile_ui_endpoints(client):
    """Test the UI template routes render with HTTP 200."""
    res1 = client.get('/api/profile/ui')
    assert res1.status_code == 200
    assert b"Student Profile &amp; Interest Intelligence" in res1.data or b"Student Profile & Interest Intelligence" in res1.data

    create_res = client.post('/api/profile', json={"full_name": "UI Student", "email": "ui@example.com"})
    p_id = create_res.get_json()["profile"]["id"]

    res2 = client.get(f'/api/profile/ui/{p_id}')
    assert res2.status_code == 200
    assert b"UI Student" in res2.data


def test_profile_academic_qualification_ui_and_removal_of_domain_and_interests(client):
    """
    Verify:
    1. In new profile mode (no qualification selected): all detail sections are hidden.
    2. In edit mode with Undergraduate profile: Undergraduate details visible, others hidden.
    3. In edit mode with Diploma profile: Diploma details visible, others hidden.
    4. In edit mode with Postgraduate profile: Postgraduate details visible, others hidden.
    5. Domain input/card/box is completely removed from profile UI.
    6. Academic Interests input/card/box is completely removed from profile UI.
    """
    # 1. New profile mode
    new_res = client.get('/api/profile/ui')
    assert new_res.status_code == 200
    new_html = new_res.data.decode('utf-8')
    assert 'id="section-undergraduate" style="display: none;"' in new_html
    assert 'id="section-diploma" style="display: none;"' in new_html
    assert 'id="section-postgraduate" style="display: none;"' in new_html
    assert 'updateQualificationSections()' in new_html
    assert "Academic Interests" not in new_html
    assert "Domain Interests:" not in new_html

    # 2. Undergraduate profile
    ug_create = client.post('/api/profile', json={
        "full_name": "UG Test Student",
        "email": "ug.test@example.com",
        "education_level": "Undergraduate"
    })
    ug_id = ug_create.get_json()["profile"]["id"]
    ug_res = client.get(f'/api/profile/ui/{ug_id}')
    ug_html = ug_res.data.decode('utf-8')
    assert 'id="section-undergraduate" style="display: block;"' in ug_html
    assert 'id="section-diploma" style="display: none;"' in ug_html
    assert 'id="section-postgraduate" style="display: none;"' in ug_html

    # 3. Diploma profile
    dip_create = client.post('/api/profile', json={
        "full_name": "Dip Test Student",
        "email": "dip.test@example.com",
        "education_level": "Diploma"
    })
    dip_id = dip_create.get_json()["profile"]["id"]
    dip_res = client.get(f'/api/profile/ui/{dip_id}')
    dip_html = dip_res.data.decode('utf-8')
    assert 'id="section-undergraduate" style="display: none;"' in dip_html
    assert 'id="section-diploma" style="display: block;"' in dip_html
    assert 'id="section-postgraduate" style="display: none;"' in dip_html

    # 4. Postgraduate profile
    pg_create = client.post('/api/profile', json={
        "full_name": "PG Test Student",
        "email": "pg.test@example.com",
        "education_level": "Postgraduate"
    })
    pg_id = pg_create.get_json()["profile"]["id"]
    pg_res = client.get(f'/api/profile/ui/{pg_id}')
    pg_html = pg_res.data.decode('utf-8')
    assert 'id="section-undergraduate" style="display: none;"' in pg_html
    assert 'id="section-diploma" style="display: none;"' in pg_html
    assert 'id="section-postgraduate" style="display: block;"' in pg_html
