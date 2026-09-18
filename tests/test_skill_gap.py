import pytest
from skill_gap.services import SkillGapService


# =============================================================================
# Unit Tests for SkillGapService
# =============================================================================

def test_all_skills_matching():
    """Scenario 1: 100% of target skills are satisfied by current student skills."""
    current_skills = ["Python", "Flask", "SQL", "Git", "Docker"]
    target_skills = ["python", "flask", "sql", "git", "docker"]

    result = SkillGapService.analyze_gap(current_skills, target_skills)

    assert result["match_rate"] == 100.0
    assert result["gap_percentage"] == 0.0
    assert len(result["matching_skills"]) == 5
    assert len(result["missing_skills"]) == 0
    assert result["total_required"] == 5
    assert result["total_matched"] == 5
    assert result["total_missing"] == 0
    assert len(result["learning_areas"]) == 0


def test_no_skills_matching():
    """Scenario 2: Student has skills but none match the target career requirements."""
    current_skills = ["Graphic Design", "Photoshop", "Illustrator"]
    target_skills = ["Python", "PostgreSQL", "Docker", "Kubernetes"]

    result = SkillGapService.analyze_gap(current_skills, target_skills)

    assert result["match_rate"] == 0.0
    assert result["gap_percentage"] == 100.0
    assert len(result["matching_skills"]) == 0
    assert len(result["missing_skills"]) == 4
    assert result["total_required"] == 4
    assert result["total_matched"] == 0
    assert result["total_missing"] == 4


def test_partial_matching_and_percentages():
    """Scenario 3: Exactly 7 out of 10 skills matching (70% match rate, 30% gap)."""
    current_skills = [
        "Python", "SQL", "Git", "Linux", "Docker", "REST API", "HTML"
    ]
    target_skills = [
        "Python", "SQL", "Git", "Linux", "Docker", "REST API", "HTML",
        "Kubernetes", "AWS", "Terraform"
    ]

    result = SkillGapService.analyze_gap(current_skills, target_skills)

    assert result["match_rate"] == 70.0
    assert result["gap_percentage"] == 30.0
    assert result["total_required"] == 10
    assert result["total_matched"] == 7
    assert result["total_missing"] == 3
    assert len(result["matching_skills"]) == 7
    assert len(result["missing_skills"]) == 3


def test_case_insensitive_and_whitespace_normalization():
    """Scenario 4: Differences in case, whitespace, and basic punctuation."""
    current_skills = "  pYtHoN  ,   FLASK ;  PoStGrEsQl \n  dOcKeR "
    target_skills = ["Python", "Flask", "PostgreSQL", "Docker"]

    result = SkillGapService.analyze_gap(current_skills, target_skills)

    assert result["match_rate"] == 100.0
    assert result["gap_percentage"] == 0.0
    assert len(result["matching_skills"]) == 4
    assert len(result["missing_skills"]) == 0


def test_duplicate_skills_handling():
    """Scenario 5: Redundant duplicates in student and target skills are deduplicated."""
    current_skills = ["Python", "python", "PYTHON", "  python  ", "SQL", "sql"]
    target_skills = ["Python", "python", "SQL", "sql", "Docker", "docker"]

    result = SkillGapService.analyze_gap(current_skills, target_skills)

    # Unique target skills: Python, SQL, Docker (3 skills)
    assert result["total_required"] == 3
    assert result["total_matched"] == 2
    assert result["total_missing"] == 1
    assert result["match_rate"] == 66.67
    assert result["gap_percentage"] == 33.33
    assert len(result["matching_skills"]) == 2
    assert len(result["missing_skills"]) == 1


def test_empty_current_skills():
    """Scenario 6: Student has no current skills (empty list / None / empty string)."""
    target_skills = ["Python", "Django", "PostgreSQL"]

    result_none = SkillGapService.analyze_gap(None, target_skills)
    assert result_none["match_rate"] == 0.0
    assert result_none["gap_percentage"] == 100.0
    assert result_none["total_matched"] == 0
    assert result_none["total_missing"] == 3

    result_empty_str = SkillGapService.analyze_gap("", target_skills)
    assert result_empty_str["match_rate"] == 0.0
    assert result_empty_str["gap_percentage"] == 100.0


