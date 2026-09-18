from db import db

class StudentProfile(db.Model):
    """
    Student Profile Model Foundation.
    To be expanded by Developer 1.
    """
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    education_level = db.Column(db.String(50), nullable=True)
    interests_json = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "education_level": self.education_level
        }
