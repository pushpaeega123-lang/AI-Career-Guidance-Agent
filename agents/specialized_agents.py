from typing import Any, Dict
from career.services import PathwayAnalysisService, PathwayDiscoveryService
from eligibility.services import EligibilityService
from planner.roadmap import RoadmapService
from planner.services import PlannerService
from skill_gap.services import SkillGapService
from .base_agent import BaseAgent



class EligibilityAgent(BaseAgent):
    """
    Specialized Domain Agent for evaluating student eligibility against opportunities.
    """
    def __init__(self):
        super().__init__(
            agent_name="EligibilityAgent",
            description="Evaluates student qualifications, degrees, skills, age, and experience against target opportunities."
        )

    def process_task(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        student_data = (
            task_input.get("student_profile")
            or task_input.get("student")
            or task_input.get("profile")
            or {}
        )
        opportunity_data = (
            task_input.get("opportunity")
            or task_input.get("requirements")
            or task_input.get("pathway")
            or {}
        )

        result = EligibilityService.check_eligibility(
            student_profile_data=student_data,
            target_opportunity_data=opportunity_data
        )

        explanation = f"Eligibility status: {result['status']}. " + " ".join(result.get("reasons", []))
        return {
            "status": "success",
            "agent": self.agent_name,
            "data": result,
            "explanation": explanation
        }


class SkillGapAgent(BaseAgent):
    """
    Specialized Domain Agent for analyzing skill gaps between current student abilities and target roles.
    """
    def __init__(self):
        super().__init__(
            agent_name="SkillGapAgent",
            description="Analyzes required vs possessed skills, calculates match and gap rates, and maps learning areas."
        )

    def process_task(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        current_skills = (
            task_input.get("current_skills")
            or task_input.get("student_skills")
            or task_input.get("skills")
            or []
        )
        target_skills = (
            task_input.get("target_skills")
            or task_input.get("target_career_skills")
            or task_input.get("required_skills")
            or []
        )

        result = SkillGapService.analyze_gap(
            current_skills=current_skills,
            target_career_skills=target_skills
        )

        explanation = (
            f"Skill match rate is {result['match_rate']}%, with a skill gap of {result['gap_percentage']}%. "
            f"Identified {len(result['matching_skills'])} matching skills and {len(result['missing_skills'])} missing skills."
        )

        return {
            "status": "success",
            "agent": self.agent_name,
            "data": result,
            "explanation": explanation
        }


class PlannerAgent(BaseAgent):
    """
    Specialized Domain Agent for generating sequential career action plans and milestones.
    """
    def __init__(self):
        super().__init__(
            agent_name="PlannerAgent",
            description="Transforms career goals and identified skill gaps into 4-phase sequential action milestones."
        )

    def process_task(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        student_id = task_input.get("student_id")
        selected_pathway = task_input.get("selected_pathway") or task_input.get("pathway")
        target_role = (
            task_input.get("target_role")
            or task_input.get("role")
            or task_input.get("career_goal")
            or (selected_pathway.get("name") if isinstance(selected_pathway, dict) else (selected_pathway if isinstance(selected_pathway, str) else None))
        )
        current_skills = task_input.get("current_skills") or task_input.get("skills")
        if not current_skills and isinstance(task_input.get("student_profile"), dict):
            current_skills = task_input["student_profile"].get("skills")

        skill_gap_obj = task_input.get("skill_gap") or task_input.get("skill_gap_result")
        skill_gaps = task_input.get("skill_gaps") or task_input.get("missing_skills")
        if not skill_gaps and isinstance(skill_gap_obj, dict):
            skill_gaps = skill_gap_obj.get("missing_skills")

        learning_areas = task_input.get("learning_areas")
        if not learning_areas and isinstance(skill_gap_obj, dict):
            learning_areas = skill_gap_obj.get("learning_areas")

        elig_obj = task_input.get("eligibility") or task_input.get("eligibility_result")
        elig_status = task_input.get("eligibility_status") or (elig_obj.get("status") if isinstance(elig_obj, dict) else None)

        education_level = task_input.get("education_level")
        if not education_level and isinstance(task_input.get("student_profile"), dict):
            education_level = task_input["student_profile"].get("education_level")

        timeline_months = task_input.get("timeline_months", 6)
        reuse_existing = task_input.get("reuse_existing", False)

        if not target_role or not str(target_role).strip():
            raise ValueError("PlannerAgent requires a non-empty target_role or selected_pathway.")

        pathway_dict = selected_pathway if isinstance(selected_pathway, dict) else None
        selected_pathway_repr = (
            pathway_dict.get("name")
            if pathway_dict
            else (str(selected_pathway) if selected_pathway else target_role)
        )

        if student_id:
            # Create persistent plan if student_id is provided
            plan = PlannerService.create_plan(
                student_id=student_id,
                target_role=target_role,
                current_skills=current_skills,
                skill_gaps=skill_gaps,
                education_level=education_level,
                timeline_months=timeline_months,
                eligibility_status=elig_status,
                eligibility_result=elig_obj if isinstance(elig_obj, dict) else None,
                pathway_data=pathway_dict,
                learning_areas=learning_areas,
                reuse_existing=reuse_existing,
            )
            data = plan.to_dict()
            plan_id = plan.id
            milestone_count = data.get("total_milestones", len(data.get("milestones", [])))
            progress = data.get("progress_percentage", 0.0)
            next_action_obj = data.get("next_recommended_action")
            next_action_title = next_action_obj.get("title") if isinstance(next_action_obj, dict) else (str(next_action_obj) if next_action_obj else "Start Phase 1")
        else:
            # Generate standalone milestone sequence
            milestones = PlannerService.generate_milestones(
                target_role=target_role,
                current_skills=current_skills,
                skill_gaps=skill_gaps,
                education_level=education_level,
                timeline_months=timeline_months,
                eligibility_status=elig_status,
                eligibility_result=elig_obj if isinstance(elig_obj, dict) else None,
                pathway_data=pathway_dict,
                learning_areas=learning_areas,
            )
            plan_id = None
            milestone_count = len(milestones)
            progress = 0.0
            next_action_obj = milestones[0] if milestones else None
            next_action_title = next_action_obj.get("title") if next_action_obj else "None"
            data = {
                "id": None,
                "student_id": None,
                "target_role": target_role,
                "timeline_months": timeline_months,
                "milestones": milestones,
                "total_milestones": milestone_count,
                "completed_milestones": 0,
                "in_progress_milestones": 0,
                "pending_milestones": milestone_count,
                "progress_percentage": progress,
                "next_recommended_action": next_action_obj,
            }

        explanation = (
            f"Generated {milestone_count} actionable milestones across 4 phases for '{target_role}'. "
            f"Next recommended step: {next_action_title}."
        )

        return {
            "status": "success",
            "agent": self.agent_name,
            "action": "create_action_plan",
            "selected_pathway": selected_pathway_repr,
            "plan_id": plan_id,
            "milestone_count": milestone_count,
            "progress": progress,
            "next_action": next_action_title,
            "data": data,
            "explanation": explanation
        }


class RoadmapAgent(BaseAgent):
    """
    Specialized Domain Agent for synthesizing the unified career roadmap across all stages.
    """
    def __init__(self):
        super().__init__(
            agent_name="RoadmapAgent",
            description="Connects Student Profile, Career Goals, Education, Skills, Opportunities, and Action Plan."
        )

    def process_task(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        student_id = task_input.get("student_id")
        if not student_id:
            raise ValueError("RoadmapAgent requires a valid student_id.")

        selected_pathway = task_input.get("selected_pathway") or task_input.get("pathway")
        target_role = task_input.get("target_role") or task_input.get("role")
        current_skills = task_input.get("current_skills") or task_input.get("skills")
        target_skills = task_input.get("target_skills") or task_input.get("required_skills")
        opportunity_id = task_input.get("opportunity_id")

        pathway_dict = selected_pathway if isinstance(selected_pathway, dict) else None
        elig_obj = task_input.get("eligibility") or task_input.get("eligibility_result")
        skill_gap_obj = task_input.get("skill_gap") or task_input.get("skill_gap_result")

        roadmap = RoadmapService.build_roadmap(
            student_id=student_id,
            target_role=target_role,
            current_skills=current_skills,
            target_skills=target_skills,
            opportunity_id=opportunity_id,
            pathway_data=pathway_dict,
            eligibility_result=elig_obj if isinstance(elig_obj, dict) else None,
            skill_gap_result=skill_gap_obj if isinstance(skill_gap_obj, dict) else None,
        )

        stage_count = len(roadmap.get("stages", []))
        progress = roadmap.get("roadmap_progress_percentage", 0.0)
        next_action_obj = roadmap.get("next_recommended_action")
        next_action_title = next_action_obj.get("title") if isinstance(next_action_obj, dict) else (str(next_action_obj) if next_action_obj else "Continue milestones")

        explanation = (
            f"Synthesized {stage_count}-stage roadmap for {roadmap['student_name']} targeting {roadmap['career_goal']}. "
            f"Overall roadmap progress is {progress}%."
        )

        return {
            "status": "success",
            "agent": self.agent_name,
            "action": "generate_roadmap",
            "plan_id": roadmap.get("active_plan_id"),
            "stage_count": stage_count,
            "progress": progress,
            "next_action": next_action_title,
            "data": roadmap,
            "explanation": explanation
        }


class OpportunityPathwayAgent(BaseAgent):
    """
    Specialized Domain Agent for discovering career and education pathways.
    """
    def __init__(self):
        super().__init__(
            agent_name="OpportunityPathwayAgent",
            description="Synthesizes relevant career and education pathways based on declared targets or student exploration profiles."
        )

    def process_task(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        result = PathwayDiscoveryService.discover_pathways(task_input)
        count = result.get("total_pathways", 0)
        mode = result.get("career_direction", "exploring")
        if mode == "known":
            explanation = f"Assembled pathway roadmap and verified criteria for target role: '{result.get('target_role')}'."
        else:
            explanation = f"Identified {count} explainable career pathways for exploration matching your profile evidence."

        return {
            "status": "success",
            "agent": self.agent_name,
            "data": result,
            "explanation": explanation
        }


class PathwayAnalysisAgent(BaseAgent):
    """
    Specialized Domain Agent for evaluating combined Eligibility and Skill Gap
    readiness against a student's selected career pathway.
    """
    def __init__(self):
        super().__init__(
            agent_name="PathwayAnalysisAgent",
            description="Evaluates eligibility status and analyzes skill gaps for the student's selected career pathway."
        )

    def process_task(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        result = PathwayAnalysisService.analyze_pathway_fit(task_input)
        if result.get("status") == "clarification_needed":
            explanation = result.get("message", "Please select a career pathway before running eligibility and skill analysis.")
        elif result.get("status") == "conflict_detected":
            explanation = result.get("error", "Conflict detected between target role and selected pathway.")
        else:
            p_name = result.get("selected_pathway", {}).get("name", "Selected Pathway")
            elig_status = result.get("eligibility", {}).get("status", "NEEDS_VERIFICATION")
            match_rate = result.get("skill_gap", {}).get("match_rate", 0)
            explanation = f"Evaluated pathway fit for '{p_name}'. Eligibility Status: {elig_status}. Skill Match Rate: {match_rate}%."

        return {
            "status": result.get("status", "success"),
            "agent": self.agent_name,
            "data": result,
            "explanation": explanation
        }