def test_empty_target_skills():
    """Scenario 7: Target career requires 0 specific skills."""
    current_skills = ["Python", "JavaScript"]

    result = SkillGapService.analyze_gap(current_skills, [])

    assert result["match_rate"] == 100.0
    assert result["gap_percentage"] == 0.0
    assert result["total_required"] == 0
    assert result["total_matched"] == 0
    assert result["total_missing"] == 0
    assert result["matching_skills"] == []
    assert result["missing_skills"] == []


def test_priority_explicit_and_fallback():
    """Scenario 8: Priority categorization with explicit buckets and deterministic fallback."""
    # Explicit priorities via dictionary buckets
    target_dict = {
        "critical": ["Python", "SQL"],
        "recommended": ["Docker"],
        "optional": ["Figma"]
    }
    current_skills = ["SQL"]

    result_exp = SkillGapService.analyze_gap(current_skills, target_dict)
    assert result_exp["total_required"] == 4
    assert result_exp["total_matched"] == 1
    assert result_exp["total_missing"] == 3
    assert "Python" in result_exp["priority_breakdown"]["critical"]
    assert "Docker" in result_exp["priority_breakdown"]["recommended"]
    assert "Figma" in result_exp["priority_breakdown"]["optional"]

    # Deterministic fallback when priorities omitted
    target_plain = ["Python", "PostgreSQL", "Docker", "Jest"]
    result_fallback = SkillGapService.analyze_gap([], target_plain)
    # Python (Programming) and PostgreSQL (Databases) -> Critical
    # Docker (Cloud/DevOps) and Jest (Testing) -> Recommended
    assert "Python" in result_fallback["priority_breakdown"]["critical"]
    assert "PostgreSQL" in result_fallback["priority_breakdown"]["critical"]
    assert "Docker" in result_fallback["priority_breakdown"]["recommended"]
    assert "Jest" in result_fallback["priority_breakdown"]["recommended"]


def test_learning_areas_mapping():
    """Scenario 9: Missing skills are mapped to structured broad learning areas."""
    current_skills = ["HTML", "CSS"]
    target_skills = [
        "HTML", "CSS", "Python", "Rust", "PostgreSQL", "Redis",
        "Docker", "Kubernetes", "Pytest", "Git"
    ]

    result = SkillGapService.analyze_gap(current_skills, target_skills)

    areas = {item["area"]: item["skills"] for item in result["learning_areas"]}

    assert "Programming Languages" in areas
    assert "Python" in areas["Programming Languages"]
    assert "Rust" in areas["Programming Languages"]

    assert "Databases & Storage" in areas
    assert "PostgreSQL" in areas["Databases & Storage"]
    assert "Redis" in areas["Databases & Storage"]

    assert "Cloud & DevOps" in areas
    assert "Docker" in areas["Cloud & DevOps"]
    assert "Kubernetes" in areas["Cloud & DevOps"]

    assert "Testing & Quality Assurance" in areas
    assert "Pytest" in areas["Testing & Quality Assurance"]

    assert "Version Control & Collaboration" in areas
    assert "Git" in areas["Version Control & Collaboration"]


# =============================================================================
# API Route Integration Tests
# =============================================================================

def test_api_skill_gap_health(client):
    """Verify GET /api/skill-gap/health endpoint contract."""
    response = client.get('/api/skill-gap/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["module"] == "skill_gap_analyzer"


def test_api_skill_gap_analyze_success(client):
    """Verify POST /api/skill-gap/analyze endpoint with valid payload."""
    payload = {
        "current_skills": ["Python", "Flask"],
        "target_skills": ["Python", "Flask", "SQL", "Docker"]
    }

    response = client.post('/api/skill-gap/analyze', json=payload)
    assert response.status_code == 200
    data = response.get_json()

    assert data["match_rate"] == 50.0
    assert data["gap_percentage"] == 50.0
    assert "matching_skills" in data
    assert "missing_skills" in data
    assert "priority_breakdown" in data
    assert "learning_areas" in data


def test_api_skill_gap_analyze_invalid_payload(client):
    """Verify POST /api/skill-gap/analyze with invalid payload returns 400."""
    response = client.post(
        '/api/skill-gap/analyze',
        data="invalid plain text",
        content_type="text/plain"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_api_skill_gap_demo_route(client):
    """Verify GET /api/skill-gap/demo returns 200 and loads dashboard template."""
    response = client.get('/api/skill-gap/demo')
    assert response.status_code == 200
    assert b"Skill Gap Analysis Engine" in response.data
