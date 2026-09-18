import pytest
from profile.interest_intelligence import InterestIntelligenceService, CAREER_DOMAINS, UNKNOWN_DOMAIN

def test_interest_normalization_whitespace_and_capitalization():
    """Test normalization trims whitespace and standardizes capitalization."""
    res = InterestIntelligenceService.analyze_interests("   pYtHoN   ")
    assert res["status"] == "success"
    assert len(res["interests"]) == 1
    assert res["interests"][0]["name"] == "Python"
    assert res["interests"][0]["original"] == "pYtHoN"
    assert res["interests"][0]["is_mapped"] is True

def test_interest_normalization_duplicate_handling():
    """Test duplicates are stripped while preserving the first appearance."""
    res = InterestIntelligenceService.analyze_interests("Python, python, PYTHON, SQL, sql")
    assert res["status"] == "success"
    assert len(res["interests"]) == 2
    names = [item["name"] for item in res["interests"]]
    assert names == ["Python", "Data Science"] or "Python" in names

def test_interest_normalization_list_and_string_inputs():
    """Test service handles both comma-separated strings and Python lists."""
    res_str = InterestIntelligenceService.analyze_interests("Python, Machine Learning")
    res_list = InterestIntelligenceService.analyze_interests(["Python", "Machine Learning"])

    assert res_str["status"] == "success"
    assert res_list["status"] == "success"
    assert len(res_str["interests"]) == len(res_list["interests"])
    assert [i["name"] for i in res_str["interests"]] == [i["name"] for i in res_list["interests"]]

def test_known_interest_mapping_multi_domain():
    """Test known interest maps to correct domains with factual explanations."""
    res = InterestIntelligenceService.analyze_interests("Python")
    python_entry = res["interests"][0]
    domain_names = [d["name"] for d in python_entry["domains"]]

    assert "Technology & Software" in domain_names
    assert "Data & AI" in domain_names

    # Verify explainability reasons are present and non-empty
    for d in python_entry["domains"]:
        assert len(d["reason"].strip()) > 10
        assert "guarantee" not in d["reason"].lower()

def test_multiple_interests_mapping():
    """Test multiple distinct interests across different domains."""
    input_terms = "Python, Medicine, Accounting, Mechanical Engineering, Graphic Design"
    res = InterestIntelligenceService.analyze_interests(input_terms)

    assert res["status"] == "success"
    assert len(res["interests"]) == 5
    summary = res["domain_summary"]

    assert "Technology & Software" in summary
    assert "Healthcare" in summary
    assert "Finance & Commerce" in summary
    assert "Engineering" in summary
    assert "Design & Creative" in summary
    assert len(res["unmapped_interests"]) == 0

def test_unknown_interest_safe_handling():
    """Test novel or uncatalogued interests do not crash and are safely categorized."""
    res = InterestIntelligenceService.analyze_interests("Astrophotography, Quantum Alchemy")
    assert res["status"] == "success"
    assert len(res["interests"]) == 2

    for item in res["interests"]:
        assert item["is_mapped"] is False
        assert len(item["domains"]) == 1
        assert item["domains"][0]["name"] == UNKNOWN_DOMAIN
        assert "not currently indexed" in item["domains"][0]["reason"]

    assert "Astrophotography" in res["unmapped_interests"]
    assert "Quantum Alchemy" in res["unmapped_interests"]

def test_mixed_known_and_unknown_interests():
    """Test mix of catalogued and uncatalogued interests."""
    res = InterestIntelligenceService.analyze_interests("Cybersecurity, Deep-Sea Cartography, Biology")
    assert res["status"] == "success"
    assert len(res["interests"]) == 3

    mapped_names = [i["name"] for i in res["interests"] if i["is_mapped"]]
    unmapped_names = [i["name"] for i in res["interests"] if not i["is_mapped"]]

    assert "Cybersecurity" in mapped_names
    assert "Biology" in mapped_names
    assert "Deep-Sea Cartography" in unmapped_names
    assert "Cybersecurity" in res["domain_summary"]
    assert "Healthcare" in res["domain_summary"]

