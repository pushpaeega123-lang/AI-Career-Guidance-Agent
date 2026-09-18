from db import db

class ActionPlan(db.Model):
    """
    Action Plan Model Foundation.
    To be expanded by Developer 4.
    """
    __tablename__ = 'action_plans'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    target_role = db.Column(db.String(120), nullable=False)
    timeline_months = db.Column(db.Integer, default=6)
    milestones_json = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "target_role": self.target_role,
            "timeline_months": self.timeline_months
        }
