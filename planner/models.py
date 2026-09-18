from datetime import datetime
import json
from db import db


class ActionPlan(db.Model):
    """
    Action Plan Model representing personalized career roadmaps and milestones.
    """
    __tablename__ = 'action_plans'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    target_role = db.Column(db.String(120), nullable=False)
    timeline_months = db.Column(db.Integer, default=6)
    milestones_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_milestones(self):
        """Retrieve decoded list of milestones."""
        if not self.milestones_json:
            return []
        try:
            return json.loads(self.milestones_json)
        except (ValueError, TypeError):
            return []

    def set_milestones(self, milestones):
        """Serialize and store milestones list as JSON string."""
        self.milestones_json = json.dumps(milestones)

    def calculate_progress(self):
        """Calculate progress metrics and identify next recommended milestone."""
        milestones = self.get_milestones()
        total = len(milestones)
        if total == 0:
            return {
                "total_milestones": 0,
                "completed_milestones": 0,
                "in_progress_milestones": 0,
                "pending_milestones": 0,
                "progress_percentage": 0.0,
                "next_recommended_action": None
            }

        completed = sum(1 for m in milestones if m.get("status") == "completed")
        in_progress = sum(1 for m in milestones if m.get("status") == "in_progress")
        pending = sum(1 for m in milestones if m.get("status") == "pending")
        progress_percentage = round((completed / total) * 100.0, 2)

        # Determine next recommended action: first 'in_progress', else first 'pending'
        next_action = None
        for m in milestones:
            if m.get("status") == "in_progress":
                next_action = m
                break
        if not next_action:
            for m in milestones:
                if m.get("status") == "pending":
                    next_action = m
                    break

        return {
            "total_milestones": total,
            "completed_milestones": completed,
            "in_progress_milestones": in_progress,
            "pending_milestones": pending,
            "progress_percentage": progress_percentage,
            "next_recommended_action": next_action
        }

    def to_dict(self):
        """Serialize ActionPlan with milestone details and computed progress."""
        progress = self.calculate_progress()
        return {
            "id": self.id,
            "student_id": self.student_id,
            "target_role": self.target_role,
            "timeline_months": self.timeline_months,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "milestones": self.get_milestones(),
            "total_milestones": progress["total_milestones"],
            "completed_milestones": progress["completed_milestones"],
            "in_progress_milestones": progress["in_progress_milestones"],
            "pending_milestones": progress["pending_milestones"],
            "progress_percentage": progress["progress_percentage"],
            "next_recommended_action": progress["next_recommended_action"]
        }
