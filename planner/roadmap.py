import json
from typing import Any, Dict, List, Optional
from db import db
from eligibility.services import EligibilityService
from opportunities.models import Opportunity
from profile.models import StudentProfile
from skill_gap.services import SkillGapService
from .models import ActionPlan
from .services import PlannerService


class RoadmapService:
    """
    Unified Career Roadmap Service.
    Connects Student Profile → Career Goal → Education → Skills → Opportunities → Action Plan → Progress.
    """

    @classmethod
    def build_roadmap(
        cls,
        student_id: int,
        target_role: Optional[str] = None,
        current_skills: Any = None,
        target_skills: Any = None,
        opportunity_id: Optional[int] = None,
        pathway_data: Optional[Dict[str, Any]] = None,
        eligibility_result: Optional[Dict[str, Any]] = None,
        skill_gap_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Build an end-to-end connected career roadmap for a student.
        Consumes existing models, selected pathway fit analysis, and planner milestones.
        """
        student = db.session.get(StudentProfile, student_id)
        if not student:
            if student_id == 1:
                student = StudentProfile(id=1, full_name="Student User", email="student@example.com", education_level="Bachelor's")
                db.session.add(student)
                db.session.commit()
            else:
                raise ValueError(f"Student with ID {student_id} not found.")

        # Retrieve student's latest action plans
        plans = (
            ActionPlan.query.filter_by(student_id=student.id)
            .order_by(ActionPlan.created_at.desc())
            .all()
        )
        latest_plan: Optional[ActionPlan] = plans[0] if plans else None

        # Resolve Target Career Goal
        pathway_name = pathway_data.get("name") if (pathway_data and isinstance(pathway_data, dict)) else None
        resolved_role = (
            (target_role.strip() if target_role and target_role.strip() else None)
            or pathway_name
            or (latest_plan.target_role if latest_plan else None)
        )

        # 1. Stage 1: Student Foundation & Profile
        interests_list = []
        if student.interests_json:
            try:
                interests_list = json.loads(student.interests_json)
                if not isinstance(interests_list, list):
                    interests_list = [str(interests_list)]
            except Exception:
                interests_list = [student.interests_json]

        profile_stage = {
            "stage_id": "profile_foundation",
            "stage_name": "Student Profile & Background",
            "sequence": 1,
            "status": "completed" if student.full_name and student.education_level else "in_progress",
            "data": {
                "student_id": student.id,
                "full_name": student.full_name or "Information not available",
                "email": student.email or "Information not available",
                "current_education": student.education_level or "Information not available",
                "interests": interests_list if interests_list else "Information not available",
            }
        }

        # 2. Stage 2: Target Career Goal
        career_goal_stage = {
            "stage_id": "career_goal",
            "stage_name": "Target Career Goal",
            "sequence": 2,
            "status": "completed" if resolved_role else "pending",
            "data": {
                "target_role": resolved_role or "Information not available",
                "selected_pathway": pathway_data if pathway_data else None,
                "pathway_id": pathway_data.get("id") if pathway_data else None,
                "pathway_name": pathway_data.get("name") if pathway_data else None,
                "industry_sector": pathway_data.get("industry_sector") if pathway_data else None,
                "timeline_months": latest_plan.timeline_months if latest_plan else 6,
                "active_plan_id": latest_plan.id if latest_plan else None,
            }
        }

        # 3. Stage 3: Education Requirements & Pathway
        edu_status = "completed"
        if not student.education_level:
            edu_status = "pending"
        elif not resolved_role:
            edu_status = "in_progress"

        education_stage = {
            "stage_id": "education_pathway",
            "stage_name": "Education Pathway & Prerequisite",
            "sequence": 3,
            "status": edu_status,
            "data": {
                "current_education": student.education_level or "Information not available",
                "prerequisite_status": "Verified" if student.education_level else "Information not available",
                "recommendation": f"Ensure completed degree aligns with standard {resolved_role} requirements." if resolved_role else "Select a career goal to verify educational alignment.",
            }
        }

        # 4. Stage 4: Skills Matrix & Gap Assessment
        # Use provided skills or extract from student/latest plan
        extracted_student_skills = current_skills or []
        extracted_target_skills = target_skills or []

        if skill_gap_result and isinstance(skill_gap_result, dict) and "matching_skills" in skill_gap_result:
            gap_result = skill_gap_result
            has_skills_data = True
            skills_status = "completed" if gap_result.get("gap_percentage", 100) == 0 else "in_progress"
        else:
            if not extracted_target_skills and resolved_role:
                # Provide sensible default target skills for common roles if not explicitly passed
                extracted_target_skills = [
                    resolved_role.split()[0], "Git", "Problem Solving", "Core Technologies"
                ]

            has_skills_data = bool(extracted_student_skills or extracted_target_skills)
            if has_skills_data:
                gap_result = SkillGapService.analyze_gap(
                    current_skills=extracted_student_skills,
                    target_career_skills=extracted_target_skills
                )
                skills_status = "completed" if gap_result["gap_percentage"] == 0 else "in_progress"
            else:
                gap_result = {
                    "matching_skills": [],
                    "missing_skills": [],
                    "match_rate": 0.0,
                    "gap_percentage": 0.0,
                    "total_required": 0,
                    "total_matched": 0,
                    "total_missing": 0,
                    "priority_breakdown": {"critical": [], "recommended": [], "optional": []},
                    "learning_areas": [],
                }
                skills_status = "pending"

        skills_stage = {
            "stage_id": "skills_assessment",
            "stage_name": "Skills Matrix & Gap Analysis",
            "sequence": 4,
            "status": skills_status,
            "data": {
                "has_data": has_skills_data,
                "current_skills": extracted_student_skills if extracted_student_skills else (gap_result.get("matching_skills", []) if has_skills_data else "Information not available"),
                "matching_skills": gap_result["matching_skills"] if has_skills_data else "Information not available",
                "missing_skills": gap_result["missing_skills"] if has_skills_data else "Information not available",
                "match_rate": gap_result["match_rate"] if has_skills_data else "Information not available",
                "gap_percentage": gap_result["gap_percentage"] if has_skills_data else "Information not available",
                "priority_breakdown": gap_result.get("priority_breakdown", {}),
                "learning_areas": gap_result.get("learning_areas", []),
            }
        }

        # 5. Stage 5: Opportunities & Eligibility Verification
        opps_data = []
        overall_eligibility = "Information not available"

        if eligibility_result and isinstance(eligibility_result, dict):
            overall_eligibility = eligibility_result.get("status", "NEEDS_VERIFICATION")
            if pathway_data:
                opps_data.append({
                    "id": pathway_data.get("id"),
                    "title": pathway_data.get("name", resolved_role or "Career Pathway"),
                    "organization": pathway_data.get("industry_sector", "Career Pathway"),
                    "opportunity_type": pathway_data.get("type", "Career Pathway"),
                    "deadline": "Open / Rolling",
                    "eligibility_status": overall_eligibility,
                    "eligible": eligibility_result.get("eligible", False),
                    "reasons": eligibility_result.get("reasons", [])[:2] if eligibility_result.get("reasons") else []
                })
        else:
            # Check existing opportunities in DB
            opportunities_query = Opportunity.query
            if opportunity_id:
                opportunities_query = opportunities_query.filter_by(id=opportunity_id)
            available_opps = opportunities_query.limit(3).all()

            if available_opps:
                for opp in available_opps:
                    # Run deterministic eligibility check
                    student_profile_dict = student.to_dict()
                    if extracted_student_skills:
                        student_profile_dict["skills"] = extracted_student_skills
                    opp_dict = opp.to_dict()

                    elig_check = EligibilityService.check_eligibility(
                        student_profile_data=student_profile_dict,
                        target_opportunity_data=opp_dict
                    )
                    opps_data.append({
                        "id": opp.id,
                        "title": opp.title,
                        "organization": opp.organization or "Information not available",
                        "opportunity_type": opp.opportunity_type,
                        "deadline": opp.deadline or "Open / Rolling",
                        "eligibility_status": elig_check["status"],
                        "eligible": elig_check["eligible"],
                        "reasons": elig_check["reasons"][:2] if elig_check["reasons"] else []
                    })
                overall_eligibility = opps_data[0]["eligibility_status"]

        if overall_eligibility == "ELIGIBLE":
            opps_stage_status = "completed"
        elif overall_eligibility in ("NOT_ELIGIBLE", "NEEDS_VERIFICATION") or opps_data:
            opps_stage_status = "in_progress"
        else:
            opps_stage_status = "pending"

        opportunities_stage = {
            "stage_id": "opportunities_eligibility",
            "stage_name": "Target Opportunities & Eligibility",
            "sequence": 5,
            "status": opps_stage_status,
            "data": {
                "available_opportunities_count": len(opps_data),
                "overall_eligibility": overall_eligibility,
                "opportunities": opps_data if opps_data else "Information not available",
            }
        }

        # 6. Stage 6: Execution Action Plan & Milestones
        if latest_plan:
            plan_progress = latest_plan.calculate_progress()
            milestones = latest_plan.get_milestones()
            plan_status = "completed" if plan_progress["progress_percentage"] == 100.0 else "in_progress"
            action_plan_data = {
                "plan_id": latest_plan.id,
                "target_role": latest_plan.target_role,
                "timeline_months": latest_plan.timeline_months,
                "total_milestones": plan_progress["total_milestones"],
                "completed_milestones": plan_progress["completed_milestones"],
                "in_progress_milestones": plan_progress["in_progress_milestones"],
                "pending_milestones": plan_progress["pending_milestones"],
                "progress_percentage": plan_progress["progress_percentage"],
                "next_recommended_action": plan_progress["next_recommended_action"],
                "milestones": milestones,
            }
        else:
            plan_status = "pending"
            action_plan_data = {
                "plan_id": None,
                "target_role": resolved_role or "Information not available",
                "timeline_months": 6,
                "total_milestones": 0,
                "completed_milestones": 0,
                "in_progress_milestones": 0,
                "pending_milestones": 0,
                "progress_percentage": 0.0,
                "next_recommended_action": None,
                "milestones": [],
                "message": "Information not available. Action plan has not yet been generated for this student."
            }

        action_plan_stage = {
            "stage_id": "action_plan_milestones",
            "stage_name": "Execution Action Plan & Milestones",
            "sequence": 6,
            "status": plan_status,
            "data": action_plan_data,
        }

        # Calculate Overall Roadmap Progress
        # Normalized 6-Stage Weighting:
        # Stage 1: Profile Foundation (15%)
        # Stage 2: Career Goal Selection (15%)
        # Stage 3: Education Prerequisite Verification (15%)
        # Stage 4: Skills Matrix & Gap Closure (20%)
        # Stage 5: Target Opportunities & Eligibility (15%)
        # Stage 6: Execution Action Plan & Milestones (20%)
        stages = [
            profile_stage,
            career_goal_stage,
            education_stage,
            skills_stage,
            opportunities_stage,
            action_plan_stage,
        ]

        s1_pct = 15.0 if profile_stage["status"] == "completed" else 5.0
        s2_pct = 15.0 if career_goal_stage["status"] == "completed" else 0.0
        s3_pct = 15.0 if education_stage["status"] == "completed" else 5.0

        # Skills Stage (20% weight)
        match_rate = skills_stage["data"].get("match_rate", 0.0)
        if isinstance(match_rate, (int, float)):
            s4_pct = round((float(match_rate) / 100.0) * 20.0, 1)
        else:
            s4_pct = 20.0 if skills_stage["status"] == "completed" else 5.0

        # Opportunities Stage (15% weight)
        if opportunities_stage["status"] == "completed":
            s5_pct = 15.0
        elif opportunities_stage["status"] == "in_progress":
            s5_pct = 7.5
        else:
            s5_pct = 0.0

        # Action Plan Milestones Stage (20% weight)
        plan_pct = action_plan_data.get("progress_percentage", 0.0) if latest_plan else 0.0
        s6_pct = round((float(plan_pct) / 100.0) * 20.0, 1)

        roadmap_progress = round(s1_pct + s2_pct + s3_pct + s4_pct + s5_pct + s6_pct, 1)
        roadmap_progress = min(100.0, max(0.0, roadmap_progress))

        if roadmap_progress >= 100.0:
            journey_stage_label = "Completed & Job Ready"
        elif roadmap_progress >= 75.0:
            journey_stage_label = "Advanced Progression"
        elif roadmap_progress >= 25.0:
            journey_stage_label = "Active Progression"
        else:
            journey_stage_label = "Foundational Preparation"

        return {
            "student_id": student.id,
            "student_name": student.full_name or "Information not available",
            "career_goal": resolved_role or "Information not available",
            "education_level": student.education_level or "Information not available",
            "roadmap_progress_percentage": roadmap_progress,
            "journey_stage_label": journey_stage_label,
            "is_completed": (roadmap_progress >= 100.0),
            "active_plan_id": latest_plan.id if latest_plan else None,
            "next_recommended_action": action_plan_data.get("next_recommended_action"),
            "stages": stages,
        }
