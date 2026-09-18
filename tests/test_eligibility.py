import pytest
from eligibility.services import EligibilityService


# =============================================================================
# Unit Tests for EligibilityService
# =============================================================================

def test_fully_eligible_student():
    """Scenario 1: Fully eligible student meeting all opportunity requirements."""
    student = {
        "education_level": "Bachelor's Degree",
        "degree": "Computer Science",
        "skills": ["Python", "Flask", "SQL", "Docker"],
        "age": 24,
        "experience": 2
    }
    opportunity = {
        "min_education": "Bachelor's",
        "required_degree": "Computer Science",
        "required_skills": ["Python", "SQL"],
        "min_age": 21,
        "max_age": 30,
        "min_experience": 1
    }

    result = EligibilityService.check_eligibility(student, opportunity)

    assert result["status"] == "ELIGIBLE"
    assert result["eligible"] is True
    assert len(result["satisfied_criteria"]) == 5
    assert len(result["missing_criteria"]) == 0
    assert len(result["unverified_criteria"]) == 0
    assert len(result["reasons"]) > 0


def test_clearly_ineligible_student():
    """Scenario 2: Clearly ineligible student failing education and experience."""
    student = {
        "education_level": "High School",
        "degree": "General Science",
        "skills": ["HTML", "CSS"],
        "age": 19,
        "experience": 0
    }
    opportunity = {
        "min_education": "Master's Degree",
        "required_degree": "Computer Science",
        "required_skills": ["Python", "Machine Learning"],
        "min_age": 22,
        "min_experience": 2
    }

    result = EligibilityService.check_eligibility(student, opportunity)

    assert result["status"] == "NOT_ELIGIBLE"
    assert result["eligible"] is False
    assert len(result["missing_criteria"]) >= 4
    # Check that reasons contain clear explanations
    reason_text = " ".join(result["reasons"])
    assert "Required education" in reason_text or "education" in reason_text.lower()
    assert "experience" in reason_text.lower()
    assert "skills" in reason_text.lower()


def test_missing_student_information_needs_verification():
    """Scenario 3: Requirements exist but student information is omitted or empty."""
    student = {}
    opportunity = {
        "min_education": "Bachelor's",
        "required_degree": "Engineering",
        "required_skills": ["Python", "FastAPI"],
        "max_age": 28,
        "min_experience": 2
    }

    result = EligibilityService.check_eligibility(student, opportunity)

    assert result["status"] == "NEEDS_VERIFICATION"
    assert result["eligible"] is None
    assert len(result["unverified_criteria"]) == 5
    assert len(result["missing_criteria"]) == 0
    assert len(result["satisfied_criteria"]) == 0


def test_missing_opportunity_requirements():
    """Scenario 4: Opportunity has no requirements specified (open eligibility)."""
    student = {
        "education_level": "High School",
        "skills": ["Communication"]
    }
    opportunity = {}

    result = EligibilityService.check_eligibility(student, opportunity)

    assert result["status"] == "ELIGIBLE"
    assert result["eligible"] is True
    assert len(result["satisfied_criteria"]) == 0
    assert len(result["missing_criteria"]) == 0
    assert len(result["unverified_criteria"]) == 0
    assert any("No specific eligibility criteria" in r for r in result["reasons"])


def test_skill_matching_exact_and_partial():
    """Scenario 5: Skill matching with partial fulfillment, missing skills, and empty skills."""
    # Subset satisfied, some missing
    student = {"skills": ["Python", "Django", "Git"]}
    opportunity = {"required_skills": ["Python", "Django", "Kubernetes", "AWS"]}

    result = EligibilityService.check_eligibility(student, opportunity)
    assert result["status"] == "NOT_ELIGIBLE"
    assert result["eligible"] is False
    assert len(result["missing_criteria"]) == 1
    missing_crit = result["missing_criteria"][0]
    assert "kubernetes" in missing_crit["missing_skills"]
    assert "aws" in missing_crit["missing_skills"]
    assert "python" in missing_crit["satisfied_skills"]
    assert "django" in missing_crit["satisfied_skills"]

    # Student skills string formatting
    student_str = {"skills": "python ,  flask ; postgresql"}
    opportunity_req = {"required_skills": ["PostgreSQL", "Python"]}
    result2 = EligibilityService.check_eligibility(student_str, opportunity_req)
    assert result2["status"] == "ELIGIBLE"
    assert result2["eligible"] is True


