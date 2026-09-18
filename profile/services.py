import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from flask import has_request_context, session
from db import db
from .models import StudentProfile

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')


class CareerDiscoveryService:
    """
    Service logic for Career Discovery Questionnaire & Exploration Profile Management.
    Collects structured education, skills, interests, work styles, and career preferences
    for students in exploration mode without making simplistic scoring assumptions.
    """

    @staticmethod
    def _normalize_string_list(raw_input: Any) -> List[str]:
        """
        Clean, strip, deduplicate, and normalize list or delimited inputs.
        Preserves original capitalization format while preventing duplicates.
        """
        if raw_input is None:
            return []

        items: List[str] = []
        if isinstance(raw_input, str):
            # Check if JSON string or comma-delimited
            raw_str = raw_input.strip()
            if not raw_str:
                return []
            if raw_str.startswith('[') and raw_str.endswith(']'):
                try:
                    parsed = json.loads(raw_str)
                    if isinstance(parsed, list):
                        items = [str(x).strip() for x in parsed if str(x).strip()]
                except Exception:
                    items = [x.strip() for x in raw_str.split(',') if x.strip()]
            else:
                items = [x.strip() for x in raw_str.split(',') if x.strip()]
        elif isinstance(raw_input, (list, tuple, set)):
            for item in raw_input:
                if item is not None:
                    cleaned = str(item).strip()
                    if cleaned:
                        items.append(cleaned)
        else:
            cleaned = str(raw_input).strip()
            if cleaned:
                items.append(cleaned)

        # Deduplicate while preserving order (case-insensitive deduplication)
        seen = set()
        deduped: List[str] = []
        for it in items:
            key = it.lower()
            if key not in seen:
                seen.add(key)
                deduped.append(it)

        return deduped

    @classmethod
    def validate_exploration_profile(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate exploration questionnaire payload.
        Enforces required education level and at least one skill or interest.
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid request payload. Expected a JSON object.")

        # 1. Education Level (Required)
        raw_edu = data.get("education_level") or data.get("education") or data.get("current_education")
        if raw_edu is None or not str(raw_edu).strip():
            raise ValueError("Education level is required.")
        education_level = str(raw_edu).strip()

        # 2. Subjects Enjoyed (Optional List)
        raw_subjects = data.get("subjects") or data.get("enjoyed_subjects") or []
        subjects = cls._normalize_string_list(raw_subjects)

        # 3. Current Skills (List)
        raw_skills = data.get("skills") or data.get("current_skills") or []
        skills = cls._normalize_string_list(raw_skills)

        # 4. Interests (List)
        raw_interests = data.get("interests") or data.get("career_interests") or []
        interests = cls._normalize_string_list(raw_interests)

        # Validation rule: At least one skill OR interest must be provided
        if not skills and not interests:
            raise ValueError("Please provide at least one current skill or interest to explore pathways.")

        # 5. Work Preferences (Optional List)
        raw_work = data.get("work_preferences") or data.get("preferred_work_style") or data.get("work_styles") or []
        work_preferences = cls._normalize_string_list(raw_work)

        # 6. Career Preferences (Optional List)
        raw_career_prefs = data.get("career_preferences") or data.get("sector_preferences") or []
        career_preferences = cls._normalize_string_list(raw_career_prefs)

        # 7. Additional Information (Optional Free-Text)
        raw_additional = data.get("additional_information") or data.get("additional_info") or data.get("notes") or ""
        additional_information = str(raw_additional).strip() if raw_additional else None

        return {
            "education_level": education_level,
            "subjects": subjects,
            "skills": skills,
            "interests": interests,
            "work_preferences": work_preferences,
            "career_preferences": career_preferences,
            "additional_information": additional_information
        }

    @classmethod
    def save_exploration_profile(
        cls,
        data: Dict[str, Any],
        session_obj: Optional[Dict[str, Any]] = None,
        student_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Validate and store the exploration profile into session and optionally database.
        """
        validated_profile = cls.validate_exploration_profile(data)

        # Session storage
        target_session = session_obj if session_obj is not None else (session if has_request_context() else None)
        if target_session is not None:
            target_session["career_direction"] = "exploring"
            target_session["target_role"] = None
            target_session.pop("selected_pathway", None)
            target_session.pop("shortlisted_pathways", None)
            target_session["exploration_profile"] = validated_profile

        # Optional database persistence if student_id provided
        if student_id is not None:
            try:
                profile = db.session.get(StudentProfile, student_id)
                if profile:
                    profile.education_level = validated_profile["education_level"]
                    profile.subjects_json = json.dumps(validated_profile["subjects"])
                    profile.skills_json = json.dumps(validated_profile["skills"])
                    profile.interests_json = json.dumps(validated_profile["interests"])
                    profile.work_preferences_json = json.dumps(validated_profile["work_preferences"])
                    profile.career_preferences_json = json.dumps(validated_profile["career_preferences"])
                    profile.additional_information = validated_profile["additional_information"]
                    db.session.commit()
            except Exception:
                db.session.rollback()

        return {
            "status": "success",
            "career_direction": "exploring",
            "target_role": None,
            "is_completed": True,
            "student_profile": validated_profile,
            "message": "Career exploration profile successfully saved. Ready for pathway discovery."
        }

    @classmethod
    def get_exploration_profile(cls, session_obj: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieve stored exploration profile from session.
        """
        target_session = session_obj if session_obj is not None else (session if has_request_context() else None)
        if target_session is not None:
            profile = target_session.get("exploration_profile")
            direction = target_session.get("career_direction") or "exploring"
            return {
                "status": "success",
                "career_direction": direction,
                "target_role": target_session.get("target_role") if direction == "known" else None,
                "student_profile": profile,
                "is_set": bool(profile)
            }

        return {
            "status": "success",
            "career_direction": None,
            "target_role": None,
            "student_profile": None,
            "is_set": False
        }

    @classmethod
    def clear_exploration_profile(cls, session_obj: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Reset exploration profile and clear session state.
        """
        target_session = session_obj if session_obj is not None else (session if has_request_context() else None)
        if target_session is not None:
            target_session.pop("exploration_profile", None)

        return {
            "status": "success",
            "message": "Career exploration profile cleared.",
            "student_profile": None,
            "is_set": False
        }


class ProfileService:
    """
    Service logic for Student Profile & Interest Intelligence foundation.
    Encapsulates validation, database transactions, and business logic.
    """

    @staticmethod
    def validate_profile_input(data: dict, is_update: bool = False, profile_id: int = None) -> tuple[bool, str | None]:
        """Validates incoming profile payload."""
        if not isinstance(data, dict):
            return False, "Request payload must be a JSON object"

        # Full name validation (required for create, optional for update)
        if not is_update or 'full_name' in data:
            full_name = data.get('full_name')
            if not full_name or not isinstance(full_name, str) or len(full_name.strip()) < 2:
                return False, "Full name is required and must be at least 2 characters"

        # Email validation (required for create, optional for update)
        if not is_update or 'email' in data:
            email = data.get('email')
            if not email or not isinstance(email, str) or not EMAIL_REGEX.match(email.strip()):
                return False, "A valid email address is required (e.g. user@example.com)"
            
            # Check for existing duplicate email
            normalized_email = email.strip().lower()
            existing = StudentProfile.query.filter_by(email=normalized_email).first()
            if existing:
                if not is_update or (profile_id is not None and existing.id != profile_id):
                    return False, f"A profile with email '{normalized_email}' already exists"

        return True, None

    @staticmethod
    def create_profile(data: dict) -> tuple[StudentProfile | None, str | None]:
        """Creates a new student profile after input validation."""
        is_valid, error = ProfileService.validate_profile_input(data, is_update=False)
        if not is_valid:
            return None, error

        try:
            profile = StudentProfile(
                full_name=data['full_name'].strip(),
                email=data['email'].strip().lower(),
                education_level=data.get('education_level', '').strip() if data.get('education_level') else None,
                qualification=data.get('qualification', '').strip() if data.get('qualification') else None,
                career_goals=data.get('career_goals', '').strip() if data.get('career_goals') else None,
                location=data.get('location', '').strip() if data.get('location') else None
            )

            # Assign structured fields through model setters
            if 'degree_details' in data:
                profile.set_degree_details(data['degree_details'])
            if 'diploma_details' in data:
                profile.set_diploma_details(data['diploma_details'])
            if 'pg_details' in data:
                profile.set_pg_details(data['pg_details'])
            if 'skills' in data:
                profile.set_skills(data['skills'])
            if 'interests' in data:
                profile.set_interests(data['interests'])
            if 'preferred_locations' in data:
                profile.set_preferred_locations(data['preferred_locations'])
            if 'preferences' in data:
                profile.set_preferences(data['preferences'])

            db.session.add(profile)
            db.session.commit()
            return profile, None
        except Exception as e:
            db.session.rollback()
            return None, f"Database error creating profile: {str(e)}"

    @staticmethod
    def get_profile_by_id(profile_id: int) -> StudentProfile | None:
        """Fetch a single profile by primary key."""
        if not isinstance(profile_id, int):
            try:
                profile_id = int(profile_id)
            except (ValueError, TypeError):
                return None
        return db.session.get(StudentProfile, profile_id)

    @staticmethod
    def get_profile_by_email(email: str) -> StudentProfile | None:
        """Fetch a single profile by email address."""
        if not email or not isinstance(email, str):
            return None
        return StudentProfile.query.filter_by(email=email.strip().lower()).first()

    @staticmethod
    def update_profile(profile_id: int, data: dict) -> tuple[StudentProfile | None, str | None]:
        """Updates an existing student profile."""
        profile = ProfileService.get_profile_by_id(profile_id)
        if not profile:
            return None, f"Profile with ID {profile_id} not found"

        is_valid, error = ProfileService.validate_profile_input(data, is_update=True, profile_id=profile.id)
        if not is_valid:
            return None, error

        try:
            if 'full_name' in data and data['full_name']:
                profile.full_name = data['full_name'].strip()
            if 'email' in data and data['email']:
                profile.email = data['email'].strip().lower()
            if 'education_level' in data:
                profile.education_level = data['education_level'].strip() if data['education_level'] else None
            if 'qualification' in data:
                profile.qualification = data['qualification'].strip() if data['qualification'] else None
            if 'career_goals' in data:
                profile.career_goals = data['career_goals'].strip() if data['career_goals'] else None
            if 'location' in data:
                profile.location = data['location'].strip() if data['location'] else None

            # Update structured fields
            if 'degree_details' in data:
                profile.set_degree_details(data['degree_details'])
            if 'diploma_details' in data:
                profile.set_diploma_details(data['diploma_details'])
            if 'pg_details' in data:
                profile.set_pg_details(data['pg_details'])
            if 'skills' in data:
                profile.set_skills(data['skills'])
            if 'interests' in data:
                profile.set_interests(data['interests'])
            if 'preferred_locations' in data:
                profile.set_preferred_locations(data['preferred_locations'])
            if 'preferences' in data:
                profile.set_preferences(data['preferences'])

            profile.updated_at = datetime.utcnow()
            db.session.commit()
            return profile, None
        except Exception as e:
            db.session.rollback()
            return None, f"Database error updating profile: {str(e)}"

    @staticmethod
    def list_profiles(limit: int = 50, offset: int = 0) -> list[StudentProfile]:
        """Lists student profiles with pagination."""
        return StudentProfile.query.order_by(StudentProfile.id.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def delete_profile(profile_id: int) -> tuple[bool, str | None]:
        """Deletes a student profile."""
        profile = ProfileService.get_profile_by_id(profile_id)
        if not profile:
            return False, f"Profile with ID {profile_id} not found"

        try:
            db.session.delete(profile)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f"Database error deleting profile: {str(e)}"

    @staticmethod
    def analyze_student_interests(profile_id: int = None, interests=None) -> tuple[dict | None, str | None]:
        """
        Analyzes interests either supplied directly or retrieved from a stored StudentProfile.
        Reuses the central InterestIntelligenceService.
        """
        from .interest_intelligence import InterestIntelligenceService

        target_interests = interests
        if profile_id is not None:
            profile = ProfileService.get_profile_by_id(profile_id)
            if not profile:
                return None, f"Profile with ID {profile_id} not found"
            if target_interests is None:
                target_interests = profile.get_interests()

        analysis = InterestIntelligenceService.analyze_interests(target_interests)
        return analysis, None



