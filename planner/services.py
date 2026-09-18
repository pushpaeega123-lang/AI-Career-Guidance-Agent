from typing import Any, Dict, List, Optional
from db import db
from profile.models import StudentProfile
from skill_gap.services import SkillGapService
from .models import ActionPlan


class PlannerService:
    """
    Personalized Career Action Planner Service.
    Transforms student goals, profiles, and skill gaps into sequential milestone roadmaps.
    """

    @classmethod
    def generate_milestones(
        cls,
        target_role: str,
        current_skills: Any = None,
        skill_gaps: Any = None,
        education_level: Optional[str] = None,
        timeline_months: int = 6,
        eligibility_status: Optional[str] = None,
        eligibility_result: Optional[Dict[str, Any]] = None,
        pathway_data: Optional[Dict[str, Any]] = None,
        learning_areas: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Synthesize a structured sequence of milestones across:
        1. Immediate (Weeks 1-2)
        2. Short-term (Month 1-2)
        3. Medium-term (Month 3-4)
        4. Long-term (Month 5-6)
        Personalized based on skill gaps, pathway context, and eligibility status.
        """
        role_title = target_role.strip() if target_role else "Target Career Role"

        # Format skill gap highlights for personalized descriptions
        gap_list: List[str] = []
        if isinstance(skill_gaps, (list, tuple, set)):
            gap_list = [str(s).strip() for s in skill_gaps if str(s).strip()]
        elif isinstance(skill_gaps, dict):
            if "missing_skills" in skill_gaps:
                gap_list = [str(s).strip() for s in skill_gaps["missing_skills"]]
            elif "critical" in skill_gaps or "recommended" in skill_gaps:
                gap_list = skill_gaps.get("critical", []) + skill_gaps.get("recommended", [])
        elif isinstance(skill_gaps, str) and skill_gaps.strip():
            gap_list = [s.strip() for s in skill_gaps.split(",") if s.strip()]

        top_gaps_str = ", ".join(gap_list[:4]) if gap_list else "core domain technologies"

        # Resolve eligibility status
        norm_elig = str(eligibility_status).strip().upper() if eligibility_status else None
        if not norm_elig and eligibility_result and isinstance(eligibility_result, dict):
            norm_elig = str(eligibility_result.get("status", "")).strip().upper()

        # Pathway-specific next steps or context
        pathway_next_step = None
        if pathway_data and isinstance(pathway_data, dict):
            pathway_next_step = pathway_data.get("next_step") or pathway_data.get("typical_next_step")

        # Configure Phase 1 & Phase 4 milestones based on eligibility state
        if norm_elig == "NOT_ELIGIBLE":
            m1_title = f"Prerequisite Qualification Action: Satisfy {role_title} Entry Criteria"
            m1_desc = (
                f"Review and satisfy unmet entry criteria for {role_title}. "
                f"Address missing prerequisite qualifications before advancing to direct application stages."
            )
            m1_cat = "Education"
            m11_title = f"Verify Eligibility & Submit Applications for {role_title}"
            m11_desc = (
                f"Re-verify eligibility requirements after satisfying prerequisite qualifications "
                f"and submit tailored applications for active openings."
            )
        elif norm_elig == "NEEDS_VERIFICATION":
            m1_title = f"Prerequisite Verification & Documentation for {role_title}"
            m1_desc = (
                f"Compile academic records, verify requirement details, and validate alignment "
                f"against prerequisite criteria for {role_title}."
            )
            m1_cat = "Preparation"
            m11_title = f"Active Application Submissions for {role_title}"
            m11_desc = f"Submit applications for verified {role_title} openings with complete supporting credentials."
        else:
            m1_title = f"Baseline Assessment & Pathway Setup for {role_title}"
            m1_desc = (
                pathway_next_step
                if pathway_next_step
                else f"Audit existing background, set up developer/academic tools, and map curriculum prerequisites for {role_title}."
            )
            m1_cat = "Preparation"
            m11_title = f"Active Application Submissions for {role_title}"
            m11_desc = f"Submit applications for relevant job openings, internships, or competitive opportunities with tailored pitches."

        milestones: List[Dict[str, Any]] = [
            # Phase 1: Immediate (Weeks 1 - 2)
            {
                "id": "m1",
                "phase": "immediate",
                "phase_label": "Immediate (Weeks 1-2)",
                "title": m1_title,
                "description": m1_desc,
                "category": m1_cat,
                "priority": "High",
                "timeframe": "Weeks 1-2",
                "status": "pending",
            },
            {
                "id": "m2",
                "phase": "immediate",
                "phase_label": "Immediate (Weeks 1-2)",
                "title": "Version Control & Project Portfolio Setup",
                "description": "Initialize a structured GitHub/GitLab profile with clean documentation and CI baseline for tracking practical work.",
                "category": "Experience",
                "priority": "Medium",
                "timeframe": "Weeks 1-2",
                "status": "pending",
            },

            # Phase 2: Short-Term (Month 1 - 2)
            {
                "id": "m3",
                "phase": "short_term",
                "phase_label": "Short-term (Month 1-2)",
                "title": f"Core Skill Gap Mastery: {top_gaps_str}",
                "description": f"Engage in structured coursework and hands-on exercises to close critical skill gaps ({top_gaps_str}).",
                "category": "Skill Development",
                "priority": "High",
                "timeframe": "Month 1-2",
                "status": "pending",
            },
            {
                "id": "m4",
                "phase": "short_term",
                "phase_label": "Short-term (Month 1-2)",
                "title": "Certification & Structured Learning Enrollment",
                "description": f"Enroll in accredited certifications or academic coursework aligned with {role_title} requirements.",
                "category": "Education",
                "priority": "Medium",
                "timeframe": "Month 1-2",
                "status": "pending",
            },
            {
                "id": "m5",
                "phase": "short_term",
                "phase_label": "Short-term (Month 1-2)",
                "title": f"Foundational Practical Project: {gap_list[0] if gap_list else 'Core Prototype'}",
                "description": f"Build and deploy a functional standalone prototype demonstrating core concepts in {top_gaps_str}.",
                "category": "Experience",
                "priority": "High",
                "timeframe": "Month 2",
                "status": "pending",
            },

            # Phase 3: Medium-Term (Month 3 - 4)
            {
                "id": "m6",
                "phase": "medium_term",
                "phase_label": "Medium-term (Month 3-4)",
                "title": f"Advanced System Design & Architecture for {role_title}",
                "description": "Learn production-grade architecture, scalable patterns, performance optimization, and industry best practices.",
                "category": "Skill Development",
                "priority": "Medium",
                "timeframe": "Month 3",
                "status": "pending",
            },
            {
                "id": "m7",
                "phase": "medium_term",
                "phase_label": "Medium-term (Month 3-4)",
                "title": "Comprehensive Capstone Project Implementation",
                "description": f"Develop an end-to-end full-lifecycle project specifically showcasing skills demanded in {role_title} opportunities ({top_gaps_str}).",
                "category": "Experience",
                "priority": "High",
                "timeframe": "Months 3-4",
                "status": "pending",
            },
            {
                "id": "m8",
                "phase": "medium_term",
                "phase_label": "Medium-term (Month 3-4)",
                "title": "Open Source Contribution & Community Engagement",
                "description": "Contribute bug fixes or features to active open-source repositories and publish technical walkthrough articles.",
                "category": "Preparation",
                "priority": "Low",
                "timeframe": "Month 4",
                "status": "pending",
            },

            # Phase 4: Long-Term (Month 5 - 6)
            {
                "id": "m9",
                "phase": "long_term",
                "phase_label": "Long-term (Month 5-6)",
                "title": "Targeted Resume & Technical Portfolio Polish",
                "description": f"Tailor resume, cover letters, and live demo links emphasizing demonstrated competencies in {role_title}.",
                "category": "Application",
                "priority": "High",
                "timeframe": "Month 5",
                "status": "pending",
            },
            {
                "id": "m10",
                "phase": "long_term",
                "phase_label": "Long-term (Month 5-6)",
                "title": "Technical & Behavioral Mock Interview Preparation",
                "description": "Simulate live technical coding challenges, system design rounds, and behavioral interview scenarios.",
                "category": "Preparation",
                "priority": "High",
                "timeframe": "Months 5-6",
                "status": "pending",
            },
            {
                "id": "m11",
                "phase": "long_term",
                "phase_label": "Long-term (Month 5-6)",
                "title": m11_title,
                "description": m11_desc,
                "category": "Application",
                "priority": "High",
                "timeframe": "Month 6",
                "status": "pending",
            },
        ]

        return milestones

    @classmethod
    def create_plan(
        cls,
        student_id: int,
        target_role: str,
        current_skills: Any = None,
        skill_gaps: Any = None,
        education_level: Optional[str] = None,
        timeline_months: int = 6,
        eligibility_status: Optional[str] = None,
        eligibility_result: Optional[Dict[str, Any]] = None,
        pathway_data: Optional[Dict[str, Any]] = None,
        learning_areas: Optional[List[Dict[str, Any]]] = None,
        reuse_existing: bool = False,
    ) -> ActionPlan:
        """
        Validate student and target role, generate milestone roadmap, and persist to database.
        If reuse_existing is True and a plan already exists for the student and target role, returns the existing plan.
        """
        if not target_role or not str(target_role).strip():
            raise ValueError("Target career role cannot be empty.")

        clean_role = target_role.strip()

        student = db.session.get(StudentProfile, student_id)
        if not student:
            if student_id == 1:
                student = StudentProfile(id=1, full_name="Student User", email="student@example.com", education_level="Bachelor's")
                db.session.add(student)
                db.session.commit()
            else:
                raise ValueError(f"Student profile with ID {student_id} not found.")

        # Check for existing plan if reuse_existing is requested
        if reuse_existing:
            existing_plan = (
                ActionPlan.query.filter_by(student_id=student.id, target_role=clean_role)
                .order_by(ActionPlan.created_at.desc())
                .first()
            )
            if existing_plan:
                return existing_plan

        # If education level was not provided, fall back to student's profile education level
        if not education_level and student.education_level:
            education_level = student.education_level

        milestones = cls.generate_milestones(
            target_role=clean_role,
            current_skills=current_skills,
            skill_gaps=skill_gaps,
            education_level=education_level,
            timeline_months=timeline_months,
            eligibility_status=eligibility_status,
            eligibility_result=eligibility_result,
            pathway_data=pathway_data,
            learning_areas=learning_areas,
        )

        plan = ActionPlan(
            student_id=student.id,
            target_role=clean_role,
            timeline_months=int(timeline_months) if timeline_months else 6,
        )
        plan.set_milestones(milestones)

        db.session.add(plan)
        db.session.commit()

        return plan

    @classmethod
    def get_plan_by_id(cls, plan_id: int) -> Optional[ActionPlan]:
        """Retrieve action plan by plan ID."""
        return db.session.get(ActionPlan, plan_id)

    @classmethod
    def get_plans_by_student(cls, student_id: int) -> List[ActionPlan]:
        """Retrieve all action plans for a student ordered by creation date descending."""
        return (
            ActionPlan.query.filter_by(student_id=student_id)
            .order_by(ActionPlan.created_at.desc())
            .all()
        )

    @classmethod
    def update_milestone_status(
        cls,
        plan_id: int,
        milestone_id: str,
        new_status: str,
    ) -> ActionPlan:
        """
        Update the status ('pending', 'in_progress', 'completed') of a specific milestone in a plan.
        """
        plan = db.session.get(ActionPlan, plan_id)
        if not plan:
            raise ValueError(f"Action plan with ID {plan_id} not found.")

        normalized_status = str(new_status).strip().lower()
        if normalized_status not in ("pending", "in_progress", "completed"):
            raise ValueError(f"Invalid milestone status '{new_status}'. Allowed values: pending, in_progress, completed.")

        milestones = plan.get_milestones()
        found = False
        for m in milestones:
            if str(m.get("id")) == str(milestone_id):
                m["status"] = normalized_status
                found = True
                break

        if not found:
            raise ValueError(f"Milestone with ID '{milestone_id}' not found in action plan {plan_id}.")

        plan.set_milestones(milestones)
        db.session.commit()

        return plan
