"""
Career Pathway Guidance Service (Member 2).
Provides explainable, data-driven career guidance by evaluating student profile
attributes (interests, skills, education, career goals) against the career catalogue
and Interest Intelligence engine.

Guiding Principles:
1. Deterministic and explainable (No LLMs / Gemini dependencies).
2. No unsupported precision (No fake % match scores, no certainty claims or guarantees).
3. Robust handling of incomplete/empty profiles with explicit guidance limitations.
4. Seamless integration with StudentProfile and InterestIntelligenceService.
"""

from typing import Tuple, Dict, Any, List, Optional
from profile.services import ProfileService
from profile.models import StudentProfile
from profile.interest_intelligence import InterestIntelligenceService
from .catalogue import CAREER_CATALOGUE, CATALOGUE_BY_ID, CATALOGUE_BY_DOMAIN


SKILL_ALIASES = {
    "pandas": ["python", "data wrangling", "statistical modeling", "data visualization"],
    "numpy": ["python", "linear algebra", "statistical modeling"],
    "scikit-learn": ["machine learning algorithms", "statistical modeling", "python"],
    "sklearn": ["machine learning algorithms", "statistical modeling", "python"],
    "matplotlib": ["data visualization", "python"],
    "seaborn": ["data visualization", "python"],
    "flask": ["programming", "rest apis", "python"],
    "django": ["programming", "rest apis", "python"],
    "fastapi": ["programming", "rest apis", "python"],
    "pytorch": ["deep learning frameworks (pytorch/tensorflow)", "python"],
    "tensorflow": ["deep learning frameworks (pytorch/tensorflow)", "python"],
    "react": ["react/vue/frontend frameworks", "html/css", "javascript/typescript"],
    "vue": ["react/vue/frontend frameworks", "html/css"],
    "javascript": ["javascript/typescript", "programming"],
    "typescript": ["javascript/typescript", "programming"],
    "sql": ["database management", "sql"],
}


