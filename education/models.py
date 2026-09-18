from db import db

class EducationCourse(db.Model):
    """
    Education Pathway Model Foundation.
    To be expanded by Developer 2.
    """
    __tablename__ = 'education_courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    institution = db.Column(db.String(150), nullable=True)
    degree_level = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "institution": self.institution,
            "degree_level": self.degree_level
        }
