import re
from datetime import datetime
from db import db
from .models import StudentProfile

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

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


