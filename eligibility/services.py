import re
from typing import Any, Dict, List, Optional, Tuple, Union


class EligibilityService:
    """
    Deterministic and explainable Eligibility Verification Engine.
    Evaluates student profile data against opportunity/pathway requirements.
    """

    # Education hierarchy mapping: lower integer = lower level of study
    EDUCATION_HIERARCHY = {
        "none": 0,
        "primary": 1,
        "middle school": 1,
        "high school": 1,
        "secondary": 1,
        "10th": 1,
        "12th": 1,
        "10+2": 1,
        "intermediate": 1,
        "matriculation": 1,
        "ged": 1,
        "diploma": 2,
        "polytechnic": 2,
        "associate": 2,
        "vocational": 2,
        "certificate": 2,
        "bachelor": 3,
        "bachelors": 3,
        "bachelor's": 3,
        "undergraduate": 3,
        "ug": 3,
        "graduate": 3,
        "graduation": 3,
        "b.tech": 3,
        "btech": 3,
        "b.e.": 3,
        "be": 3,
        "b.sc": 3,
        "bsc": 3,
        "b.com": 3,
        "bcom": 3,
        "b.a": 3,
        "ba": 3,
        "b.c.a": 3,
        "bca": 3,
        "bba": 3,
        "bs": 3,
        "b.s": 3,
        "master": 4,
        "masters": 4,
        "master's": 4,
        "postgraduate": 4,
        "post-graduate": 4,
        "pg": 4,
        "m.tech": 4,
        "mtech": 4,
        "m.e.": 4,
        "me": 4,
        "m.sc": 4,
        "msc": 4,
        "m.com": 4,
        "mcom": 4,
        "m.a": 4,
        "ma": 4,
        "m.c.a": 4,
        "mca": 4,
        "mba": 4,
        "ms": 4,
        "m.s": 4,
        "doctorate": 5,
        "doctoral": 5,
        "phd": 5,
        "ph.d": 5,
        "ph.d.": 5,
        "post-doc": 5,
        "post-doctoral": 5,
    }

    @staticmethod
    def _normalize_string(val: Any) -> Optional[str]:
        """Normalize a string: strip, lowercase, collapse whitespaces."""
        if val is None:
            return None
        s = str(val).strip().lower()
        s = re.sub(r"\s+", " ", s)
        return s if s else None

    @classmethod
    def _normalize_string_list(cls, val: Any) -> List[str]:
        """Convert a list or comma-separated/newline string to a normalized list of unique strings."""
        if val is None:
            return []
        if isinstance(val, (list, tuple, set)):
            raw_items = [str(x) for x in val if x is not None]
        elif isinstance(val, str):
            raw_items = re.split(r"[,;\n\r]+", val)
        else:
            raw_items = [str(val)]

        normalized = []
        seen = set()
        for item in raw_items:
            norm = cls._normalize_string(item)
            if norm and norm not in seen:
                seen.add(norm)
                normalized.append(norm)
        return normalized

    @staticmethod
    def _parse_number(val: Any) -> Optional[float]:
        """Extract a numeric value (int or float) from strings or numbers."""
        if val is None:
            return None
        if isinstance(val, (int, float)):
            return float(val)
        s = str(val).strip()
        match = re.search(r"[-+]?\d*\.?\d+", s)
        if match:
            try:
                return float(match.group(0))
            except ValueError:
                return None
        return None

    @classmethod
    def _get_education_rank(cls, edu_str: Optional[str]) -> Optional[int]:
        """Get the integer hierarchy rank for an education string."""
        norm = cls._normalize_string(edu_str)
        if not norm:
            return None

        # Exact match in dictionary
        if norm in cls.EDUCATION_HIERARCHY:
            return cls.EDUCATION_HIERARCHY[norm]

        # Check tokens and substrings (prefer highest matching level)
        highest_rank = None
        for key, rank in cls.EDUCATION_HIERARCHY.items():
            pattern = r"\b" + re.escape(key) + r"\b"
            if re.search(pattern, norm):
                if highest_rank is None or rank > highest_rank:
                    highest_rank = rank

        return highest_rank

    @classmethod
    def _extract_data(cls, raw_data: Any) -> Dict[str, Any]:
        """Flatten or extract dictionary from various input formats."""
        if raw_data is None:
            return {}
        if hasattr(raw_data, "to_dict") and callable(raw_data.to_dict):
            return raw_data.to_dict()
        if isinstance(raw_data, dict):
            # Unwrap common root wrappers if present
            for wrap_key in ("student", "student_profile", "opportunity", "requirements", "data", "profile"):
                if wrap_key in raw_data and isinstance(raw_data[wrap_key], dict) and len(raw_data) == 1:
                    return raw_data[wrap_key]
            return raw_data
        return {}

    @classmethod
    def check_eligibility(
        cls,
        student_profile_data: Any,
        target_opportunity_data: Any,
    ) -> Dict[str, Any]:
        """
        Evaluate eligibility of student profile data against target opportunity requirements.

        Returns structured dictionary:
        {
            "status": "ELIGIBLE" | "NOT_ELIGIBLE" | "NEEDS_VERIFICATION",
            "eligible": True | False | None,
            "satisfied_criteria": [...],
            "missing_criteria": [...],
            "unverified_criteria": [...],
            "reasons": [...]
        }
        """
        student = cls._extract_data(student_profile_data)
        opportunity = cls._extract_data(target_opportunity_data)

        # Merge nested requirements if present in opportunity
        opp_reqs = {}
        if "requirements" in opportunity and isinstance(opportunity["requirements"], dict):
            opp_reqs.update(opportunity["requirements"])
        for k, v in opportunity.items():
            if k != "requirements":
                opp_reqs[k] = v

        satisfied_criteria: List[Dict[str, Any]] = []
        missing_criteria: List[Dict[str, Any]] = []
        unverified_criteria: List[Dict[str, Any]] = []
        reasons: List[str] = []

        # 1. Evaluate Education Level / Minimum Qualification
        cls._evaluate_education_level(student, opp_reqs, satisfied_criteria, missing_criteria, unverified_criteria, reasons)

        # 2. Evaluate Degree / Field of Study
        cls._evaluate_degree(student, opp_reqs, satisfied_criteria, missing_criteria, unverified_criteria, reasons)

        # 3. Evaluate Skills
        cls._evaluate_skills(student, opp_reqs, satisfied_criteria, missing_criteria, unverified_criteria, reasons)

        # 4. Evaluate Age
        cls._evaluate_age(student, opp_reqs, satisfied_criteria, missing_criteria, unverified_criteria, reasons)

        # 5. Evaluate Experience
        cls._evaluate_experience(student, opp_reqs, satisfied_criteria, missing_criteria, unverified_criteria, reasons)

        # 6. Evaluate GPA / Percentage / Score (if specified)
        cls._evaluate_score(student, opp_reqs, satisfied_criteria, missing_criteria, unverified_criteria, reasons)

        # 7. Evaluate Certifications (if specified)
        cls._evaluate_certifications(student, opp_reqs, satisfied_criteria, missing_criteria, unverified_criteria, reasons)

        # Handle empty requirements case
        total_evals = len(satisfied_criteria) + len(missing_criteria) + len(unverified_criteria)
        if total_evals == 0:
            status = "ELIGIBLE"
            eligible = True
            reasons.append("No specific eligibility criteria required for this opportunity.")
        elif len(missing_criteria) > 0:
            status = "NOT_ELIGIBLE"
            eligible = False
        elif len(unverified_criteria) > 0:
            status = "NEEDS_VERIFICATION"
            eligible = None
        else:
            status = "ELIGIBLE"
            eligible = True

        return {
            "status": status,
            "eligible": eligible,
            "satisfied_criteria": satisfied_criteria,
            "missing_criteria": missing_criteria,
            "unverified_criteria": unverified_criteria,
            "reasons": reasons,
        }

    # =========================================================================
    # Individual Criteria Evaluators
    # =========================================================================

    @classmethod
    def _evaluate_education_level(
        cls,
        student: Dict[str, Any],
        opp: Dict[str, Any],
        satisfied: List[Dict[str, Any]],
        missing: List[Dict[str, Any]],
        unverified: List[Dict[str, Any]],
        reasons: List[str],
    ) -> None:
        # Check requirement keys
        req_edu = (
            opp.get("min_education")
            or opp.get("required_education")
            or opp.get("education_level")
            or opp.get("min_qualification")
            or opp.get("qualification")
        )
        if req_edu is None or str(req_edu).strip() == "":
            return

        req_edu_str = str(req_edu).strip()
        req_rank = cls._get_education_rank(req_edu_str)

        # Check student keys
        stu_edu = (
            student.get("education_level")
            or student.get("qualification")
            or student.get("education")
            or student.get("highest_qualification")
            or student.get("education_qualification")
        )

        if stu_edu is None or str(stu_edu).strip() == "":
            criterion_data = {
                "criterion": "education_level",
                "requirement": req_edu_str,
                "student_value": None,
                "message": f"Education qualification '{req_edu_str}' is required, but student profile does not provide education details.",
            }
            unverified.append(criterion_data)
            reasons.append(criterion_data["message"])
            return

        stu_edu_str = str(stu_edu).strip()
        stu_rank = cls._get_education_rank(stu_edu_str)

        if req_rank is not None and stu_rank is not None:
            if stu_rank >= req_rank:
                criterion_data = {
                    "criterion": "education_level",
                    "requirement": req_edu_str,
                    "student_value": stu_edu_str,
                    "message": f"Education level '{stu_edu_str}' meets or exceeds required '{req_edu_str}'.",
                }
                satisfied.append(criterion_data)
                reasons.append(criterion_data["message"])
            else:
                criterion_data = {
                    "criterion": "education_level",
                    "requirement": req_edu_str,
                    "student_value": stu_edu_str,
                    "message": f"Required education level is '{req_edu_str}', but student has '{stu_edu_str}'.",
                }
                missing.append(criterion_data)
                reasons.append(criterion_data["message"])
        else:
            # Fallback string containment / comparison
            norm_stu = cls._normalize_string(stu_edu_str) or ""
            norm_req = cls._normalize_string(req_edu_str) or ""
            if norm_req in norm_stu or norm_stu in norm_req:
                criterion_data = {
                    "criterion": "education_level",
                    "requirement": req_edu_str,
                    "student_value": stu_edu_str,
                    "message": f"Education qualification '{stu_edu_str}' matches required '{req_edu_str}'.",
                }
                satisfied.append(criterion_data)
                reasons.append(criterion_data["message"])
            else:
                criterion_data = {
                    "criterion": "education_level",
                    "requirement": req_edu_str,
                    "student_value": stu_edu_str,
                    "message": f"Required education qualification '{req_edu_str}' does not match student qualification '{stu_edu_str}'.",
                }
                missing.append(criterion_data)
                reasons.append(criterion_data["message"])

    @classmethod
    def _evaluate_degree(
        cls,
        student: Dict[str, Any],
        opp: Dict[str, Any],
        satisfied: List[Dict[str, Any]],
        missing: List[Dict[str, Any]],
        unverified: List[Dict[str, Any]],
        reasons: List[str],
    ) -> None:
        req_degrees = (
            opp.get("required_degree")
            or opp.get("required_degrees")
            or opp.get("degree")
            or opp.get("degrees")
            or opp.get("allowed_degrees")
            or opp.get("field_of_study")
        )
        if req_degrees is None or (isinstance(req_degrees, str) and not req_degrees.strip()):
            return

        req_degree_list = cls._normalize_string_list(req_degrees)
        if not req_degree_list:
            return

        stu_degree = (
            student.get("degree")
            or student.get("field_of_study")
            or student.get("major")
            or student.get("stream")
            or student.get("branch")
        )

        if stu_degree is None or (isinstance(stu_degree, str) and not stu_degree.strip()):
            criterion_data = {
                "criterion": "degree",
                "requirement": req_degrees,
                "student_value": None,
                "message": f"Degree/field of study in {req_degree_list} is required, but student profile does not provide degree information.",
            }
            unverified.append(criterion_data)
            reasons.append(criterion_data["message"])
            return

        stu_degree_norm = cls._normalize_string(stu_degree) or ""
        stu_degree_list = cls._normalize_string_list(stu_degree)

        # Check if student's degree matches any required degree pattern
        matched = False
        matched_req = ""
        for req in req_degree_list:
            # Check exact substring containment or token match
            if req in stu_degree_norm or any(req == s or req in s or s in req for s in stu_degree_list):
                matched = True
                matched_req = req
                break

        if matched:
            criterion_data = {
                "criterion": "degree",
                "requirement": req_degrees,
                "student_value": stu_degree,
                "message": f"Degree '{stu_degree}' satisfies required degree/field '{matched_req}'.",
            }
            satisfied.append(criterion_data)
            reasons.append(criterion_data["message"])
        else:
            criterion_data = {
                "criterion": "degree",
                "requirement": req_degrees,
                "student_value": stu_degree,
                "message": f"Student degree '{stu_degree}' does not match required degree/field {req_degree_list}.",
            }
            missing.append(criterion_data)
            reasons.append(criterion_data["message"])

    @classmethod
    def _evaluate_skills(
        cls,
        student: Dict[str, Any],
        opp: Dict[str, Any],
        satisfied: List[Dict[str, Any]],
        missing: List[Dict[str, Any]],
        unverified: List[Dict[str, Any]],
        reasons: List[str],
    ) -> None:
        req_skills_raw = (
            opp.get("required_skills")
            or opp.get("skills")
            or opp.get("mandatory_skills")
        )
        if req_skills_raw is None:
            return

        req_skills = cls._normalize_string_list(req_skills_raw)
        if not req_skills:
            return

        # Check if student profile provided a skills field
        stu_has_skill_field = False
        stu_skills_raw = None
        for k in ("skills", "technical_skills", "known_skills"):
            if k in student:
                stu_has_skill_field = True
                stu_skills_raw = student[k]
                break

        if not stu_has_skill_field or stu_skills_raw is None:
            criterion_data = {
                "criterion": "skills",
                "requirement": req_skills,
                "student_value": None,
                "message": f"Required skills {req_skills} cannot be verified because student profile does not provide skills.",
            }
            unverified.append(criterion_data)
            reasons.append(criterion_data["message"])
            return

        stu_skills = set(cls._normalize_string_list(stu_skills_raw))
        satisfied_skills = [s for s in req_skills if s in stu_skills]
        missing_skills = [s for s in req_skills if s not in stu_skills]

        if not missing_skills:
            criterion_data = {
                "criterion": "skills",
                "requirement": req_skills,
                "student_value": list(stu_skills),
                "message": f"All required skills are satisfied: {satisfied_skills}.",
            }
            satisfied.append(criterion_data)
            reasons.append(criterion_data["message"])
        else:
            criterion_data = {
                "criterion": "skills",
                "requirement": req_skills,
                "student_value": list(stu_skills),
                "satisfied_skills": satisfied_skills,
                "missing_skills": missing_skills,
                "message": f"Missing required skills: {missing_skills} (satisfied: {satisfied_skills}).",
            }
            missing.append(criterion_data)
            reasons.append(criterion_data["message"])

    @classmethod
    def _evaluate_age(
        cls,
        student: Dict[str, Any],
        opp: Dict[str, Any],
        satisfied: List[Dict[str, Any]],
        missing: List[Dict[str, Any]],
        unverified: List[Dict[str, Any]],
        reasons: List[str],
    ) -> None:
        min_age_val = opp.get("min_age")
        max_age_val = opp.get("max_age")
        age_limit_raw = opp.get("age_limit")

        # Parse age limit if passed as dict or string
        if isinstance(age_limit_raw, dict):
            min_age_val = age_limit_raw.get("min", min_age_val)
            max_age_val = age_limit_raw.get("max", max_age_val)
        elif age_limit_raw is not None and min_age_val is None and max_age_val is None:
            parsed_limit = cls._parse_number(age_limit_raw)
            if parsed_limit is not None:
                max_age_val = parsed_limit

        min_age = cls._parse_number(min_age_val)
        max_age = cls._parse_number(max_age_val)

        if min_age is None and max_age is None:
            return

        stu_age_raw = student.get("age") or student.get("student_age")
        if stu_age_raw is None:
            req_desc = f"Age between {min_age if min_age is not None else 0} and {max_age if max_age is not None else 'any'}"
            criterion_data = {
                "criterion": "age",
                "requirement": {"min_age": min_age, "max_age": max_age},
                "student_value": None,
                "message": f"Age requirement ({req_desc}) specified, but student age is not provided.",
            }
            unverified.append(criterion_data)
            reasons.append(criterion_data["message"])
            return

        stu_age = cls._parse_number(stu_age_raw)
        if stu_age is None:
            criterion_data = {
                "criterion": "age",
                "requirement": {"min_age": min_age, "max_age": max_age},
                "student_value": stu_age_raw,
                "message": f"Could not parse student age value '{stu_age_raw}'.",
            }
            unverified.append(criterion_data)
            reasons.append(criterion_data["message"])
            return

        # Check bounds
        if min_age is not None and stu_age < min_age:
            criterion_data = {
                "criterion": "age",
                "requirement": {"min_age": min_age, "max_age": max_age},
                "student_value": stu_age,
                "message": f"Student age ({int(stu_age)}) is below the minimum required age of {int(min_age)}.",
            }
            missing.append(criterion_data)
            reasons.append(criterion_data["message"])
        elif max_age is not None and stu_age > max_age:
            criterion_data = {
                "criterion": "age",
                "requirement": {"min_age": min_age, "max_age": max_age},
                "student_value": stu_age,
                "message": f"Student age ({int(stu_age)}) exceeds the maximum allowed age of {int(max_age)}.",
            }
            missing.append(criterion_data)
            reasons.append(criterion_data["message"])
        else:
            criterion_data = {
                "criterion": "age",
                "requirement": {"min_age": min_age, "max_age": max_age},
                "student_value": stu_age,
                "message": f"Student age ({int(stu_age)}) satisfies the age requirement.",
            }
            satisfied.append(criterion_data)
            reasons.append(criterion_data["message"])

    @classmethod
    def _evaluate_experience(
        cls,
        student: Dict[str, Any],
        opp: Dict[str, Any],
        satisfied: List[Dict[str, Any]],
        missing: List[Dict[str, Any]],
        unverified: List[Dict[str, Any]],
        reasons: List[str],
    ) -> None:
        min_exp_raw = (
            opp.get("min_experience")
            or opp.get("min_experience_years")
            or opp.get("experience_required")
            or opp.get("experience_years")
            or opp.get("experience")
        )
        if min_exp_raw is None:
            return

        min_exp = cls._parse_number(min_exp_raw)
        if min_exp is None or min_exp <= 0:
            return

        stu_exp_raw = None
        for k in ("experience", "experience_years", "years_of_experience", "total_experience"):
            if k in student and student[k] is not None:
                stu_exp_raw = student[k]
                break

        if stu_exp_raw is None or (isinstance(stu_exp_raw, str) and not stu_exp_raw.strip()):
            criterion_data = {
                "criterion": "experience",
                "requirement": min_exp,
                "student_value": None,
                "message": f"Minimum experience of {min_exp} years required, but student experience is not specified.",
            }
            unverified.append(criterion_data)
            reasons.append(criterion_data["message"])
            return

        stu_exp = cls._parse_number(stu_exp_raw)
        if stu_exp is None:
            criterion_data = {
                "criterion": "experience",
                "requirement": min_exp,
                "student_value": stu_exp_raw,
                "message": f"Could not parse student experience '{stu_exp_raw}'.",
            }
            unverified.append(criterion_data)
            reasons.append(criterion_data["message"])
            return

        if stu_exp >= min_exp:
            criterion_data = {
                "criterion": "experience",
                "requirement": min_exp,
                "student_value": stu_exp,
                "message": f"Student experience ({stu_exp} years) satisfies the required minimum of {min_exp} years.",
            }
            satisfied.append(criterion_data)
            reasons.append(criterion_data["message"])
        else:
            criterion_data = {
                "criterion": "experience",
                "requirement": min_exp,
                "student_value": stu_exp,
                "message": f"Student has {stu_exp} years of experience, which is less than the required {min_exp} years.",
            }
            missing.append(criterion_data)
            reasons.append(criterion_data["message"])

    @classmethod
    def _evaluate_score(
        cls,
        student: Dict[str, Any],
        opp: Dict[str, Any],
        satisfied: List[Dict[str, Any]],
        missing: List[Dict[str, Any]],
        unverified: List[Dict[str, Any]],
        reasons: List[str],
    ) -> None:
        min_score_raw = (
            opp.get("min_gpa")
            or opp.get("min_percentage")
            or opp.get("min_score")
            or opp.get("cutoff_marks")
        )
        if min_score_raw is None:
            return

        min_score = cls._parse_number(min_score_raw)
        if min_score is None:
            return

        stu_score_raw = None
        for k in ("gpa", "percentage", "score", "cgpa", "marks"):
            if k in student and student[k] is not None:
                stu_score_raw = student[k]
                break

        if stu_score_raw is None or (isinstance(stu_score_raw, str) and not stu_score_raw.strip()):
            criterion_data = {
                "criterion": "score",
                "requirement": min_score,
                "student_value": None,
                "message": f"Minimum score of {min_score} required, but student score is not provided.",
            }
            unverified.append(criterion_data)
            reasons.append(criterion_data["message"])
            return

        stu_score = cls._parse_number(stu_score_raw)
        if stu_score is None:
            criterion_data = {
                "criterion": "score",
                "requirement": min_score,
                "student_value": stu_score_raw,
                "message": f"Could not parse student score '{stu_score_raw}'.",
            }
            unverified.append(criterion_data)
            reasons.append(criterion_data["message"])
            return

        if stu_score >= min_score:
            criterion_data = {
                "criterion": "score",
                "requirement": min_score,
                "student_value": stu_score,
                "message": f"Student score ({stu_score}) meets or exceeds the required minimum score of {min_score}.",
            }
            satisfied.append(criterion_data)
            reasons.append(criterion_data["message"])
        else:
            criterion_data = {
                "criterion": "score",
                "requirement": min_score,
                "student_value": stu_score,
                "message": f"Student score ({stu_score}) is below the required minimum score of {min_score}.",
            }
            missing.append(criterion_data)
            reasons.append(criterion_data["message"])

    @classmethod
    def _evaluate_certifications(
        cls,
        student: Dict[str, Any],
        opp: Dict[str, Any],
        satisfied: List[Dict[str, Any]],
        missing: List[Dict[str, Any]],
        unverified: List[Dict[str, Any]],
        reasons: List[str],
    ) -> None:
        req_certs_raw = opp.get("required_certifications") or opp.get("certifications")
        if req_certs_raw is None:
            return

        req_certs = cls._normalize_string_list(req_certs_raw)
        if not req_certs:
            return

        stu_has_certs_field = False
        stu_certs_raw = None
        for k in ("certifications", "certified_in", "certificates"):
            if k in student:
                stu_has_certs_field = True
                stu_certs_raw = student[k]
                break

        if not stu_has_certs_field or stu_certs_raw is None:
            criterion_data = {
                "criterion": "certifications",
                "requirement": req_certs,
                "student_value": None,
                "message": f"Required certifications {req_certs} cannot be verified because student certifications are not specified.",
            }
            unverified.append(criterion_data)
            reasons.append(criterion_data["message"])
            return

        stu_certs = set(cls._normalize_string_list(stu_certs_raw))
        satisfied_certs = [c for c in req_certs if any(c == sc or c in sc or sc in c for sc in stu_certs)]
        missing_certs = [c for c in req_certs if c not in satisfied_certs]

        if not missing_certs:
            criterion_data = {
                "criterion": "certifications",
                "requirement": req_certs,
                "student_value": list(stu_certs),
                "message": f"All required certifications satisfied: {satisfied_certs}.",
            }
            satisfied.append(criterion_data)
            reasons.append(criterion_data["message"])
        else:
            criterion_data = {
                "criterion": "certifications",
                "requirement": req_certs,
                "student_value": list(stu_certs),
                "satisfied_certifications": satisfied_certs,
                "missing_certifications": missing_certs,
                "message": f"Missing required certifications: {missing_certs}.",
            }
            missing.append(criterion_data)
            reasons.append(criterion_data["message"])