def test_case_insensitive_matching():
    """Scenario 6: Case-insensitivity across degrees, education level, and skills."""
    student = {
        "education_level": "bachelor of technology",
        "degree": "b.tech in computer science",
        "skills": ["PYTHON", "FLASK", "dOcKeR"],
        "age": "25",
        "experience": "3 YEARS"
    }
    opportunity = {
        "min_education": "Bachelor's",
        "required_degree": "Computer Science",
        "required_skills": ["python", "flask", "docker"],
        "min_age": 20,
        "max_age": 30,
        "min_experience": 2
    }

    result = EligibilityService.check_eligibility(student, opportunity)
    assert result["status"] == "ELIGIBLE"
    assert result["eligible"] is True
    assert len(result["missing_criteria"]) == 0


def test_multiple_failed_requirements():
    """Scenario 7: Multiple distinct criteria failing simultaneously."""
    student = {
        "education_level": "High School",
        "degree": "Arts",
        "skills": ["Photoshop"],
        "age": 35,
        "experience": 0.5
    }
    opportunity = {
        "min_education": "Bachelor's Degree",
        "required_degree": "Computer Science",
        "required_skills": ["Python", "SQL"],
        "max_age": 30,
        "min_experience": 3
    }

    result = EligibilityService.check_eligibility(student, opportunity)
    assert result["status"] == "NOT_ELIGIBLE"
    assert result["eligible"] is False
    # All 5 criteria should be in missing_criteria
    failed_names = [item["criterion"] for item in result["missing_criteria"]]
    assert "education_level" in failed_names
    assert "degree" in failed_names
    assert "skills" in failed_names
    assert "age" in failed_names
    assert "experience" in failed_names
    assert len(result["reasons"]) >= 5


def test_needs_verification_scenario():
    """Scenario 8: Some criteria satisfied, but missing fields trigger NEEDS_VERIFICATION."""
    student = {
        "education_level": "Bachelor of Technology",
        "degree": "Computer Science",
        # Missing skills, age, experience in student data
    }
    opportunity = {
        "min_education": "Bachelor's",
        "required_degree": "Computer Science",
        "required_skills": ["Python", "TensorFlow"],
        "min_experience": 1
    }

    result = EligibilityService.check_eligibility(student, opportunity)
    assert result["status"] == "NEEDS_VERIFICATION"
    assert result["eligible"] is None
    assert len(result["satisfied_criteria"]) == 2  # education & degree satisfied
    assert len(result["missing_criteria"]) == 0
    assert len(result["unverified_criteria"]) == 2  # skills & experience unverified


def test_education_hierarchy_progression():
    """Higher education tier satisfies lower education requirement."""
    # Master's satisfies Bachelor's requirement
    student_masters = {"education_level": "Master of Science in IT"}
    opp_bachelors = {"min_education": "Bachelor's Degree"}
    res = EligibilityService.check_eligibility(student_masters, opp_bachelors)
    assert res["status"] == "ELIGIBLE"
    assert res["eligible"] is True

    # PhD satisfies Master's requirement
    student_phd = {"education_level": "Ph.D. in Computer Engineering"}
    opp_masters = {"min_education": "Master's"}
    res_phd = EligibilityService.check_eligibility(student_phd, opp_masters)
    assert res_phd["status"] == "ELIGIBLE"
    assert res_phd["eligible"] is True

    # Diploma does NOT satisfy Bachelor's requirement
    student_diploma = {"education_level": "Diploma in Mechanical"}
    res_dip = EligibilityService.check_eligibility(student_diploma, opp_bachelors)
    assert res_dip["status"] == "NOT_ELIGIBLE"
    assert res_dip["eligible"] is False


def test_experience_parsing_variations():
    """Test experience number formats: integer, float, strings like '3+ years'."""
    opp = {"min_experience": 3}

    assert EligibilityService.check_eligibility({"experience": 3}, opp)["status"] == "ELIGIBLE"
    assert EligibilityService.check_eligibility({"experience": 4.5}, opp)["status"] == "ELIGIBLE"
    assert EligibilityService.check_eligibility({"experience": "3.5 years"}, opp)["status"] == "ELIGIBLE"
    assert EligibilityService.check_eligibility({"experience": "5+ yrs"}, opp)["status"] == "ELIGIBLE"
    assert EligibilityService.check_eligibility({"experience": "1 year"}, opp)["status"] == "NOT_ELIGIBLE"
    assert EligibilityService.check_eligibility({"experience": 2}, opp)["status"] == "NOT_ELIGIBLE"


def test_age_boundary_conditions():
    """Test min_age and max_age boundaries."""
    opp = {"min_age": 18, "max_age": 25}

    assert EligibilityService.check_eligibility({"age": 18}, opp)["status"] == "ELIGIBLE"
    assert EligibilityService.check_eligibility({"age": 25}, opp)["status"] == "ELIGIBLE"
    assert EligibilityService.check_eligibility({"age": 21}, opp)["status"] == "ELIGIBLE"
    assert EligibilityService.check_eligibility({"age": 17}, opp)["status"] == "NOT_ELIGIBLE"
    assert EligibilityService.check_eligibility({"age": 26}, opp)["status"] == "NOT_ELIGIBLE"


