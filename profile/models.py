import json
from datetime import datetime
from db import db

class StudentProfile(db.Model):
    """
    Student Profile Model.
    Supports comprehensive academic, skill, interest, and career preference intelligence.
    Maintains compatibility with downstream ActionPlan foreign keys (student_profiles.id).
    """
    __tablename__ = 'student_profiles'

    # Primary key (Kept intact for Member 4 ActionPlan foreign key compatibility)
    id = db.Column(db.Integer, primary_key=True)

    # Basic Info
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    education_level = db.Column(db.String(100), nullable=True) # e.g. Undergraduate, Diploma, Postgraduate, High School
    qualification = db.Column(db.String(150), nullable=True)   # Current qualification / summary

    # Detailed Educational Stages (JSON text for schema stability and nested flexibility)
    degree_details_json = db.Column(db.Text, nullable=True)
    diploma_details_json = db.Column(db.Text, nullable=True)
    pg_details_json = db.Column(db.Text, nullable=True)

    # Skills & Interests Intelligence
    skills_json = db.Column(db.Text, nullable=True)
    interests_json = db.Column(db.Text, nullable=True)

    # Goals and Geographical / Work Preferences
    career_goals = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(150), nullable=True)
    preferred_locations_json = db.Column(db.Text, nullable=True)
    preferences_json = db.Column(db.Text, nullable=True) # Work mode, study preferences

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- JSON Helper Methods ---
    @staticmethod
    def _parse_json_field(val, default_type=list):
        if not val:
            return default_type()
        if isinstance(val, (list, dict)):
            return val
        try:
            return json.loads(val)
        except (ValueError, TypeError):
            if default_type == list and isinstance(val, str):
                return [item.strip() for item in val.split(',') if item.strip()]
            return default_type()

    # --- Getters and Setters ---
    def get_skills(self):
        return self._parse_json_field(self.skills_json, list)

    def set_skills(self, skills):
        if isinstance(skills, list):
            self.skills_json = json.dumps([str(s).strip() for s in skills if str(s).strip()])
        elif isinstance(skills, str):
            items = [s.strip() for s in skills.split(',') if s.strip()]
            self.skills_json = json.dumps(items)
        else:
            self.skills_json = json.dumps([])

    def get_interests(self):
        return self._parse_json_field(self.interests_json, list)

    def set_interests(self, interests):
        if isinstance(interests, list):
            self.interests_json = json.dumps([str(i).strip() for i in interests if str(i).strip()])
        elif isinstance(interests, str):
            items = [i.strip() for i in interests.split(',') if i.strip()]
            self.interests_json = json.dumps(items)
        else:
            self.interests_json = json.dumps([])

    def get_preferred_locations(self):
        return self._parse_json_field(self.preferred_locations_json, list)

    def set_preferred_locations(self, locations):
        if isinstance(locations, list):
            self.preferred_locations_json = json.dumps([str(loc).strip() for loc in locations if str(loc).strip()])
        elif isinstance(locations, str):
            items = [l.strip() for l in locations.split(',') if l.strip()]
            self.preferred_locations_json = json.dumps(items)
        else:
            self.preferred_locations_json = json.dumps([])

    def get_degree_details(self):
        return self._parse_json_field(self.degree_details_json, dict)

    def set_degree_details(self, details):
        if isinstance(details, dict):
            self.degree_details_json = json.dumps(details)
        elif isinstance(details, str) and details.strip():
            try:
                self.degree_details_json = json.dumps(json.loads(details))
            except Exception:
                self.degree_details_json = json.dumps({"description": details.strip()})
        else:
            self.degree_details_json = json.dumps({})

    def get_diploma_details(self):
        return self._parse_json_field(self.diploma_details_json, dict)

    def set_diploma_details(self, details):
        if isinstance(details, dict):
            self.diploma_details_json = json.dumps(details)
        elif isinstance(details, str) and details.strip():
            try:
                self.diploma_details_json = json.dumps(json.loads(details))
            except Exception:
                self.diploma_details_json = json.dumps({"description": details.strip()})
        else:
            self.diploma_details_json = json.dumps({})

    def get_pg_details(self):
        return self._parse_json_field(self.pg_details_json, dict)

    def set_pg_details(self, details):
        if isinstance(details, dict):
            self.pg_details_json = json.dumps(details)
        elif isinstance(details, str) and details.strip():
            try:
                self.pg_details_json = json.dumps(json.loads(details))
            except Exception:
                self.pg_details_json = json.dumps({"description": details.strip()})
        else:
            self.pg_details_json = json.dumps({})

    def get_preferences(self):
        return self._parse_json_field(self.preferences_json, dict)

    def set_preferences(self, prefs):
        if isinstance(prefs, dict):
            self.preferences_json = json.dumps(prefs)
        elif isinstance(prefs, str) and prefs.strip():
            try:
                self.preferences_json = json.dumps(json.loads(prefs))
            except Exception:
                self.preferences_json = json.dumps({"notes": prefs.strip()})
        else:
            self.preferences_json = json.dumps({})

    def to_dict(self):
        """Standardized serialization for API responses and downstream module consumption."""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "education_level": self.education_level or "",
            "qualification": self.qualification or "",
            "degree_details": self.get_degree_details(),
            "diploma_details": self.get_diploma_details(),
            "pg_details": self.get_pg_details(),
            "skills": self.get_skills(),
            "interests": self.get_interests(),
            "career_goals": self.career_goals or "",
            "location": self.location or "",
            "preferred_locations": self.get_preferred_locations(),
            "preferences": self.get_preferences(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
