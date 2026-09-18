"""
Education Pathway Guidance Service (Member 2 - Step 6).
Provides explainable, data-driven educational pathway recommendations by evaluating
student academic standing, qualifications, skills, interests, and target careers against
the Education Pathway Catalogue and Career Catalogue.

Guiding Principles:
1. Deterministic and factual (No LLMs / Gemini dependencies).
2. Transparent reasoning connecting Current Education -> Next Steps -> Specializations -> Career Connections.
3. Strict neutrality (No fake percentage matches, no guarantees of admission, licensing, or employment).
4. Robust handling of incomplete/empty profiles with actionable information gaps.
5. Reusable across general profile guidance and career-targeted queries (?career_id=...).
"""

from typing import Tuple, Dict, Any, List, Optional
from profile.services import ProfileService
from profile.models import StudentProfile
from profile.interest_intelligence import InterestIntelligenceService
from career.catalogue import CATALOGUE_BY_ID, CAREER_CATALOGUE
from .catalogue import EDUCATION_PATHWAY_CATALOGUE, PATHWAY_BY_ID, PATHWAYS_BY_LEVEL


class EducationService:
    """
    Service layer for Education Pathway Guidance and Catalogue queries.
    """

    @staticmethod
    def get_courses_by_degree(degree_level: str) -> List[Dict[str, Any]]:
        """
        Foundation hook retained for backward compatibility with initial stubs.
        """
        if not degree_level:
            return []
        normalized = degree_level.strip().lower()
        return [
            p for p in EDUCATION_PATHWAY_CATALOGUE
            if p["current_education_level"].lower() == normalized or normalized in p["possible_next_step"].lower()
        ]

    @staticmethod
    def get_education_catalogue(
        education_level: Optional[str] = None,
        domain: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves the education pathway catalogue, optionally filtered by
        education level and/or career domain.
        """
        results = list(EDUCATION_PATHWAY_CATALOGUE)
        if education_level:
            lvl_clean = education_level.strip().lower()
            results = [
                p for p in results
                if p["current_education_level"].lower() == lvl_clean or lvl_clean in p["possible_next_step"].lower()
            ]
        if domain:
            dom_clean = domain.strip().lower()
            results = [
                p for p in results
                if any(dom_clean == d.lower() for d in p.get("relevant_domains", []))
            ]
        return results

    @staticmethod
    def get_pathway_by_id(pathway_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single education pathway by its unique ID.
        """
        if not pathway_id or not isinstance(pathway_id, str):
            return None
        return PATHWAY_BY_ID.get(pathway_id.strip().lower())

    @classmethod
    def get_pathways_for_profile(
        cls,
        profile_id: int,
        career_id: Optional[str] = None
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Generates structured, explainable education pathway guidance for a student profile.
        Optionally tailors pathways toward a specific target career ID.

        Returns: (guidance_dict, None) on success, or (None, error_message) on error.
        """
        profile = ProfileService.get_profile_by_id(profile_id)
        if not profile:
            return None, f"Student profile with ID {profile_id} not found."

        selected_career = None
        if career_id:
            career_id_clean = career_id.strip().lower()
            if career_id_clean not in CATALOGUE_BY_ID:
                return None, f"Career pathway with ID '{career_id}' not found in catalogue."
            selected_career = CATALOGUE_BY_ID[career_id_clean]

        guidance = cls.evaluate_profile_education(profile, selected_career=selected_career)
        return guidance, None

    @classmethod
    def evaluate_profile_education(
        cls,
        profile: StudentProfile,
        selected_career: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Core educational pathway evaluation engine:
        1. Analyzes current educational credentials (qualification, degrees, diploma, PG).
        2. Evaluates student interests and domains via InterestIntelligenceService.
        3. Identifies information gaps for unrecorded or partial fields.
        4. Matches catalogue pathways based on level, target career, domain, and skills.
        5. Formulates factual, non-hype explanations for each recommended educational route.
        """
        student_level = (profile.education_level or "").strip()
        qualification = (profile.qualification or "").strip()
        degree_details = profile.get_degree_details() or {}
        diploma_details = profile.get_diploma_details() or {}
        pg_details = profile.get_pg_details() or {}
        skills = profile.get_skills() or []
        interests = profile.get_interests() or []
        career_goals = (profile.career_goals or "").strip()

        # Step A: Run Interest Intelligence Engine
        intel = InterestIntelligenceService.analyze_interests(interests)
        detected_domains = intel.get("domain_summary", [])
        unmapped_interests = intel.get("unmapped_interests", [])
        canonical_interests = [item["name"] for item in intel.get("interests", []) if item.get("is_mapped")]

        # Step B: Identify Factual Information Gaps
        information_gaps: List[str] = []
        if not student_level:
            information_gaps.append(
                "Education level has not been recorded on your profile; recommendations are presented on an exploratory basis."
            )
        if not qualification:
            information_gaps.append(
                "Detailed qualification information is incomplete; specific academic prerequisites could not be verified."
            )
        if not skills:
            information_gaps.append(
                "No technical or practical skills have been listed; foundational preparation for advanced coursework cannot be fully assessed."
            )
        if not interests:
            information_gaps.append(
                "No academic or career interests have been recorded; general pathways across multiple sectors are provided."
            )
        elif unmapped_interests:
            unmapped_str = ", ".join(unmapped_interests)
            information_gaps.append(
                f"Some entered interests could not be mapped to standard domains: {unmapped_str}."
            )
        if not career_goals and not selected_career:
            information_gaps.append(
                "No target career goal was specified; pathways explore diverse opportunities across your academic standing."
            )

        # Step C: Evaluate & Score Pathways
        skills_lookup = [s.strip().lower() for s in skills if s and s.strip()]
        interests_lookup = [i.strip().lower() for i in canonical_interests]
        goal_text_lower = career_goals.lower()

        evaluated_pathways = []
        for pathway in EDUCATION_PATHWAY_CATALOGUE:
            pathway_level = pathway["current_education_level"].strip().lower()
            pathway_domains = [d.lower() for d in pathway.get("relevant_domains", [])]
            pathway_interests = [i.lower() for i in pathway.get("relevant_interests", [])]
            useful_skills = pathway.get("useful_skills", [])
            related_careers = pathway.get("related_career_ids", [])

            # --- 1. Level Alignment ---
            level_rank = 0
            if student_level:
                st_lvl_lower = student_level.lower()
                if pathway_level in st_lvl_lower or st_lvl_lower in pathway_level:
                    level_rank = 3
                elif "diploma" in st_lvl_lower and pathway_level == "diploma":
                    level_rank = 3
                elif any(term in st_lvl_lower for term in ["undergrad", "bachelor", "b.tech", "b.sc", "b.com", "degree"]) and pathway_level == "undergraduate":
                    level_rank = 3
                elif any(term in st_lvl_lower for term in ["postgrad", "master", "m.tech", "m.sc", "mba"]) and pathway_level == "postgraduate":
                    level_rank = 3
                elif any(term in st_lvl_lower for term in ["secondary", "12th", "inter", "high"]) and pathway_level == "higher secondary":
                    level_rank = 3
                else:
                    level_rank = 0
            else:
                # If no level recorded, consider all as exploratory
                level_rank = 1

            # --- 2. Career Target Alignment ---
            career_rank = 0
            if selected_career:
                if selected_career["id"] in related_careers:
                    career_rank = 4
                elif selected_career["domain"].lower() in pathway_domains:
                    career_rank = 2
            elif career_goals:
                for rc_id in related_careers:
                    if rc_id in CATALOGUE_BY_ID:
                        c_name = CATALOGUE_BY_ID[rc_id]["name"].lower()
                        if any(w in goal_text_lower for w in c_name.replace("/", " ").split() if len(w) > 3):
                            career_rank = 2
                            break

            # --- 3. Domain & Interest Alignment ---
            interest_rank = 0
            matched_interests = []
            for pi in pathway.get("relevant_interests", []):
                pi_lower = pi.lower()
                for user_int in interests_lookup:
                    if user_int in pi_lower or pi_lower in user_int:
                        if pi not in matched_interests:
                            matched_interests.append(pi)

            domain_matched = any(d.lower() in [dom.lower() for dom in detected_domains] for d in pathway.get("relevant_domains", []))
            if matched_interests and domain_matched:
                interest_rank = 3
            elif domain_matched or matched_interests:
                interest_rank = 2

            # --- 4. Skill Alignment ---
            matched_skills = []
            for us in useful_skills:
                us_lower = us.lower()
                for user_sk in skills_lookup:
                    if user_sk in us_lower or us_lower in user_sk:
                        if us not in matched_skills:
                            matched_skills.append(us)
            skill_rank = 2 if len(matched_skills) >= 2 else (1 if len(matched_skills) == 1 else 0)

            # Combined Priority Score for Deterministic Ordering
            total_score = (level_rank * 3) + (career_rank * 3) + (interest_rank * 2) + skill_rank

            # Build Factual Explanations
            why_identified = cls._build_pathway_explanations(
                pathway=pathway,
                student_level=student_level,
                qualification=qualification,
                selected_career=selected_career,
                career_goals=career_goals,
                matched_interests=matched_interests,
                domain_matched=domain_matched,
                matched_skills=matched_skills
            )

            # Format Connected Career Objects
            connected_careers = []
            for cid in related_careers:
                if cid in CATALOGUE_BY_ID:
                    c_obj = CATALOGUE_BY_ID[cid]
                    connected_careers.append({
                        "id": c_obj["id"],
                        "name": c_obj["name"],
                        "domain": c_obj["domain"]
                    })

            evaluated_pathways.append({
                "id": pathway["id"],
                "title": pathway["title"],
                "current_education_level": pathway["current_education_level"],
                "possible_next_step": pathway["possible_next_step"],
                "higher_study_options": pathway.get("higher_study_options", []),
                "specialization_options": pathway.get("specialization_options", []),
                "relevant_domains": pathway.get("relevant_domains", []),
                "relevant_interests": pathway.get("relevant_interests", []),
                "useful_skills": pathway.get("useful_skills", []),
                "matched_interests": matched_interests,
                "matched_skills": matched_skills,
                "why_identified": why_identified,
                "career_connections": connected_careers,
                "admission_prerequisites": pathway.get("admission_prerequisites", "See institutional guidelines."),
                "limitations": pathway.get("limitations", []),
                "_score": total_score
            })

        # Step D: Sort Pathways Deterministically
        # Sort descending by score, then alphabetically by title
        evaluated_pathways.sort(key=lambda x: (-x["_score"], x["title"]))

        # Remove internal score from public output
        for p in evaluated_pathways:
            p.pop("_score", None)

        # Filter: If career_id was provided, return pathways connecting to that career or domain
        if selected_career:
            targeted = [
                p for p in evaluated_pathways
                if selected_career["id"] in [c["id"] for c in p["career_connections"]] or
                   selected_career["domain"] in p["relevant_domains"]
            ]
            final_pathways = targeted if targeted else evaluated_pathways[:6]
        elif student_level:
            # Prioritize pathways matching the student's current level
            level_matched = [
                p for p in evaluated_pathways
                if p["current_education_level"].lower() in student_level.lower() or student_level.lower() in p["current_education_level"].lower()
            ]
            final_pathways = level_matched if level_matched else evaluated_pathways[:6]
        else:
            final_pathways = evaluated_pathways[:6]

        # Aggregate unique career connections from selected pathways
        all_career_connections = []
        seen_careers = set()
        for p in final_pathways:
            for c in p["career_connections"]:
                if c["id"] not in seen_careers:
                    seen_careers.add(c["id"])
                    all_career_connections.append(c)

        # Build Standardized Guidance Limitations / Disclaimers
        standard_limitations = [
            "This guidance outlines possible educational progression pathways based on recorded profile information.",
            "Actual admission, prerequisites, and degree eligibility depend on institutional criteria, accrediting bodies, and regulatory jurisdictions.",
            "This is an informational guidance assessment and does not constitute a guarantee of admission, licensing, or employment."
        ]

        return {
            "success": True,
            "profile_id": profile.id,
            "student_name": profile.full_name,
            "selected_career": {
                "id": selected_career["id"],
                "name": selected_career["name"],
                "domain": selected_career["domain"],
                "typical_education": selected_career.get("typical_education", [])
            } if selected_career else None,
            "current_education": {
                "education_level": student_level or "Not specified",
                "qualification": qualification or "Not specified",
                "degree_details": degree_details,
                "diploma_details": diploma_details,
                "pg_details": pg_details
            },
            "pathways_count": len(final_pathways),
            "pathways": final_pathways,
            "career_connections": all_career_connections,
            "information_gaps": information_gaps,
            "limitations": standard_limitations
        }

    @staticmethod
    def _build_pathway_explanations(
        pathway: Dict[str, Any],
        student_level: str,
        qualification: str,
        selected_career: Optional[Dict[str, Any]],
        career_goals: str,
        matched_interests: List[str],
        domain_matched: bool,
        matched_skills: List[str]
    ) -> List[str]:
        """
        Builds transparent, factual, qualified explanations.
        Avoids unsupported precision, hype, or certainty language.
        """
        explanations = []

        # 1. Current Education Connection
        if student_level or qualification:
            edu_summary = f"{qualification} ({student_level})".strip() if qualification and student_level else (qualification or student_level)
            if pathway["current_education_level"].lower() in student_level.lower() or student_level.lower() in pathway["current_education_level"].lower():
                explanations.append(
                    f"Educational standing connection: Your recorded standing ({edu_summary}) serves as the typical prerequisite baseline for entry into {pathway['possible_next_step']}."
                )
            else:
                explanations.append(
                    f"Educational progression note: This pathway typically begins from {pathway['current_education_level']}; your current recorded standing is {edu_summary}."
                )
        else:
            explanations.append(
                f"Educational consideration: Assessed as a potential progression route from {pathway['current_education_level']}; profile education level is currently unrecorded."
            )

        # 2. Target Career Connection (if selected)
        if selected_career:
            if selected_career["id"] in pathway.get("related_career_ids", []):
                explanations.append(
                    f"Career target alignment: Directly supports the educational and qualification prerequisites commonly required for {selected_career['name']}."
                )
            elif selected_career["domain"] in pathway.get("relevant_domains", []):
                explanations.append(
                    f"Sector alignment: Provides structured academic preparation relevant to the broader {selected_career['domain']} sector."
                )

        # 3. Interest & Domain Connection
        if matched_interests:
            explanations.append(
                f"Interest alignment: Relates to your recorded interest(s) in {', '.join(matched_interests)}."
            )
        elif domain_matched:
            explanations.append(
                f"Domain connection: Aligns with identified career domains ({', '.join(pathway.get('relevant_domains', []))})."
            )

        # 4. Skill Connection
        if matched_skills:
            explanations.append(
                f"Skill foundation: Foundational skills you have recorded ({', '.join(matched_skills)}) support readiness for this coursework."
            )

        # 5. Career Goal Connection (if applicable and no selected career)
        if not selected_career and career_goals:
            for rc_id in pathway.get("related_career_ids", []):
                if rc_id in CATALOGUE_BY_ID:
                    c_name = CATALOGUE_BY_ID[rc_id]["name"]
                    if c_name.lower() in career_goals.lower() or career_goals.lower() in c_name.lower():
                        explanations.append(
                            f"Career goal connection: Supports your stated goal ('{career_goals}') through aligned professional specialization."
                        )
                        break

        # 6. Factual Progression Summary
        explanations.append(
            f"Progression pathway: {pathway['explanation']}"
        )

        return explanations