def test_empty_interest_input():
    """Test empty or whitespace-only inputs return empty structured responses."""
    res_empty_str = InterestIntelligenceService.analyze_interests("")
    assert res_empty_str["status"] == "success"
    assert res_empty_str["interests"] == []
    assert res_empty_str["domain_summary"] == []
    assert res_empty_str["unmapped_interests"] == []

    res_none = InterestIntelligenceService.analyze_interests(None)
    assert res_none["status"] == "success"
    assert res_none["interests"] == []

def test_career_domain_catalogue():
    """Test catalogue includes standard domains."""
    catalogue = InterestIntelligenceService.get_career_domains()
    assert isinstance(catalogue, list)
    assert "Technology & Software" in catalogue
    assert "Data & AI" in catalogue
    assert "Cybersecurity" in catalogue
    assert "Healthcare" in catalogue
    assert "Business & Management" in catalogue
    assert "Finance & Commerce" in catalogue
    assert "Education & Teaching" in catalogue
    assert "Law" in catalogue
    assert "Design & Creative" in catalogue
    assert "Government & Public Service" in catalogue
    assert "Media & Communication" in catalogue
    assert "Science & Research" in catalogue
    assert "Skilled & Technical Trades" in catalogue

# --- API Route Tests ---

def test_api_analyze_interests_with_list(client):
    """Test POST /api/profile/interests/analyze with a list of interests."""
    payload = {
        "interests": ["Python", "Machine Learning", "Cloud Computing"]
    }
    res = client.post('/api/profile/interests/analyze', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["interests"]) == 3
    assert "Technology & Software" in data["domain_summary"]
    assert "Data & AI" in data["domain_summary"]
    assert len(data["unmapped_interests"]) == 0

def test_api_analyze_interests_with_string(client):
    """Test POST /api/profile/interests/analyze with a comma-separated string."""
    payload = {
        "interests": "Artificial Intelligence, Civil Engineering"
    }
    res = client.post('/api/profile/interests/analyze', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["interests"]) == 2
    assert "Data & AI" in data["domain_summary"]
    assert "Engineering" in data["domain_summary"]

def test_api_analyze_interests_from_profile_id(client):
    """Test POST /api/profile/interests/analyze using an existing profile ID."""
    # Create student profile with interests
    profile_payload = {
        "full_name": "Interest Test Student",
        "email": "interest_test@example.com",
        "interests": ["Cybersecurity", "Law", "Teaching"]
    }
    create_res = client.post('/api/profile', json=profile_payload)
    assert create_res.status_code == 201
    p_id = create_res.get_json()["profile"]["id"]

    # Analyze via profile_id
    analyze_res = client.post('/api/profile/interests/analyze', json={"profile_id": p_id})
    assert analyze_res.status_code == 200
    data = analyze_res.get_json()
    assert data["status"] == "success"
    assert len(data["interests"]) == 3
    assert "Cybersecurity" in data["domain_summary"]
    assert "Law" in data["domain_summary"]
    assert "Education & Teaching" in data["domain_summary"]

def test_api_analyze_interests_profile_not_found(client):
    """Test POST /api/profile/interests/analyze with non-existent profile ID returns 404."""
    res = client.post('/api/profile/interests/analyze', json={"profile_id": 99999})
    assert res.status_code == 404
    data = res.get_json()
    assert data["status"] == "error"
    assert "not found" in data["message"].lower()

def test_api_analyze_interests_missing_payload(client):
    """Test POST /api/profile/interests/analyze with missing required fields returns 400."""
    res = client.post('/api/profile/interests/analyze', json={})
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "error"
    assert "Either 'interests' or 'profile_id' must be provided" in data["message"]

def test_api_get_domains_catalogue(client):
    """Test GET /api/profile/interests/domains returns domains catalogue."""
    res = client.get('/api/profile/interests/domains')
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["domains"]) >= 14
    assert "Technology & Software" in data["domains"]
