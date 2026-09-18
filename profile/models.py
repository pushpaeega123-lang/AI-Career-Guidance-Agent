import json
from db import db

class StudentProfile(db.Model):
    """
    Student Profile Model.
    Stores student demographics, education level, skills, interests, work styles,
    and career preferences for pathway guidance.
    """
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    education_level = db.Column(db.String(50), nullable=True)
    subjects_json = db.Column(db.Text, nullable=True)
    skills_json = db.Column(db.Text, nullable=True)
    interests_json = db.Column(db.Text, nullable=True)
    work_preferences_json = db.Column(db.Text, nullable=True)
    career_preferences_json = db.Column(db.Text, nullable=True)
    additional_information = db.Column(db.Text, nullable=True)

    def _parse_json_list(self, raw_json):
        if not raw_json:
            return []
        try:
            val = json.loads(raw_json)
            return val if isinstance(val, list) else [val]
        except Exception:
            return [raw_json]

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "education_level": self.education_level,
            "subjects": self._parse_json_list(self.subjects_json),
            "skills": self._parse_json_list(self.skills_json),
            "interests": self._parse_json_list(self.interests_json),
            "work_preferences": self._parse_json_list(self.work_preferences_json),
            "career_preferences": self._parse_json_list(self.career_preferences_json),
            "additional_information": self.additional_information
        }

