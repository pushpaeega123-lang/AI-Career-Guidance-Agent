import re
from typing import Any, Dict, List, Optional
from .base_agent import BaseAgent
from .specialized_agents import (
    EligibilityAgent,
    OpportunityPathwayAgent,
    PathwayAnalysisAgent,
    PlannerAgent,
    RoadmapAgent,
    SkillGapAgent,
)


class AgentOrchestrator:
    """
    Central Multi-Agent Orchestrator.
    Performs deterministic task identification, context extraction, and workflow execution
    across specialized domain agents.
    """

    def __init__(self):
        self.registered_agents: Dict[str, BaseAgent] = {}
        self._register_default_agents()

    def _register_default_agents(self):
        """Initialize and register standard specialized domain agents."""
        self.register_agent("eligibility", EligibilityAgent())
        self.register_agent("skill_gap", SkillGapAgent())
        self.register_agent("planner", PlannerAgent())
        self.register_agent("roadmap", RoadmapAgent())
        self.register_agent("opportunity_pathway", OpportunityPathwayAgent())
        self.register_agent("pathway_analysis", PathwayAnalysisAgent())

    def register_agent(self, agent_key: str, agent_instance: BaseAgent):
        """Register a specialized domain agent."""
        self.registered_agents[agent_key] = agent_instance

    def get_agent(self, agent_key: str) -> Optional[BaseAgent]:
        """Retrieve a registered agent instance."""
        return self.registered_agents.get(agent_key)

    def detect_intent(self, user_query: Optional[str], context: Optional[Dict[str, Any]] = None) -> str:
        """
        Deterministically identify the requested task intent from explicit context or natural language query.
        Returns one of: 'pathway_discovery', 'eligibility', 'skill_gap', 'planner', 'roadmap', 'comprehensive_guidance', or 'clarification'.
        """
        ctx = context or {}

        # 1. Check for explicit intent in context
        explicit_intent = ctx.get("intent") or ctx.get("task") or ctx.get("action")
        if explicit_intent:
            norm_intent = str(explicit_intent).strip().lower()
            if norm_intent in ("pathway_fit", "pathway_analysis", "fit_analysis", "analyze_pathway", "selected_pathway_analysis", "pathway_evaluation"):
                return "pathway_fit"
            if norm_intent in ("pathway_discovery", "pathway", "pathways", "discover_pathways", "discover", "explore_pathways", "explore_careers"):
                return "pathway_discovery"
            if norm_intent in ("eligibility", "eligible", "check_eligibility"):
                return "eligibility"
            if norm_intent in ("skill_gap", "skillgap", "skills", "analyze_skills"):
                return "skill_gap"
            if norm_intent in ("planner", "plan", "action_plan", "create_plan"):
                return "planner"
            if norm_intent in ("roadmap", "career_roadmap", "journey"):
                return "roadmap"
            if norm_intent in ("comprehensive_guidance", "comprehensive", "full_guidance", "multi_agent", "career_guidance", "pathway_to_roadmap"):
                return "comprehensive_guidance"

        # 2. Check context structure signatures
        if "student_profile" in ctx and ("opportunity" in ctx or "requirements" in ctx):
            return "eligibility"
        if "current_skills" in ctx and "target_skills" in ctx and "target_role" not in ctx:
            return "skill_gap"

        # 3. Analyze query text with deterministic regex / keyword matching
        if not user_query or not str(user_query).strip():
            return "clarification"

        q = str(user_query).lower()

        # Pathway fit / Selected pathway analysis patterns (check before general discovery)
        if any(p in q for p in [
            "analyze my selected pathway", "analyze selected pathway", "analyze my selected",
            "analyze selected", "selected pathway", "pathway fit", "fit analysis",
            "analyze my", "evaluate selected", "evaluate pathway fit", "check selected pathway",
            "check my pathway", "analyze pathway"
        ]):
            return "pathway_fit"

        # Multi-agent / comprehensive guidance patterns
        if any(p in q for p in [
            "how do i become", "how to become", "career guidance", "comprehensive",
            "guide me", "transition to", "complete roadmap", "full path", "career transition",
            "pathway to roadmap"
        ]):
            return "comprehensive_guidance"

        # Pathway discovery patterns
        if any(p in q for p in [
            "pathways for me", "what careers can i explore", "i don't know what career to choose",
            "i don't know what career", "what careers can i", "discover pathways",
            "pathway discovery", "career pathways", "pathways to explore", "explore pathways",
            "career options", "what pathways", "recommend pathways", "explore careers",
            "pathway", "pathways"
        ]):
            return "pathway_discovery"

        # Eligibility patterns
        if any(p in q for p in [
            "am i eligible", "check eligibility", "check my eligibility", "eligible",
            "eligibility", "qualify", "requirements", "prerequisite", "prerequisites",
            "meet criteria"
        ]):
            return "eligibility"

        # Skill gap patterns
        if any(p in q for p in [
            "what skills am i missing", "analyze my skill gap", "analyze skill gap",
            "skill gap", "skills gap", "missing skills", "skills matrix", "what skills",
            "compare skills", "match rate", "skills required", "gap analysis"
        ]):
            return "skill_gap"

        # Planner patterns
        if any(p in q for p in [
            "create my action plan", "create action plan", "what should i do next",
            "action plan", "generate action plan", "make action plan", "milestones",
            "timeline", "study plan", "action roadmap", "next steps", "learning plan",
            "milestone"
        ]):
            return "planner"

        # Roadmap patterns
        if any(p in q for p in [
            "show my roadmap", "show my career journey", "show career journey",
            "show career roadmap", "show roadmap", "view roadmap", "my roadmap",
            "roadmap", "journey", "career path", "end to end", "overview"
        ]):
            return "roadmap"

        # Default to clarification if query is ambiguous
        return "clarification"

    def route_request(self, user_query: Optional[str] = "", context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Orchestrates request routing to the appropriate specialized agent or multi-agent workflow.
        """
        ctx = context or {}
        intent = self.detect_intent(user_query, ctx)

        # Handle Ambiguous / Clarification requests
        if intent == "clarification":
            return {
                "intent": "clarification",
                "agent_used": None,
                "agents_executed": [],
                "status": "clarification_needed",
                "result": None,
                "explanation": (
                    "Please specify the guidance you need. I can help with: "
                    "1) Discovering career and education pathways, "
                    "2) Eligibility verification for specific opportunities, "
                    "3) Skill gap analysis against target careers, "
                    "4) Personalized milestone action planning, or "
                    "5) End-to-end career roadmap synthesis."
                ),
                "recommended_next_action": "Select a task: Pathway Discovery, Eligibility, Skill Gap, Action Planner, or Full Career Guidance.",
                "errors": []
            }

        # Handle Pathway Fit / Selected Pathway Analysis
        if intent == "pathway_fit":
            agent = self.registered_agents["pathway_analysis"]
            try:
                task_ctx = dict(ctx)
                if not task_ctx.get("target_role"):
                    m = re.search(r"analyze\s+(?:my\s+)?([a-zA-Z\s]+?)\s+pathway", user_query or "", re.IGNORECASE)
                    if m:
                        role_cand = m.group(1).strip()
                        if role_cand.lower() not in ("selected", "target", "chosen", "current"):
                            task_ctx["target_role"] = role_cand
                            task_ctx["career_direction"] = task_ctx.get("career_direction") or "known"

                res = agent.process_task(task_ctx)
                agent_status = res.get("status")
                data = res.get("data", {})

                if agent_status == "clarification_needed":
                    return {
                        "intent": "pathway_fit",
                        "agent_used": agent.agent_name,
                        "agents_executed": [agent.agent_name],
                        "status": "clarification_needed",
                        "result": data,
                        "explanation": res["explanation"],
                        "recommended_next_action": "Please select a career pathway from Pathway Discovery before running analysis.",
                        "errors": []
                    }
                elif agent_status == "conflict_detected":
                    return {
                        "intent": "pathway_fit",
                        "agent_used": agent.agent_name,
                        "agents_executed": [agent.agent_name],
                        "status": "error",
                        "result": data,
                        "explanation": res["explanation"],
                        "recommended_next_action": "Align your target role and selected pathway or re-run Pathway Discovery.",
                        "errors": [data.get("error", "Target role and selected pathway conflict.")]
                    }
                else:
                    return {
                        "intent": "pathway_fit",
                        "agent_used": agent.agent_name,
                        "agents_executed": [agent.agent_name],
                        "status": "success",
                        "result": data,
                        "explanation": res["explanation"],
                        "recommended_next_action": "Continue to Personalized Action Plan.",
                        "errors": []
                    }
            except Exception as e:
                return {
                    "intent": "pathway_fit",
                    "agent_used": agent.agent_name,
                    "agents_executed": [agent.agent_name],
                    "status": "error",
                    "result": None,
                    "explanation": f"PathwayAnalysisAgent encountered an error: {str(e)}",
                    "recommended_next_action": "Ensure valid pathway selection and profile state.",
                    "errors": [str(e)]
                }

        # Handle Single Domain Agent Intents
        if intent == "pathway_discovery":
            agent = self.registered_agents["opportunity_pathway"]
            try:
                res = agent.process_task(ctx)
                return {
                    "intent": "pathway_discovery",
                    "agent_used": agent.agent_name,
                    "agents_executed": [agent.agent_name],
                    "status": "success",
                    "result": res["data"],
                    "explanation": res["explanation"],
                    "recommended_next_action": "Select or shortlist a pathway to evaluate specific eligibility prerequisites.",
                    "errors": []
                }
            except Exception as e:
                return {
                    "intent": "pathway_discovery",
                    "agent_used": agent.agent_name,
                    "agents_executed": [agent.agent_name],
                    "status": "error",
                    "result": None,
                    "explanation": f"OpportunityPathwayAgent encountered an error: {str(e)}",
                    "recommended_next_action": "Check career direction and student profile parameters.",
                    "errors": [str(e)]
                }

        if intent == "eligibility":
            agent = self.registered_agents["eligibility"]
            try:
                res = agent.process_task(ctx)
                return {
                    "intent": "eligibility",
                    "agent_used": agent.agent_name,
                    "agents_executed": [agent.agent_name],
                    "status": "success",
                    "result": res["data"],
                    "explanation": res["explanation"],
                    "recommended_next_action": "Review missing or unverified criteria to satisfy opportunity prerequisites.",
                    "errors": []
                }
            except Exception as e:
                return {
                    "intent": "eligibility",
                    "agent_used": agent.agent_name,
                    "agents_executed": [agent.agent_name],
                    "status": "error",
                    "result": None,
                    "explanation": f"EligibilityAgent encountered an error: {str(e)}",
                    "recommended_next_action": "Check student profile and opportunity requirement parameters.",
                    "errors": [str(e)]
                }

        if intent == "skill_gap":
            agent = self.registered_agents["skill_gap"]
            try:
                res = agent.process_task(ctx)
                return {
                    "intent": "skill_gap",
                    "agent_used": agent.agent_name,
                    "agents_executed": [agent.agent_name],
                    "status": "success",
                    "result": res["data"],
                    "explanation": res["explanation"],
                    "recommended_next_action": "Focus on critical priority missing skills before applying to target roles.",
                    "errors": []
                }
            except Exception as e:
                return {
                    "intent": "skill_gap",
                    "agent_used": agent.agent_name,
                    "agents_executed": [agent.agent_name],
                    "status": "error",
                    "result": None,
                    "explanation": f"SkillGapAgent encountered an error: {str(e)}",
                    "recommended_next_action": "Provide current and target skill lists for comparison.",
                    "errors": [str(e)]
                }

        if intent == "planner":
            agent = self.registered_agents["planner"]
            try:
                task_ctx = dict(ctx)
                if not task_ctx.get("target_role") and not task_ctx.get("selected_pathway"):
                    m = re.search(r"(?:for|as|to become a?)\s+([a-zA-Z\s]+)", user_query or "", re.IGNORECASE)
                    if m:
                        role_cand = m.group(1).strip()
                        if role_cand.lower() not in ("action plan", "milestone", "roadmap"):
                            task_ctx["target_role"] = role_cand
                res = agent.process_task(task_ctx)
                next_action_str = res.get("next_action") or (res.get("data", {}).get("next_recommended_action", {}).get("title") if isinstance(res.get("data", {}).get("next_recommended_action"), dict) else "Start Phase 1")
                return {
                    "intent": "planner",
                    "agent_used": agent.agent_name,
                    "agents_executed": [agent.agent_name],
                    "status": "success",
                    "result": res["data"],
                    "explanation": res["explanation"],
                    "recommended_next_action": f"Begin immediate milestone: {next_action_str}.",
                    "errors": []
                }
            except Exception as e:
                return {
                    "intent": "planner",
                    "agent_used": agent.agent_name,
                    "agents_executed": [agent.agent_name],
                    "status": "error",
                    "result": None,
                    "explanation": f"PlannerAgent encountered an error: {str(e)}",
                    "recommended_next_action": "Specify target_role and valid student parameters.",
                    "errors": [str(e)]
                }

        if intent == "roadmap":
            agent = self.registered_agents["roadmap"]
            try:
                task_ctx = dict(ctx)
                if not task_ctx.get("student_id"):
                    task_ctx["student_id"] = 1
                res = agent.process_task(task_ctx)
                return {
                    "intent": "roadmap",
                    "agent_used": agent.agent_name,
                    "agents_executed": [agent.agent_name],
                    "status": "success",
                    "result": res["data"],
                    "explanation": res["explanation"],
                    "recommended_next_action": "Execute sequential milestones in the active action plan stage.",
                    "errors": []
                }
            except Exception as e:
                return {
                    "intent": "roadmap",
                    "agent_used": agent.agent_name,
                    "agents_executed": [agent.agent_name],
                    "status": "error",
                    "result": None,
                    "explanation": f"RoadmapAgent encountered an error: {str(e)}",
                    "recommended_next_action": "Ensure a valid student_id is provided.",
                    "errors": [str(e)]
                }

        # Multi-Agent Coordinated Flow: Comprehensive Career Guidance
        if intent == "comprehensive_guidance":
            return self._execute_multi_agent_workflow(user_query, ctx)

        return {
            "intent": "unknown",
            "agent_used": None,
            "agents_executed": [],
            "status": "error",
            "result": None,
            "explanation": "Unable to route request to any domain agent.",
            "recommended_next_action": "Please clarify your career guidance objective.",
            "errors": ["Unknown intent detected."]
        }

    def _execute_multi_agent_workflow(self, user_query: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute coordinated multi-agent workflow:
        PathwayAnalysisAgent (if pathway present) → SkillGapAgent → EligibilityAgent → PlannerAgent → RoadmapAgent (if student_id present).
        """
        activated_agents = []
        errors = []
        combined_result: Dict[str, Any] = {}

        curr_skills = ctx.get("current_skills") or ctx.get("skills") or []
        selected_pathway = ctx.get("selected_pathway") or ctx.get("pathway")
        target_role = (
            ctx.get("target_role")
            or ctx.get("role")
            or (selected_pathway.get("name") if isinstance(selected_pathway, dict) else None)
            or "Software Engineer"
        )
        target_skills = ctx.get("target_skills") or ctx.get("required_skills") or [
            target_role.split()[0], "Git", "Problem Solving", "Databases"
        ]

        # 1. Pathway Analysis (if pathway provided)
        if selected_pathway:
            try:
                pathway_agent = self.registered_agents.get("pathway_analysis")
                if pathway_agent:
                    pathway_res = pathway_agent.process_task(ctx)
                    combined_result["pathway_analysis"] = pathway_res.get("data", {})
                    activated_agents.append(pathway_agent.agent_name)
                    if pathway_res.get("data", {}).get("eligibility"):
                        combined_result["eligibility"] = pathway_res["data"]["eligibility"]
                    if pathway_res.get("data", {}).get("skill_gap"):
                        combined_result["skill_gap"] = pathway_res["data"]["skill_gap"]
            except Exception as e:
                errors.append(f"PathwayAnalysisAgent error: {str(e)}")

        # 2. Skill Gap Analysis (if not already produced by PathwayAnalysisAgent)
        if "skill_gap" not in combined_result:
            try:
                skill_agent = self.registered_agents["skill_gap"]
                skill_res = skill_agent.process_task({
                    "current_skills": curr_skills,
                    "target_skills": target_skills
                })
                combined_result["skill_gap"] = skill_res["data"]
                activated_agents.append(skill_agent.agent_name)
            except Exception as e:
                errors.append(f"SkillGapAgent error: {str(e)}")
        elif "SkillGapAgent" not in activated_agents:
            activated_agents.append("SkillGapAgent")

        # 3. Eligibility Evaluation (if not already produced and context exists)
        if "eligibility" not in combined_result and ("opportunity" in ctx or "student_profile" in ctx or selected_pathway):
            try:
                elig_agent = self.registered_agents["eligibility"]
                elig_res = elig_agent.process_task(ctx)
                combined_result["eligibility"] = elig_res["data"]
                activated_agents.append(elig_agent.agent_name)
            except Exception as e:
                errors.append(f"EligibilityAgent error: {str(e)}")
        elif "eligibility" in combined_result and "EligibilityAgent" not in activated_agents:
            activated_agents.append("EligibilityAgent")

        # 4. Action Plan Generation
        missing_skills_list = []
        learning_areas_list = []
        if "skill_gap" in combined_result:
            missing_skills_list = combined_result["skill_gap"].get("missing_skills", [])
            learning_areas_list = combined_result["skill_gap"].get("learning_areas", [])

        elig_status = None
        if "eligibility" in combined_result:
            elig_status = combined_result["eligibility"].get("status")

        try:
            planner_agent = self.registered_agents["planner"]
            planner_res = planner_agent.process_task({
                "student_id": ctx.get("student_id"),
                "target_role": target_role,
                "selected_pathway": selected_pathway,
                "current_skills": curr_skills,
                "skill_gaps": missing_skills_list,
                "learning_areas": learning_areas_list,
                "eligibility_status": elig_status,
                "eligibility": combined_result.get("eligibility"),
                "timeline_months": ctx.get("timeline_months", 6)
            })
            combined_result["action_plan"] = planner_res["data"]
            activated_agents.append(planner_agent.agent_name)
        except Exception as e:
            errors.append(f"PlannerAgent error: {str(e)}")

        # 5. Roadmap Synthesis (if student_id present)
        student_id = ctx.get("student_id")
        if student_id:
            try:
                roadmap_agent = self.registered_agents["roadmap"]
                roadmap_res = roadmap_agent.process_task({
                    "student_id": student_id,
                    "target_role": target_role,
                    "selected_pathway": selected_pathway,
                    "current_skills": curr_skills,
                    "target_skills": target_skills,
                    "opportunity_id": ctx.get("opportunity_id"),
                    "eligibility": combined_result.get("eligibility"),
                    "skill_gap": combined_result.get("skill_gap"),
                })
                combined_result["roadmap"] = roadmap_res["data"]
                activated_agents.append(roadmap_agent.agent_name)
            except Exception as e:
                errors.append(f"RoadmapAgent error: {str(e)}")

        # Next recommended step
        next_action_str = "Enroll in foundational skills coursework and set up your portfolio."
        if "action_plan" in combined_result and combined_result["action_plan"].get("next_recommended_action"):
            next_action_obj = combined_result["action_plan"]["next_recommended_action"]
            next_action_str = next_action_obj.get("title", next_action_str) if isinstance(next_action_obj, dict) else str(next_action_obj)

        agents_str = ", ".join(activated_agents)
        explanation = (
            f"Multi-agent orchestration coordinated [{agents_str}] to analyze skill requirements for '{target_role}', "
            f"formulate prioritized milestones, and synthesize career progression readiness."
        )

        pathway_repr = (
            selected_pathway.get("name")
            if isinstance(selected_pathway, dict)
            else (str(selected_pathway) if selected_pathway else target_role)
        )

        plan_id = None
        if "action_plan" in combined_result and isinstance(combined_result["action_plan"], dict):
            plan_id = combined_result["action_plan"].get("id")

        skill_summary = {}
        if "skill_gap" in combined_result and isinstance(combined_result["skill_gap"], dict):
            sg_data = combined_result["skill_gap"]
            skill_summary = {
                "match_rate": sg_data.get("match_rate", 0),
                "gap_percentage": sg_data.get("gap_percentage", 0),
                "matching_skills_count": len(sg_data.get("matching_skills", [])),
                "missing_skills_count": len(sg_data.get("missing_skills", [])),
            }

        return {
            "status": "success" if not errors else ("partial_success" if activated_agents else "error"),
            "workflow": "pathway_to_roadmap" if ("PathwayAnalysisAgent" in activated_agents or "roadmap" in combined_result) else "comprehensive_guidance",
            "intent": "comprehensive_guidance",
            "selected_pathway": pathway_repr,
            "agents_executed": activated_agents,
            "agent_used": f"MultiAgentCoordination([{agents_str}])",
            "eligibility_status": elig_status,
            "skill_gap_summary": skill_summary,
            "plan_id": plan_id,
            "roadmap": combined_result.get("roadmap", {}),
            "next_action": next_action_str,
            "result": combined_result,
            "explanation": explanation,
            "recommended_next_action": f"Immediate Focus: {next_action_str}",
            "errors": errors
        }
