from db import db

class Opportunity(db.Model):
    """
    Opportunity Model Foundation (Jobs, Govt Jobs, Exams, Internships, Scholarships).
    To be expanded by Developer 3.
    """
    __tablename__ = 'opportunities'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    opportunity_type = db.Column(db.String(50), nullable=False) # job, govt_job, exam, internship, scholarship
    organization = db.Column(db.String(150), nullable=True)
    deadline = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "opportunity_type": self.opportunity_type,
            "organization": self.organization,
            "deadline": self.deadline
        }