def test_age_limit_dict_and_score_evaluation():
    """Test opportunity with nested age_limit dict and score/gpa cutoffs."""
    opp = {
        "age_limit": {"min": 20, "max": 28},
        "min_score": 7.5
    }

    # Satisfied
    stu_ok = {"age": 22, "score": 8.0}
    res_ok = EligibilityService.check_eligibility(stu_ok, opp)
    assert res_ok["status"] == "ELIGIBLE"
    assert res_ok["eligible"] is True

    # Failed score
    stu_low_score = {"age": 22, "score": 6.8}
    res_low_score = EligibilityService.check_eligibility(stu_low_score, opp)
    assert res_low_score["status"] == "NOT_ELIGIBLE"
    assert res_low_score["eligible"] is False

    # Unverified score
    stu_no_score = {"age": 22}
    res_unverified = EligibilityService.check_eligibility(stu_no_score, opp)
    assert res_unverified["status"] == "NEEDS_VERIFICATION"
    assert res_unverified["eligible"] is None


def test_certifications_evaluation():
    """Test required certifications matching and verification."""
    opp = {"required_certifications": ["AWS Certified Solutions Architect", "CKA"]}

    # All certifications present
    stu_certified = {"certifications": ["AWS Certified Solutions Architect Associate", "CKA - Kubernetes"]}
    res_cert = EligibilityService.check_eligibility(stu_certified, opp)
    assert res_cert["status"] == "ELIGIBLE"
    assert res_cert["eligible"] is True

    # Missing one certification
    stu_missing_cert = {"certifications": ["AWS Certified Solutions Architect"]}
    res_miss = EligibilityService.check_eligibility(stu_missing_cert, opp)
    assert res_miss["status"] == "NOT_ELIGIBLE"
    assert res_miss["eligible"] is False

    # Missing certs field altogether
    stu_no_cert_field = {}
    res_unver = EligibilityService.check_eligibility(stu_no_cert_field, opp)
    assert res_unver["status"] == "NEEDS_VERIFICATION"
    assert res_unver["eligible"] is None


def test_nested_requirements_payload():
    """Test opportunity data passed with nested requirements object."""
    opp = {
        "id": 101,
        "title": "Software Engineer",
        "requirements": {
            "min_education": "Bachelor's",
            "skills": ["Python", "Flask"]
        }
    }
    stu = {
        "education_level": "B.Tech",
        "skills": ["python", "flask", "git"]
    }
    res = EligibilityService.check_eligibility(stu, opp)
    assert res["status"] == "ELIGIBLE"
    assert res["eligible"] is True


# =============================================================================
# Integration / API Route Tests
# =============================================================================

def test_api_eligibility_health(client):
    """Ensure health endpoint works and preserves existing contract."""
    response = client.get('/api/eligibility/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["module"] == "eligibility_checker"


def test_api_eligibility_check_success(client):
    """Test POST /api/eligibility/check endpoint with valid payload."""
    payload = {
        "student_profile": {
            "education_level": "Bachelor's",
            "degree": "Computer Science",
            "skills": ["Python", "Django"],
            "age": 23,
            "experience": 2
        },
        "opportunity": {
            "min_education": "Bachelor's",
            "required_skills": ["Python"],
            "max_age": 26
        }
    }

    response = client.post('/api/eligibility/check', json=payload)
    assert response.status_code == 200
    data = response.get_json()

    assert data["status"] == "ELIGIBLE"
    assert data["eligible"] is True
    assert "satisfied_criteria" in data
    assert "missing_criteria" in data
    assert "unverified_criteria" in data
    assert "reasons" in data


def test_api_eligibility_check_not_eligible(client):
    """Test POST /api/eligibility/check with ineligible student."""
    payload = {
        "student_profile": {
            "education_level": "High School",
            "skills": ["Basic HTML"]
        },
        "opportunity": {
            "min_education": "Bachelor's",
            "required_skills": ["Python", "Rust"]
        }
    }

    response = client.post('/api/eligibility/check', json=payload)
    assert response.status_code == 200
    data = response.get_json()

    assert data["status"] == "NOT_ELIGIBLE"
    assert data["eligible"] is False
    assert len(data["missing_criteria"]) >= 2


def test_api_eligibility_check_invalid_payload(client):
    """Test POST /api/eligibility/check with non-json or invalid data."""
    # Non-JSON content type and invalid body
    response = client.post(
        '/api/eligibility/check',
        data="not a json",
        content_type='text/plain'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_api_eligibility_demo_route(client):
    """Test GET /api/eligibility/demo returns 200 and loads demo template."""
    response = client.get('/api/eligibility/demo')
    assert response.status_code == 200
    assert b"Eligibility Verification Engine" in response.data