class CareerService:
    """
    Service layer for Career Pathway Guidance and Catalogue lookups.
    """

    @staticmethod
    def get_career_catalogue(domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves the career catalogue, optionally filtered by domain.
        """
        if domain:
            normalized_domain = domain.strip().lower()
            return [
                c for c in CAREER_CATALOGUE
                if c["domain"].lower() == normalized_domain or normalized_domain in [rd.lower() for rd in c.get("related_domains", [])]
            ]
        return list(CAREER_CATALOGUE)

    @staticmethod
    def get_career_by_id(career_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single career entry by unique identifier.
        """
        if not career_id or not isinstance(career_id, str):
            return None
        return CATALOGUE_BY_ID.get(career_id.strip().lower())

    @staticmethod
    def get_pathways_by_sector(sector: str) -> List[Dict[str, Any]]:
        """
        Legacy/foundation alias for getting pathways by sector/domain.
        """
        return CareerService.get_career_catalogue(domain=sector)

    @staticmethod
    def generate_guidance_for_profile(profile_id: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Generates explainable career pathway guidance for a student profile ID.
        Returns: (guidance_dict, None) on success, or (None, error_message) on failure.
        """
        profile = ProfileService.get_profile_by_id(profile_id)
        if not profile:
            return None, f"Student profile with ID {profile_id} not found."

        guidance = CareerService.evaluate_profile_guidance(profile)
        return guidance, None

    @classmethod
    def evaluate_profile_guidance(cls, profile: StudentProfile) -> Dict[str, Any]:
        """
        Core evaluation engine:
        1. Analyzes profile interests via InterestIntelligenceService.
        2. Inspects skills, education, and career goals.
        3. Formulates transparent guidance limitations for incomplete fields.
        4. Evaluates career catalogue pathways across 4 qualitative factors.
        5. Formulates factual, non-hype explanations for each recommended pathway.
        """
        student_interests = profile.get_interests()
        student_skills = profile.get_skills()
        education_level = profile.education_level or ""
        qualification = profile.qualification or ""
        career_goals = profile.career_goals or ""

        # Step A: Run Interest Intelligence Engine
        intel_result = InterestIntelligenceService.analyze_interests(student_interests)
        detected_domains = intel_result.get("domain_summary", [])
        unmapped_interests = intel_result.get("unmapped_interests", [])
        normalized_interests = [item["name"] for item in intel_result.get("interests", []) if item.get("is_mapped")]

        # Step B: Safe Handling of Missing / Incomplete Fields (Guidance Limitations)
        limitations = []
        if not student_interests:
            limitations.append(
                "No interests are recorded on your profile. Pathways are assessed on an exploratory basis."
            )
        elif unmapped_interests:
            unmapped_str = ", ".join(unmapped_interests)
            limitations.append(
                f"The following interest(s) are not indexed in standard career taxonomy: {unmapped_str}. "
                "They have been preserved for future reference but did not contribute to direct domain matching."
            )

        if not student_skills:
            limitations.append(
                "No technical or professional skills are listed on your profile. Skill readiness could not be verified; "
                "recommended foundational skills are suggested for each pathway."
            )

        if not education_level and not qualification:
            limitations.append(
                "Education level and qualification details are unrecorded. Qualification requirements are provided for "
                "informational comparison but could not be verified against current academic standing."
            )

        if not career_goals:
            limitations.append(
                "No stated career goal was specified. Guidance is determined primarily from interest, skill, and educational indicators."
            )

        # Step C: Evaluate Catalogue Pathways
        evaluated_careers = []

        # Prepare normalized student lookup sets
        student_skill_lookup = [s.strip().lower() for s in student_skills if s and s.strip()]
        student_interest_lookup = [i.strip().lower() for i in normalized_interests]
        goal_text_lower = career_goals.lower()

        for career in CAREER_CATALOGUE:
            career_domain = career["domain"]
            related_domains = career.get("related_domains", [])
            career_interests = career.get("related_interests", [])
            important_skills = career.get("important_skills", [])
            supported_education = career.get("education_levels_supported", [])

            # --- 1. Interest Alignment ---
            matched_interests = []
            for ci in career_interests:
                ci_lower = ci.lower()
                for si in student_interest_lookup:
                    if si in ci_lower or ci_lower in si:
                        if ci not in matched_interests:
                            matched_interests.append(ci)

            domain_matched = career_domain in detected_domains
            related_domain_matched = any(rd in detected_domains for rd in related_domains)

            if matched_interests and domain_matched:
                interest_factor = "Strong interest alignment"
                interest_rank = 3
            elif domain_matched:
                interest_factor = "Primary domain alignment"
                interest_rank = 2
            elif related_domain_matched or matched_interests:
                interest_factor = "Related domain or adjacent interest"
                interest_rank = 1
            else:
                interest_factor = "Exploratory / No direct interest match"
                interest_rank = 0

            # --- 2. Skill Alignment ---
            matched_skills = []
            recommended_skills = []
            for sk in important_skills:
                sk_lower = sk.lower()
                is_matched = False
                for user_sk in student_skill_lookup:
                    # Match exact or key term overlap (e.g., "python" in "python / r")
                    if user_sk in sk_lower or sk_lower in user_sk:
                        is_matched = True
                        break
                    # Also check skill aliases
                    aliases = SKILL_ALIASES.get(user_sk, [])
                    if any(a in sk_lower for a in aliases):
                        is_matched = True
                        break
                if is_matched:
                    matched_skills.append(sk)
                else:
                    recommended_skills.append(sk)

            if len(matched_skills) >= 2:
                skill_factor = "Strong skill foundation identified"
                skill_rank = 2
            elif len(matched_skills) == 1:
                skill_factor = "Foundational skills identified"
                skill_rank = 1
            else:
                skill_factor = "Skill development required"
                skill_rank = 0

            # --- 3. Education Alignment ---
            education_factor = "General informational pathway"
            if education_level:
                matched_level = False
                for supported in supported_education:
                    if supported.lower() in education_level.lower() or education_level.lower() in supported.lower():
                        matched_level = True
                        break

                if matched_level:
                    if qualification and any(term in qualification.lower() for term in ["tech", "science", "eng", "law", "med", "com", "arts", "design", "business", "admin"]):
                        education_factor = "Current qualification aligns with common educational routes"
                    else:
                        education_factor = "Educational level meets typical baseline for entry or further study"
                else:
                    education_factor = "Entry typically requires progression or specialized academic credentials"
            else:
                education_factor = "Education details not specified; typical requirements provided for reference"

            # --- 4. Career Goal Alignment ---
            goal_factor = "Not specified"
            goal_rank = 0
            if career_goals:
                career_name_lower = career["name"].lower()
                career_domain_lower = career["domain"].lower()
                if any(w in goal_text_lower for w in career_name_lower.replace("/", " ").replace("-", " ").split() if len(w) > 3):
                    goal_factor = f"Stated goal ('{career_goals}') directly aligns with this pathway"
                    goal_rank = 2
                elif any(w in goal_text_lower for w in career_domain_lower.replace("&", " ").split() if len(w) > 3):
                    goal_factor = f"Stated goal relates to the broader {career_domain} sector"
                    goal_rank = 1
                else:
                    goal_factor = "Stated goal does not directly reference this pathway"

            # --- Overall Qualitative Alignment Level (No unsupported precision) ---
            total_rank = interest_rank * 2 + skill_rank + goal_rank
            if interest_rank >= 2 or (interest_rank >= 1 and (skill_rank >= 1 or goal_rank >= 1)):
                alignment_level = "High Alignment"
            elif interest_rank == 1 or skill_rank >= 1 or goal_rank >= 1:
                alignment_level = "Moderate Alignment"
            else:
                alignment_level = "Exploratory Alignment"

            # --- Factual Explainability Generation ---
            why_identified = cls._build_explanations(
                career=career,
                matched_interests=matched_interests,
                domain_matched=domain_matched,
                related_domain_matched=related_domain_matched,
                matched_skills=matched_skills,
                recommended_skills=recommended_skills,
                education_level=education_level,
                qualification=qualification,
                education_factor=education_factor,
                career_goals=career_goals,
                goal_rank=goal_rank
            )

            evaluated_careers.append({
                "id": career["id"],
                "name": career["name"],
                "domain": career["domain"],
                "related_domains": career.get("related_domains", []),
                "description": career["description"],
                "alignment_level": alignment_level,
                "alignment_factors": {
                    "interest_alignment": interest_factor,
                    "skill_alignment": skill_factor,
                    "education_alignment": education_factor,
                    "goal_alignment": goal_factor
                },
                "why_identified": why_identified,
                "related_interests": career.get("related_interests", []),
                "matched_interests": matched_interests,
                "relevant_skills": matched_skills,
                "matched_skills": matched_skills,
                "important_skills": career.get("important_skills", []),
                "recommended_skill_development": recommended_skills,
                "typical_education": career.get("typical_education", []),
                "education_considerations": [
                    f"Typical educational route: {career['typical_education'][0]}",
                    f"Supported study/entry tiers: {', '.join(career.get('education_levels_supported', ['All Levels']))}"
                ],
                "progression": career.get("progression", []),
                "_internal_rank": total_rank
            })

        # Step D: Deterministic Ordering
        # Order: High Alignment first, then Moderate Alignment, then Exploratory Alignment.
        # Within the same level, sort by internal factor rank descending, then alphabetical.
        alignment_order = {"High Alignment": 0, "Moderate Alignment": 1, "Exploratory Alignment": 2}
        evaluated_careers.sort(key=lambda x: (alignment_order.get(x["alignment_level"], 3), -x["_internal_rank"], x["name"]))

        # Remove internal sorting key from public response
        for item in evaluated_careers:
            item.pop("_internal_rank", None)

        # Filter out purely exploratory careers if strong matches exist, to keep guidance relevant
        high_and_mod = [c for c in evaluated_careers if c["alignment_level"] in ("High Alignment", "Moderate Alignment")]
        if high_and_mod:
            final_careers = high_and_mod
        else:
            # If profile has no matching data, return top exploratory pathways
            final_careers = evaluated_careers[:6]

        # Step E: Compute Simplified Guidance Structure (Target Career & Skill Matched Jobs)
        target_career_data = None
        target_cat = None
        best_overlap = 0

        if career_goals:
            goal_clean = career_goals.strip().lower()
            goal_words = set(w for w in goal_clean.replace("/", " ").replace("-", " ").split() if len(w) > 2)

            for c in CAREER_CATALOGUE:
                c_name_lower = c["name"].lower()
                c_words = set(w for w in c_name_lower.replace("/", " ").replace("-", " ").split() if len(w) > 2)
                overlap = len(goal_words.intersection(c_words))
                if overlap > best_overlap:
                    best_overlap = overlap
                    target_cat = c

        # Fallback to top evaluated career if no explicit goal matched
        if not target_cat and evaluated_careers:
            top_id = evaluated_careers[0]["id"]
            target_cat = next((c for c in CAREER_CATALOGUE if c["id"] == top_id), None)

        if target_cat:
            target_eval = next((c for c in evaluated_careers if c["id"] == target_cat["id"]), None)
            target_matched_skills = target_eval.get("matched_skills", []) if target_eval else []
            target_missing_skills = target_eval.get("recommended_skill_development", []) if target_eval else target_cat.get("important_skills", [])

            if target_matched_skills:
                short_reason = "Matches your career goal and current skills."
            elif career_goals:
                short_reason = "Matches your selected career goal."
            else:
                short_reason = "Top career recommendation based on your profile."

            supported_levels = target_cat.get("education_levels_supported", [])
            typical_edu = target_cat.get("typical_education", [])
            education_step = ""
            has_education_action = False

            if education_level:
                edu_lower = education_level.lower()
                if "undergraduate" in edu_lower:
                    if any("undergraduate" in lvl.lower() for lvl in supported_levels):
                        education_step = "Your Undergraduate degree meets the standard educational baseline for entry."
                    else:
                        education_step = f"Recommended academic step: {typical_edu[0] if typical_edu else 'Advanced degree'}."
                        has_education_action = True
                elif "diploma" in edu_lower:
                    if any("diploma" in lvl.lower() for lvl in supported_levels):
                        education_step = "Your Polytechnic Diploma provides entry-level eligibility for junior developer/technician roles."
                    else:
                        education_step = "Recommended next step: Pursue a Bachelor's degree (B.Tech / B.E) via Lateral Entry."
                        has_education_action = True
                elif "postgraduate" in edu_lower:
                    education_step = "Your Postgraduate degree satisfies advanced qualification criteria."
                elif "secondary" in edu_lower:
                    education_step = f"Recommended next step: Enroll in a Bachelor's degree ({typical_edu[0] if typical_edu else 'Computer Science / Engineering'})."
                    has_education_action = True
                else:
                    education_step = f"Recommended educational route: {typical_edu[0] if typical_edu else 'Relevant Bachelor degree'}."
            elif typical_edu:
                education_step = f"Standard educational route: {typical_edu[0]}."

            target_career_data = {
                "id": target_cat["id"],
                "name": target_cat["name"],
                "domain": target_cat["domain"],
                "career_goal": career_goals or target_cat["name"],
                "short_reason": short_reason,
                "matched_skills": target_matched_skills,
                "missing_skills": target_missing_skills,
                "education_step": education_step,
                "has_education_action": has_education_action
            }

        # 2. Jobs Based on Current Skills (ONLY careers with existing matched skills!)
        skill_matched_careers = []
        for c in evaluated_careers:
            matched = c.get("matched_skills", [])
            if matched and len(matched) > 0:
                if target_cat and c["id"] == target_cat["id"]:
                    reason = f"Matches your career goal and current skills in {', '.join(matched)}."
                else:
                    reason = f"Matches your current skills in {', '.join(matched)}."

                skill_matched_careers.append({
                    "id": c["id"],
                    "name": c["name"],
                    "domain": c["domain"],
                    "short_reason": reason,
                    "matched_skills": matched,
                    "missing_skills": c.get("recommended_skill_development", [])[:4]
                })

        return {
            "success": True,
            "profile_id": profile.id,
            "student_name": profile.full_name,
            "domains": detected_domains,
            "profile_summary": {
                "education_level": education_level or "Not specified",
                "qualification": qualification or "Not specified",
                "skills_count": len(student_skills),
                "interests_count": len(student_interests),
                "career_goals": career_goals or "Not specified"
            },
            "interest_intelligence": {
                "analyzed_interests": intel_result.get("interests", []),
                "detected_domains": detected_domains,
                "unmapped_interests": unmapped_interests
            },
            "guidance_limitations": limitations,
            "total_pathways_evaluated": len(CAREER_CATALOGUE),
            "matched_pathways_count": len(final_careers),
            "target_career": target_career_data,
            "skill_matched_careers": skill_matched_careers,
            "careers": final_careers
        }

    @staticmethod
    def _build_explanations(
        career: Dict[str, Any],
        matched_interests: List[str],
        domain_matched: bool,
        related_domain_matched: bool,
        matched_skills: List[str],
        recommended_skills: List[str],
        education_level: str,
        qualification: str,
        education_factor: str,
        career_goals: str,
        goal_rank: int
    ) -> List[str]:
        """
        Builds transparent, factual, non-hype explanation bullet points.
        Explicitly avoids certainty language and fake percentages.
        """
        reasons = []

        # 1. Interest Connection
        if matched_interests:
            reasons.append(
                f"Interest connection: {', '.join(matched_interests)} directly relates to the core activities of {career['name']}."
            )
        elif domain_matched:
            reasons.append(
                f"Domain connection: The '{career['domain']}' sector was identified from your analyzed interests."
            )
        elif related_domain_matched:
            reasons.append(
                f"Cross-disciplinary connection: This pathway connects to adjacent fields in your identified interest areas."
            )
        else:
            reasons.append(
                "Interest connection: Exploratory pathway assessed based on general profile information."
            )

        # 2. Skill Connection
        if matched_skills:
            reasons.append(
                f"Skill connection: You have recorded foundational skills ({', '.join(matched_skills)}) that are applicable to this pathway."
            )
        else:
            reasons.append(
                "Skill connection: No existing skills directly matching this pathway were found on your profile."
            )

        # 3. Education Connection
        if education_level or qualification:
            edu_desc = f"{qualification} ({education_level})".strip() if qualification and education_level else (qualification or education_level)
            reasons.append(
                f"Education connection: Current standing ({edu_desc}) — {education_factor}."
            )
        else:
            reasons.append(
                "Education connection: Educational background is unrecorded; see typical educational routes for requisite benchmarks."
            )

        # 4. Career Goal Connection (if applicable)
        if goal_rank >= 1 and career_goals:
            reasons.append(
                f"Career goal connection: Your stated goal ('{career_goals}') aligns with this pathway."
            )

        # 5. Development Focus
        if recommended_skills:
            reasons.append(
                f"Development focus: Strengthening skills in {', '.join(recommended_skills[:3])} would support progression in this pathway."
            )

        return reasons
