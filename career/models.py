from db import db

class CareerPathway(db.Model):
    """
    Career Pathway Model Foundation.
    To be expanded by Developer 2.
    """
    __tablename__ = 'career_pathways'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    industry_sector = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "industry_sector": self.industry_sector
        }
