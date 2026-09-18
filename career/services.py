"""
Career Pathway Guidance Services.
Provides career direction management, explainable pathway discovery,
action plan generation, career roadmaps, and career catalogue lookups.
"""
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from flask import has_request_context, session
from db import db
from eligibility.services import EligibilityService
from skill_gap.services import SkillGapService
from profile.services import ProfileService
from profile.models import StudentProfile
from profile.interest_intelligence import InterestIntelligenceService
from .models import CareerPathway
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


class CareerDirectionService:
    """
    Service for managing career direction entry workflow state.
    Determines whether a student already knows their target career ('known')
    or is entering the career discovery journey ('exploring').
    """

    ALLOWED_DIRECTIONS = {"known", "exploring"}

    @classmethod
    def set_direction(
        cls,
        direction: Any,
        target_role: Optional[Any] = None,
        session_obj: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Validate and store the student's career direction decision.

        :param direction: 'known' or 'exploring'
        :param target_role: Target career title (required if direction is 'known')
        :param session_obj: Optional explicit session dictionary for testing or direct access
        :return: Structured state dictionary
        """
        if direction is None:
            raise ValueError("Career direction is required. Choose 'known' or 'exploring'.")

        norm_direction = str(direction).strip().lower()
        if norm_direction not in cls.ALLOWED_DIRECTIONS:
            raise ValueError(f"Invalid career direction '{direction}'. Allowed values are 'known' or 'exploring'.")

        resolved_role: Optional[str] = None

        if norm_direction == "known":
            if target_role is None or not str(target_role).strip():
                raise ValueError("Target role is required when career direction is 'known'.")
            resolved_role = str(target_role).strip()
        else:
            # Exploring direction: target_role is None
            resolved_role = None

        # Persist to session if within Flask request context or explicit session_obj
        target_session = session_obj if session_obj is not None else (session if has_request_context() else None)
        if target_session is not None:
            prev_role = target_session.get("target_role")
            target_session["career_direction"] = norm_direction
            if norm_direction == "known":
                target_session["target_role"] = resolved_role
                if prev_role != resolved_role:
                    target_session.pop("selected_pathway", None)
            else:
                # Exploring branch: explicitly clear target_role and stale selected pathway
                target_session["target_role"] = None
                target_session.pop("selected_pathway", None)
                target_session.pop("shortlisted_pathways", None)

        message = (
            f"Target career set to '{resolved_role}'."
            if norm_direction == "known"
            else "Exploration mode activated. Ready to begin career discovery."
        )

        return {
            "status": "success",
            "career_direction": norm_direction,
            "target_role": resolved_role,
            "message": message
        }

    @classmethod
    def get_direction(cls, session_obj: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieve current career direction workflow state.
        Guarantees that exploring mode always reports target_role as None.
        """
        target_session = session_obj if session_obj is not None else (session if has_request_context() else None)
        if target_session is not None:
            direction = target_session.get("career_direction")
            # If direction is exploring, target_role is strictly None
            target_role = target_session.get("target_role") if direction == "known" else None
            return {
                "career_direction": direction,
                "target_role": target_role,
                "is_set": bool(direction)
            }

        return {
            "career_direction": None,
            "target_role": None,
            "is_set": False
        }

    @classmethod
    def clear_direction(cls, session_obj: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Reset career direction workflow state.
        """
        target_session = session_obj if session_obj is not None else (session if has_request_context() else None)
        if target_session is not None:
            target_session.pop("career_direction", None)
            target_session.pop("target_role", None)
            target_session.pop("selected_pathway", None)
            target_session.pop("shortlisted_pathways", None)

        return {
            "status": "success",
            "message": "Career direction state cleared.",
            "career_direction": None,
            "target_role": None,
            "is_set": False
        }


class PathwayDiscoveryService:
    """
    Deterministic & Explainable Pathway Discovery Engine.
    Evaluates student evidence or known target role to synthesize relevant career and education pathways
    without making unsupported psychological claims or universal 'best career' assertions.
    """

    PATHWAY_DATABASE = [
        {
            "id": "software-engineering",
            "name": "Software Engineering",
            "industry_sector": "Technology",
            "category": "Career Pathway",
            "overview": "Designing, building, and maintaining software applications, systems, and platforms.",
            "relevant_interests": ["technology", "engineering", "computer science", "ai", "research"],
            "relevant_skills": ["programming", "problem solving", "data analysis", "mathematics"],
            "relevant_subjects": ["computer science", "mathematics", "physics"],
            "relevant_work_styles": ["working with technology", "creative work", "research/problem solving"],
            "relevant_career_prefs": ["private sector", "entrepreneurship", "open to multiple options"],
            "education_route": "B.Tech / B.E in Computer Science, B.Sc Computer Science, BCA, or equivalent software development bootcamp.",
            "typical_next_step": "Build core competence in Python/JavaScript, version control (Git), and develop sample portfolio projects.",
            "requirements": {
                "min_education": "Bachelor's",
                "required_degree": ["Computer Science", "Information Technology", "Engineering", "BCA", "MCA"],
                "required_skills": ["Programming", "Problem Solving", "Git", "Databases"]
            },
            "sources": [
                {
                    "name": "National Career Service (NCS) - IT & Software",
                    "url": "https://www.ncs.gov.in",
                    "verified_at": "2026-01-15"
                },
                {
                    "name": "AICTE Technology Pathway Framework",
                    "url": "https://www.aicte-india.org",
                    "verified_at": "2026-01-20"
                }
            ]
        },
        {
            "id": "data-science-analytics",
            "name": "Data Science & Analytics",
            "industry_sector": "Technology",
            "category": "Career Pathway",
            "overview": "Extracting insights from structured and unstructured data using statistics, machine learning, and visualization.",
            "relevant_interests": ["technology", "research", "finance", "business"],
            "relevant_skills": ["data analysis", "mathematics", "programming", "problem solving"],
            "relevant_subjects": ["mathematics", "computer science", "statistics"],
            "relevant_work_styles": ["working with data", "working with technology", "research/problem solving"],
            "relevant_career_prefs": ["private sector", "higher education/research", "open to multiple options"],
            "education_route": "Bachelor's degree in Data Science, Statistics, Mathematics, or Computer Science.",
            "typical_next_step": "Master SQL, Python data libraries (Pandas, Scikit-learn), and explore statistical modeling.",
            "requirements": {
                "min_education": "Bachelor's",
                "required_degree": ["Data Science", "Statistics", "Mathematics", "Computer Science", "Engineering"],
                "required_skills": ["Data Analysis", "Mathematics", "Programming", "Problem Solving", "SQL"]
            },
            "sources": [
                {
                    "name": "NASSCOM FutureSkills Prime - Data & AI",
                    "url": "https://futureskillsprime.in",
                    "verified_at": "2026-02-01"
                }
            ]
        },
        {
            "id": "cloud-devops",
            "name": "Cloud Architecture & DevOps",
            "industry_sector": "Technology",
            "category": "Career Pathway",
            "overview": "Managing cloud infrastructure, automated CI/CD pipelines, and high-availability enterprise services.",
            "relevant_interests": ["technology", "engineering"],
            "relevant_skills": ["programming", "problem solving", "teamwork"],
            "relevant_subjects": ["computer science", "physics"],
            "relevant_work_styles": ["working with technology", "working with machines", "office-based work"],
            "relevant_career_prefs": ["private sector", "open to multiple options"],
            "education_route": "Bachelor's in Engineering/IT, Diploma in Computer Engineering, or Cloud Platform Certifications (AWS/GCP/Azure).",
            "typical_next_step": "Practice Linux administration, containerization (Docker), and cloud fundamentals.",
            "requirements": {
                "min_education": "Bachelor's",
                "required_degree": ["Engineering", "Computer Science", "Information Technology", "Computer Applications"],
                "required_skills": ["Programming", "Linux", "Docker", "Kubernetes", "AWS", "Problem Solving"]
            },
            "sources": [
                {
                    "name": "National Career Service - Cloud Technologies",
                    "url": "https://www.ncs.gov.in",
                    "verified_at": "2026-01-15"
                }
            ]
        },
        {
            "id": "healthcare-medicine",
            "name": "Medicine & Healthcare",
            "industry_sector": "Healthcare",
            "category": "Career Pathway",
            "overview": "Diagnosing, treating, and preventing illnesses to improve human health and well-being.",
            "relevant_interests": ["healthcare", "medicine", "life sciences", "biology", "research"],
            "relevant_skills": ["biology", "communication", "problem solving", "teamwork", "leadership"],
            "relevant_subjects": ["biology", "chemistry", "physics"],
            "relevant_work_styles": ["working with people", "research/problem solving", "field/outdoor work"],
            "relevant_career_prefs": ["government sector", "private sector", "higher education/research"],
            "education_route": "MBBS, BDS, B.Pharm, B.Sc Nursing, or Allied Health Sciences degrees.",
            "typical_next_step": "Prepare for national medical entrance exams (e.g. NEET) and complete core laboratory sciences coursework.",
            "requirements": {
                "min_education": "Bachelor's",
                "required_degree": ["Medicine", "MBBS", "BDS", "Pharmacy", "Nursing", "Allied Health Sciences", "Biology"],
                "required_skills": ["Communication", "Problem Solving", "Teamwork", "Leadership"]
            },
            "sources": [
                {
                    "name": "National Medical Commission (NMC)",
                    "url": "https://www.nmc.org.in",
                    "verified_at": "2026-01-10"
                }
            ]
        },
        {
            "id": "civil-engineering",
            "name": "Civil & Infrastructure Engineering",
            "industry_sector": "Engineering",
            "category": "Career Pathway",
            "overview": "Planning, designing, and constructing vital public infrastructure including bridges, roads, and buildings.",
            "relevant_interests": ["engineering", "government/public service"],
            "relevant_skills": ["problem solving", "mathematics", "leadership", "design"],
            "relevant_subjects": ["physics", "mathematics"],
            "relevant_work_styles": ["working with machines", "field/outdoor work", "creative work"],
            "relevant_career_prefs": ["government sector", "private sector", "entrepreneurship"],
            "education_route": "B.Tech / B.E in Civil Engineering or Diploma in Civil Engineering.",
            "typical_next_step": "Review structural mechanics fundamentals, CAD tools, and engineering licensures.",
            "requirements": {
                "min_education": "Bachelor's",
                "required_degree": ["Civil Engineering", "Infrastructure Engineering", "Engineering"],
                "required_skills": ["Problem Solving", "Mathematics", "Leadership", "Design"]
            },
            "sources": [
                {
                    "name": "AICTE Engineering Curriculum Guidelines",
                    "url": "https://www.aicte-india.org",
                    "verified_at": "2026-01-20"
                }
            ]
        },
        {
            "id": "education-teaching",
            "name": "Education & Academic Teaching",
            "industry_sector": "Education",
            "category": "Career Pathway",
            "overview": "Educating, mentoring, and inspiring students in schools, colleges, and academic institutions.",
            "relevant_interests": ["education", "research", "government/public service"],
            "relevant_skills": ["communication", "public speaking", "writing", "leadership", "teamwork"],
            "relevant_subjects": ["languages", "mathematics", "social sciences", "arts", "physics", "chemistry", "biology"],
            "relevant_work_styles": ["working with people", "creative work", "office-based work"],
            "relevant_career_prefs": ["government sector", "higher education/research", "private sector"],
            "education_route": "Bachelor's/Master's degree in subject specialization + B.Ed or qualification in Teacher Eligibility Tests (TET/NET).",
            "typical_next_step": "Participate in academic mentoring, tutoring, and pursue teacher eligibility prerequisites.",
            "requirements": {
                "min_education": "Bachelor's",
                "required_degree": ["Education", "B.Ed", "Arts", "Science", "Commerce", "Languages"],
                "required_skills": ["Communication", "Public Speaking", "Writing", "Leadership"]
            },
            "sources": [
                {
                    "name": "National Council for Teacher Education (NCTE)",
                    "url": "https://ncte.gov.in",
                    "verified_at": "2026-01-18"
                }
            ]
        },
        {
            "id": "banking-finance",
            "name": "Banking & Financial Analysis",
            "industry_sector": "Finance",
            "category": "Career Pathway",
            "overview": "Managing capital, auditing financial statements, risk assessment, and financial strategy.",
            "relevant_interests": ["finance", "business", "government/public service"],
            "relevant_skills": ["mathematics", "data analysis", "problem solving", "communication"],
            "relevant_subjects": ["commerce", "mathematics", "social sciences"],
            "relevant_work_styles": ["working with data", "office-based work", "working with people"],
            "relevant_career_prefs": ["private sector", "government sector", "entrepreneurship"],
            "education_route": "B.Com, BBA Finance, Chartered Accountancy (CA), CFA, or MBA Finance.",
            "typical_next_step": "Develop expertise in spreadsheet modeling, financial reporting standards, and quantitative economics.",
            "requirements": {
                "min_education": "Bachelor's",
                "required_degree": ["Commerce", "Finance", "B.Com", "BBA", "Economics", "Accounting"],
                "required_skills": ["Mathematics", "Data Analysis", "Problem Solving", "Communication"]
            },
            "sources": [
                {
                    "name": "Institute of Chartered Accountants of India (ICAI)",
                    "url": "https://www.icai.org",
                    "verified_at": "2026-01-25"
                }
            ]
        },
        {
            "id": "public-service-govt",
            "name": "Public Administration & Civil Services",
            "industry_sector": "Government/Public Service",
            "category": "Career Pathway",
            "overview": "Policy formulation, public resource administration, law enforcement, and governance.",
            "relevant_interests": ["government/public service", "law", "education"],
            "relevant_skills": ["leadership", "communication", "writing", "problem solving"],
            "relevant_subjects": ["social sciences", "languages", "arts"],
            "relevant_work_styles": ["working with people", "field/outdoor work", "office-based work"],
            "relevant_career_prefs": ["government sector"],
            "education_route": "Bachelor's degree in any discipline from a recognized university.",
            "typical_next_step": "Review syllabus for Civil Services / State PSC exams and read national policy affairs.",
            "requirements": {
                "min_education": "Bachelor's",
                "required_degree": ["Any Discipline", "Arts", "Science", "Commerce", "Social Sciences", "Law"],
                "required_skills": ["Leadership", "Communication", "Writing", "Problem Solving"]
            },
            "sources": [
                {
                    "name": "Union Public Service Commission (UPSC)",
                    "url": "https://www.upsc.gov.in",
                    "verified_at": "2026-01-12"
                }
            ]
        },
        {
            "id": "creative-design",
            "name": "UI/UX & Product Design",
            "industry_sector": "Design/Creative",
            "category": "Career Pathway",
            "overview": "Crafting intuitive digital experiences, visual interfaces, and human-centric design solutions.",
            "relevant_interests": ["design/creative", "media", "technology"],
            "relevant_skills": ["design", "creativity", "communication", "problem solving"],
            "relevant_subjects": ["arts", "computer science"],
            "relevant_work_styles": ["creative work", "working with technology", "working with people"],
            "relevant_career_prefs": ["private sector", "entrepreneurship"],
            "education_route": "Bachelor of Design (B.Des), Fine Arts (BFA), or UI/UX certifications.",
            "typical_next_step": "Learn wireframing and prototyping tools (Figma) and create design case studies.",
            "requirements": {
                "min_education": "Bachelor's",
                "required_degree": ["Design", "B.Des", "Fine Arts", "Visual Arts", "Computer Science"],
                "required_skills": ["Design", "Creativity", "Communication", "Problem Solving"]
            },
            "sources": [
                {
                    "name": "National Institute of Design (NID)",
                    "url": "https://www.nid.edu",
                    "verified_at": "2026-01-22"
                }
            ]
        },
        {
            "id": "entrepreneurship-startups",
            "name": "Entrepreneurship & Innovation",
            "industry_sector": "Business",
            "category": "Career Pathway",
            "overview": "Founding, managing, and scaling innovative business ventures and product solutions.",
            "relevant_interests": ["business", "technology", "agriculture"],
            "relevant_skills": ["leadership", "creativity", "communication", "problem solving", "teamwork"],
            "relevant_subjects": ["commerce", "computer science"],
            "relevant_work_styles": ["creative work", "combination", "working with people"],
            "relevant_career_prefs": ["entrepreneurship"],
            "education_route": "Degree in Business Administration, Engineering, or domain specialization.",
            "typical_next_step": "Validate problem-solution fit, conduct customer discovery interviews, and develop a minimum viable product.",
            "requirements": {
                "min_education": "Bachelor's",
                "required_degree": ["Business", "Management", "Engineering", "Commerce", "Any Discipline"],
                "required_skills": ["Leadership", "Creativity", "Communication", "Problem Solving", "Teamwork"]
            },
            "sources": [
                {
                    "name": "Startup India Initiative",
                    "url": "https://www.startupindia.gov.in",
                    "verified_at": "2026-01-30"
                }
            ]
        },
        {
            "id": "legal-law",
            "name": "Law & Legal Practice",
            "industry_sector": "Legal / Law",
            "category": "Career Pathway",
            "overview": "Legal counsel, statutory compliance, litigation, legal research, and judicial advocacy.",
            "relevant_interests": ["law", "government/public service", "education", "research"],
            "relevant_skills": ["communication", "writing", "problem solving", "leadership", "critical thinking"],
            "relevant_subjects": ["social sciences", "languages", "commerce", "arts"],
            "relevant_work_styles": ["working with people", "research/problem solving", "office-based work"],
            "relevant_career_prefs": ["private sector", "government sector", "entrepreneurship"],
            "education_route": "B.A. LL.B / B.B.A. LL.B (5-year Integrated) or 3-year LL.B after graduation, followed by Bar Council enrollment.",
            "typical_next_step": "Prepare for national law entrance exams (e.g., CLAT, AILET) and develop core competence in legal research and writing.",
            "requirements": {
                "min_education": "Bachelor's",
                "required_degree": ["Law", "LL.B", "B.A. LL.B", "BBA LL.B", "Legal Studies"],
                "required_skills": ["Legal Research", "Communication", "Writing", "Problem Solving", "Critical Thinking"]
            },
            "sources": [
                {
                    "name": "Bar Council of India (BCI) Framework",
                    "url": "http://www.barcouncilofindia.org",
                    "verified_at": "2026-01-20"
                },
                {
                    "name": "National Career Service (NCS) - Legal & Judicial",
                    "url": "https://www.ncs.gov.in",
                    "verified_at": "2026-01-15"
                }
            ]
        }
    ]

    INTEREST_SYNONYMS = {
        "technology": ["tech", "software", "computer science", "ai", "coding"],
        "tech": ["technology", "software", "computer science"],
        "computer science": ["technology", "software", "programming", "coding"],
        "ai": ["artificial intelligence", "technology", "machine learning"],
        "coding": ["programming", "technology", "software"],
        "programming": ["coding", "software", "technology"],
        "helping people": ["healthcare", "education", "community service", "working with people"],
        "law": ["legal", "judiciary", "justice", "law & legal practice"],
        "legal": ["law", "judiciary", "justice", "law & legal practice"],
        "finance": ["banking", "economics", "investing", "commerce"],
        "banking": ["finance", "economics", "investing", "commerce"],
        "teaching": ["education", "academic", "mentoring"],
        "education": ["teaching", "academic", "mentoring"],
        "medicine": ["healthcare", "biology", "medical", "clinical"],
        "healthcare": ["medicine", "biology", "medical", "clinical"],
        "design": ["creative", "ui/ux", "visual arts", "product design"],
        "creative": ["design", "ui/ux", "visual arts", "media"],
    }

    SKILL_SYNONYMS = {
        "coding": ["programming", "software development"],
        "programming": ["coding", "software development"],
        "math": ["mathematics", "quantitative"],
        "mathematics": ["math", "quantitative"],
        "helping people": ["communication", "teamwork", "empathy", "working with people"],
        "biology": ["biology", "life sciences", "medical sciences"],
        "critical thinking": ["problem solving", "critical thinking"],
        "problem solving": ["critical thinking", "analytical thinking"],
        "design": ["ui/ux", "creativity", "visual design"],
        "creativity": ["design", "innovation"],
        "public speaking": ["communication", "presentation"],
        "writing": ["communication", "documentation"],
    }

    WORK_PREF_SYNONYMS = {
        "helping people": ["working with people"],
        "working with people": ["helping people"],
        "working with tech": ["working with technology"],
        "working with technology": ["working with tech"],
        "working with data": ["data analysis", "research"],
    }

    @classmethod
    def _match_dimension(
        cls,
        student_items: List[Any],
        pathway_items: List[str],
        synonyms: Optional[Dict[str, List[str]]] = None
    ) -> List[str]:
        """
        Identify which student items match pathway requirements/metadata.
        Returns list of matched student items (preserving casing).
        """
        matched = []
        if not student_items or not pathway_items:
            return matched

        norm_pathway = [re.sub(r'[^a-z0-9]+', ' ', str(x).lower()).strip() for x in pathway_items if str(x).strip()]
        pathway_tokens = set()
        for np in norm_pathway:
            for tok in np.split():
                if len(tok) >= 2:
                    pathway_tokens.add(tok)

        for raw_item in student_items:
            if raw_item is None:
                continue
            item_str = str(raw_item).strip()
            norm_item = re.sub(r'[^a-z0-9]+', ' ', item_str.lower()).strip()
            if not norm_item:
                continue

            is_match = False

            # 1. Exact string match against normalized pathway item
            if norm_item in norm_pathway:
                is_match = True

            # 2. Substring containment if token length >= 3
            if not is_match:
                for np in norm_pathway:
                    if len(norm_item) >= 3 and (norm_item in np or np in norm_item):
                        is_match = True
                        break

            # 3. Whole token match
            if not is_match:
                item_tokens = [t for t in norm_item.split() if len(t) >= 2 and t not in ('with', 'and', 'for', 'the', 'in', 'of')]
                if item_tokens and all(it in pathway_tokens or any(it in np for np in norm_pathway) for it in item_tokens):
                    is_match = True

            # 4. Synonym expansion
            if not is_match and synonyms:
                syn_list = synonyms.get(norm_item, [])
                for syn in syn_list:
                    norm_syn = re.sub(r'[^a-z0-9]+', ' ', syn.lower()).strip()
                    if norm_syn in norm_pathway or any(norm_syn in np or np in norm_syn for np in norm_pathway):
                        is_match = True
                        break

            if is_match and item_str not in matched:
                matched.append(item_str)

        return matched

    @classmethod
    def discover_pathways(
        cls,
        context: Optional[Dict[str, Any]] = None,
        session_obj: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute pathway discovery explicitly branching on career_direction.
        - If career_direction == 'known': discovers pathway(s) relevant to target_role.
        - If career_direction == 'exploring': discovers multiple relevant pathways from student profile evidence.
        """
        ctx = context or {}
        target_session = session_obj if session_obj is not None else (session if has_request_context() else None)

        # 1. Determine career direction - context takes precedence, then session, default to exploring
        direction = (
            ctx.get("career_direction")
            or (target_session.get("career_direction") if target_session else None)
            or "exploring"
        )
        direction = str(direction).strip().lower()

        # 2. Known target pathway flow
        if direction == "known":
            target_role = (
                ctx.get("target_role")
                or ctx.get("role")
                or (target_session.get("target_role") if target_session else None)
            )
            if target_role and str(target_role).strip():
                return cls._discover_for_known(str(target_role).strip())

        # 3. Exploring profile pathway flow (target_role must be None / ignored)
        student_profile = (
            ctx.get("student_profile")
            or ctx.get("profile")
            or (target_session.get("exploration_profile") if target_session else None)
            or {}
        )

        return cls._discover_for_exploring(student_profile)

    @classmethod
    def _discover_for_known(cls, target_role: str) -> Dict[str, Any]:
        """
        Assemble structured pathway details tailored to the student's declared target role.
        """
        clean_role = str(target_role).strip()
        role_lower = clean_role.lower()

        # 1. Check direct name or ID match
        matched_template = None
        for p in cls.PATHWAY_DATABASE:
            p_name_lower = p["name"].lower()
            p_id_lower = p["id"].lower()
            if role_lower == p_name_lower or role_lower == p_id_lower:
                matched_template = p
                break

        # 2. Check role alias mappings
        if not matched_template:
            role_aliases = {
                "cloud": "cloud-devops",
                "devops": "cloud-devops",
                "aws": "cloud-devops",
                "data scientist": "data-science-analytics",
                "data analyst": "data-science-analytics",
                "data science": "data-science-analytics",
                "data": "data-science-analytics",
                "software engineer": "software-engineering",
                "software": "software-engineering",
                "developer": "software-engineering",
                "programmer": "software-engineering",
                "coder": "software-engineering",
                "full stack": "software-engineering",
                "frontend": "software-engineering",
                "backend": "software-engineering",
                "doctor": "healthcare-medicine",
                "physician": "healthcare-medicine",
                "surgeon": "healthcare-medicine",
                "medical": "healthcare-medicine",
                "nurse": "healthcare-medicine",
                "lawyer": "legal-law",
                "advocate": "legal-law",
                "attorney": "legal-law",
                "law": "legal-law",
                "legal": "legal-law",
                "judge": "legal-law",
                "civil engineer": "civil-engineering",
                "civil": "civil-engineering",
                "teacher": "education-teaching",
                "teaching": "education-teaching",
                "professor": "education-teaching",
                "lecturer": "education-teaching",
                "banker": "banking-finance",
                "finance": "banking-finance",
                "accountant": "banking-finance",
                "ias": "public-service-govt",
                "civil service": "public-service-govt",
                "public service": "public-service-govt",
                "govt": "public-service-govt",
                "designer": "creative-design",
                "ui/ux": "creative-design",
                "product design": "creative-design",
                "entrepreneur": "entrepreneurship-startups",
                "startup": "entrepreneurship-startups",
            }
            for alias_key, target_pid in role_aliases.items():
                if alias_key in role_lower or role_lower in alias_key:
                    for p in cls.PATHWAY_DATABASE:
                        if p["id"] == target_pid:
                            matched_template = p
                            break
                    if matched_template:
                        break

        # 3. Substring & Token match
        if not matched_template:
            for p in cls.PATHWAY_DATABASE:
                p_name_lower = p["name"].lower()
                p_id_lower = p["id"].lower()
                if (
                    role_lower in p_name_lower or p_name_lower in role_lower or
                    role_lower in p_id_lower or p_id_lower in role_lower
                ):
                    matched_template = p
                    break

        if not matched_template:
            for p in cls.PATHWAY_DATABASE:
                p_name_lower = p["name"].lower()
                if any(token in p_name_lower for token in role_lower.split() if len(token) > 3):
                    matched_template = p
                    break

        if matched_template:
            pathway_obj = {
                "id": matched_template["id"],
                "name": matched_template["name"],
                "target_role": clean_role,
                "type": matched_template["category"],
                "industry_sector": matched_template["industry_sector"],
                "overview": matched_template["overview"],
                "relevance": {
                    "score": 10.0,
                    "matched_interests": [matched_template["industry_sector"]],
                    "matched_skills": matched_template["relevant_skills"][:3],
                    "matched_subjects": matched_template["relevant_subjects"][:2],
                    "matched_work_preferences": [],
                    "matched_career_preferences": [],
                    "matched_preferences": []
                },
                "why_relevant": f"Target pathway information tailored for your requested career goal: '{clean_role}'.",
                "education_route": matched_template["education_route"],
                "education_pathway": matched_template["education_route"],
                "next_step": matched_template["typical_next_step"],
                "typical_next_step": matched_template["typical_next_step"],
                "requirements": matched_template.get("requirements", {
                    "min_education": "Bachelor's",
                    "required_degree": ["Relevant Field", "Any Discipline"],
                    "required_skills": matched_template.get("relevant_skills", [])
                }),
                "sources": matched_template["sources"],
                "source_attribution": "Verified official curriculum guidelines and career standards."
            }
        else:
            # Construct a clean specialized pathway object without fabricating unverifiable requirements
            pathway_obj = {
                "id": re.sub(r'[^a-zA-Z0-9]+', '-', clean_role.lower()).strip('-'),
                "name": clean_role,
                "target_role": clean_role,
                "type": "Career Pathway",
                "industry_sector": "Specialized Career Track",
                "overview": f"Career progression pathway focused on {clean_role}.",
                "relevance": {
                    "score": 10.0,
                    "matched_interests": ["Specific Career Target"],
                    "matched_skills": [],
                    "matched_subjects": [],
                    "matched_work_preferences": [],
                    "matched_career_preferences": [],
                    "matched_preferences": []
                },
                "why_relevant": f"Direct pathway research assembled for your target career: '{clean_role}'.",
                "education_route": "Bachelor's / Professional Degree or specialized accredited coursework required for this domain.",
                "education_pathway": "Bachelor's / Professional Degree or specialized accredited coursework required for this domain.",
                "next_step": "Benchmark current skills against role requirements in the Skill Gap engine.",
                "typical_next_step": "Benchmark current skills against role requirements in the Skill Gap engine.",
                "requirements": {
                    "min_education": "Bachelor's",
                    "required_degree": [clean_role, "Related Field", "Any Discipline"],
                    "required_skills": ["Domain Knowledge", "Problem Solving", "Communication"]
                },
                "sources": [
                    {
                        "name": "National Career Service (NCS) Framework",
                        "url": "https://www.ncs.gov.in",
                        "verified_at": "2026-01-15"
                    }
                ],
                "source_attribution": "Verified National Occupational Standards."
            }

        return {
            "status": "success",
            "career_direction": "known",
            "target_role": clean_role,
            "total_pathways": 1,
            "pathways": [pathway_obj],
            "message": f"Target pathway information ready for '{clean_role}'."
        }

    @classmethod
    def _discover_for_exploring(cls, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate student evidence (interests, skills, subjects, work preferences, career preferences)
        and construct explainable, non-prescriptive pathway options with meaningful thresholding.
        """
        scored_pathways: List[Dict[str, Any]] = []

        interests_input = profile.get("interests", [])
        skills_input = profile.get("skills", [])
        subjects_input = profile.get("subjects", [])
        work_prefs_input = profile.get("work_preferences", [])
        career_prefs_input = profile.get("career_preferences", [])
        edu_level = profile.get("education_level", "Not specified")

        for p in cls.PATHWAY_DATABASE:
            # 1. Multi-attribute dimension matching
            matched_int = cls._match_dimension(
                interests_input,
                p["relevant_interests"] + [p["industry_sector"]],
                cls.INTEREST_SYNONYMS
            )
            matched_sk = cls._match_dimension(
                skills_input,
                p["relevant_skills"] + p.get("requirements", {}).get("required_skills", []),
                cls.SKILL_SYNONYMS
            )
            matched_sub = cls._match_dimension(
                subjects_input,
                p["relevant_subjects"]
            )
            matched_w = cls._match_dimension(
                work_prefs_input,
                p["relevant_work_styles"],
                cls.WORK_PREF_SYNONYMS
            )
            matched_c = cls._match_dimension(
                career_prefs_input,
                p["relevant_career_prefs"]
            )

            # Distinguish specific career preference vs generic "open"
            has_specific_career_pref = any(
                str(cp).strip().lower() != "open to multiple options" for cp in matched_c
            )

            # 2. Accumulated multi-attribute score
            # Primary dimension matches
            primary_matches = len(matched_int) + len(matched_sk) + len(matched_sub)
            
            # Check if sector/domain is explicitly mentioned in interests
            is_direct_sector_interest = any(
                p["industry_sector"].lower() in str(i).lower() or str(i).lower() in p["industry_sector"].lower()
                for i in matched_int
            )

            match_score = (
                len(matched_int) * 4.0
                + len(matched_sk) * 3.0
                + len(matched_sub) * 2.0
                + len(matched_w) * 1.5
                + (len(matched_c) * 1.0 if has_specific_career_pref else (0.5 if matched_c else 0.0))
                + (1.0 if is_direct_sector_interest else 0.0)
            )

            # Dimension diversity
            dimension_diversity = (
                (1 if matched_int else 0)
                + (1 if matched_sk else 0)
                + (1 if matched_sub else 0)
                + (1 if matched_w else 0)
                + (1 if matched_c else 0)
            )

            # 3. Meaningful relevance threshold
            # Pathway MUST have at least one primary match (interest, skill, or subject) OR multiple strong preference matches
            is_relevant = (
                primary_matches > 0 and match_score >= 2.0
            ) or (
                len(matched_w) > 0 and len(matched_c) > 0 and match_score >= 2.5
            )

            if not is_relevant:
                continue

            # 4. Build explainable evidence-backed rationale
            evidence_points = []
            if matched_int:
                evidence_points.append(f"interests in ({', '.join(matched_int)})")
            if matched_sk:
                evidence_points.append(f"skills in ({', '.join(matched_sk)})")
            if matched_sub:
                evidence_points.append(f"enjoyed subjects ({', '.join(matched_sub)})")
            if matched_w:
                evidence_points.append(f"work preferences ({', '.join(matched_w)})")
            if matched_c:
                evidence_points.append(f"career preferences ({', '.join(matched_c)})")

            if evidence_points:
                why_relevant = f"Matched evidence: Relevant because you indicated {', and '.join(evidence_points)}."
            else:
                why_relevant = f"Exploratory pathway aligned with your profile."

            scored_pathways.append({
                "score": match_score,
                "diversity": dimension_diversity,
                "pathway": {
                    "id": p["id"],
                    "name": p["name"],
                    "type": p["category"],
                    "industry_sector": p["industry_sector"],
                    "overview": p["overview"],
                    "relevance_score": round(match_score, 1),
                    "matched_interests": matched_int,
                    "matched_skills": matched_sk,
                    "matched_subjects": matched_sub,
                    "matched_work_prefs": matched_w,
                    "matched_career_prefs": matched_c,
                    "relevance": {
                        "score": round(match_score, 1),
                        "matched_interests": matched_int,
                        "matched_skills": matched_sk,
                        "matched_subjects": matched_sub,
                        "matched_work_preferences": matched_w,
                        "matched_career_preferences": matched_c,
                        "matched_preferences": matched_w + matched_c
                    },
                    "why_relevant": why_relevant,
                    "education_route": p["education_route"],
                    "education_pathway": p["education_route"],
                    "next_step": p["typical_next_step"],
                    "typical_next_step": p["typical_next_step"],
                    "sources": p["sources"],
                    "source_attribution": "Verified official curriculum guidelines and standards."
                }
            })

        # 5. Handle weak / no matches state cleanly
        if not scored_pathways:
            return {
                "status": "success",
                "career_direction": "exploring",
                "target_role": None,
                "total_pathways": 0,
                "student_profile": profile,
                "pathways": [],
                "message": "No strong pathway matches were found from the information provided. Please add more interests, skills, or work preferences in the Career Discovery Questionnaire to explore relevant pathways."
            }

        # 6. Rank relevant pathways by score descending, then by diversity
        scored_pathways.sort(
            key=lambda x: (x["score"], x["diversity"]),
            reverse=True
        )

        top_pathways = [item["pathway"] for item in scored_pathways[:6]]

        return {
            "status": "success",
            "career_direction": "exploring",
            "target_role": None,
            "total_pathways": len(top_pathways),
            "student_profile": profile,
            "pathways": top_pathways,
            "message": f"Identified {len(top_pathways)} career pathways for exploration based on your profile evidence."
        }

    @classmethod
    def select_pathway(
        cls,
        pathway_id: str,
        pathway_name: Optional[str] = None,
        session_obj: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store the student's selected pathway in session state for downstream analysis.
        """
        if not pathway_id or not str(pathway_id).strip():
            raise ValueError("Pathway ID is required to select a pathway.")

        clean_id = str(pathway_id).strip()

        # Resolve pathway name from database if not supplied
        resolved_name = pathway_name
        if not resolved_name:
            for p in cls.PATHWAY_DATABASE:
                if p["id"] == clean_id:
                    resolved_name = p["name"]
                    break
            if not resolved_name:
                resolved_name = clean_id.replace('-', ' ').title()

        selection_record = {
            "id": clean_id,
            "name": str(resolved_name).strip(),
            "type": "Career Pathway",
            "selected_at": datetime.utcnow().isoformat()
        }

        target_session = session_obj if session_obj is not None else (session if has_request_context() else None)
        if target_session is not None:
            target_session["selected_pathway"] = selection_record
            # In exploring mode, selecting a pathway establishes target_role to the selected pathway name for downstream consumption.
            # In known mode, preserve declared target_role so conflict detection functions properly.
            if target_session.get("career_direction") == "exploring":
                target_session["target_role"] = resolved_name
            elif not target_session.get("target_role"):
                target_session["target_role"] = resolved_name

        return {
            "status": "success",
            "selected_pathway": selection_record,
            "message": f"Pathway '{resolved_name}' selected. Ready for Eligibility verification."
        }

    @classmethod
    def get_selected_pathway(cls, session_obj: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieve the student's currently selected pathway from session.
        """
        target_session = session_obj if session_obj is not None else (session if has_request_context() else None)
        if target_session is not None:
            sel = target_session.get("selected_pathway")
            return {
                "status": "success",
                "selected_pathway": sel,
                "is_selected": bool(sel)
            }

        return {
            "status": "success",
            "selected_pathway": None,
            "is_selected": False
        }

    @classmethod
    def clear_selected_pathway(cls, session_obj: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Clear the selected pathway from session and reset exploring target_role.
        """
        target_session = session_obj if session_obj is not None else (session if has_request_context() else None)
        if target_session is not None:
            target_session.pop("selected_pathway", None)
            if target_session.get("career_direction") == "exploring":
                target_session["target_role"] = None

        return {
            "status": "success",
            "message": "Selected pathway cleared.",
            "selected_pathway": None,
            "is_selected": False
        }

    @classmethod
    def toggle_shortlist(cls, pathway_id: str, session_obj: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Toggle a pathway ID in the student's shortlist set in session.
        """
        if not pathway_id or not str(pathway_id).strip():
            raise ValueError("Pathway ID is required.")

        clean_id = str(pathway_id).strip()
        target_session = session_obj if session_obj is not None else (session if has_request_context() else None)

        shortlist = []
        is_shortlisted = False
        if target_session is not None:
            shortlist = list(target_session.get("shortlisted_pathways", []))
            if clean_id in shortlist:
                shortlist.remove(clean_id)
                is_shortlisted = False
            else:
                shortlist.append(clean_id)
                is_shortlisted = True
            target_session["shortlisted_pathways"] = shortlist

        return {
            "status": "success",
            "pathway_id": clean_id,
            "is_shortlisted": is_shortlisted,
            "shortlisted_pathways": shortlist
        }

    @classmethod
    def get_shortlisted_pathways(cls, session_obj: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Retrieve list of shortlisted pathway IDs.
        """
        target_session = session_obj if session_obj is not None else (session if has_request_context() else None)
        if target_session is not None:
            return list(target_session.get("shortlisted_pathways", []))
        return []
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
        Fetch pathways by industry sector or catalogue domain.
        """
        if not sector:
            return []
        sec_lower = str(sector).strip().lower()
        pathway_matches = [
            p for p in PathwayDiscoveryService.PATHWAY_DATABASE
            if p.get("industry_sector", "").lower() == sec_lower
        ]
        if pathway_matches:
            return pathway_matches

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


class PathwayAnalysisService:
    """
    Deterministic Integration Service connecting Selected Pathway to
    Eligibility Verification Engine and Skill Gap Analysis Engine.
    """

    @classmethod
    def check_target_pathway_conflict(cls, target_role: str, pathway: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Evaluate if a declared target role conflicts with a selected pathway.
        Returns (is_conflict, explanation_message).
        """
        if not target_role or not pathway:
            return False, None

        target_norm = str(target_role).strip().lower()
        p_name = str(pathway.get("name", "")).strip().lower()
        p_id = str(pathway.get("id", "")).strip().lower()
        p_role = str(pathway.get("target_role", "")).strip().lower()
        p_sector = str(pathway.get("industry_sector", "")).strip().lower()

        # 1. Exact or partial string match
        if target_norm == p_name or target_norm in p_name or p_name in target_norm:
            return False, None
        if p_role and (target_norm == p_role or target_norm in p_role or p_role in target_norm):
            return False, None
        if target_norm in p_id or p_id in target_norm:
            return False, None

        # 2. Known alias / sector mappings
        alias_sectors = {
            "doctor": ["healthcare-medicine", "medicine & healthcare", "healthcare"],
            "physician": ["healthcare-medicine", "medicine & healthcare", "healthcare"],
            "surgeon": ["healthcare-medicine", "medicine & healthcare", "healthcare"],
            "nurse": ["healthcare-medicine", "medicine & healthcare", "healthcare"],
            "software engineer": ["software-engineering", "technology", "software development"],
            "developer": ["software-engineering", "technology"],
            "programmer": ["software-engineering", "technology"],
            "data scientist": ["data-science-analytics", "technology", "data science"],
            "cloud engineer": ["cloud-devops", "technology", "cloud architecture & devops"],
            "devops": ["cloud-devops", "technology", "cloud architecture & devops"],
            "civil engineer": ["civil-engineering", "engineering", "civil & infrastructure engineering"],
            "teacher": ["education-teaching", "education", "education & academic teaching"],
            "professor": ["education-teaching", "education", "education & academic teaching"],
            "banker": ["banking-finance", "finance", "banking & financial analysis"],
            "accountant": ["banking-finance", "finance", "banking & financial analysis"],
            "civil servant": ["public-service-govt", "government/public service", "public administration & civil services"],
            "ias": ["public-service-govt", "government/public service", "public administration & civil services"],
            "lawyer": ["legal-law", "law & legal practice", "legal / law", "legal", "public-service-govt"],
            "advocate": ["legal-law", "law & legal practice", "legal / law", "legal"],
            "legal": ["legal-law", "law & legal practice", "legal / law", "legal"],
            "judge": ["legal-law", "law & legal practice", "legal / law", "legal", "public-service-govt"],
            "designer": ["creative-design", "design/creative", "ui/ux & product design"],
            "entrepreneur": ["entrepreneurship-startups", "business", "entrepreneurship & innovation"],
        }

        for role_key, valid_matches in alias_sectors.items():
            if role_key in target_norm or target_norm in role_key:
                if p_id in valid_matches or p_name in valid_matches or p_sector in valid_matches:
                    return False, None
                return True, f"Conflict detected: Target role '{target_role}' does not match selected pathway '{pathway.get('name')}'. Please clarify or align your selection."

        # Token overlap check
        target_tokens = set(target_norm.split())
        pathway_tokens = set(p_name.split())
        common = target_tokens.intersection(pathway_tokens)
        meaningful_common = [t for t in common if len(t) > 3 and t not in ("and", "the", "for", "with")]
        if meaningful_common:
            return False, None

        return True, f"Conflict detected: Target role '{target_role}' does not match selected pathway '{pathway.get('name')}'. Please clarify or align your selection."

    @classmethod
    def get_pathway_requirements(cls, pathway: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured requirements for a pathway from the knowledge base
        or from the pathway object without fabricating facts.
        """
        p_id = pathway.get("id")
        p_name = pathway.get("name", "")

        # Check in PATHWAY_DATABASE
        template = None
        for p in PathwayDiscoveryService.PATHWAY_DATABASE:
            if p["id"] == p_id or p["name"].lower() == p_name.lower():
                template = p
                break

        if template and "requirements" in template:
            return dict(template["requirements"])

        # Fallback to fields on pathway
        reqs = {}
        if "requirements" in pathway and isinstance(pathway["requirements"], dict):
            reqs.update(pathway["requirements"])
        if "required_skills" in pathway:
            reqs["required_skills"] = pathway["required_skills"]
        elif template and "relevant_skills" in template:
            reqs["required_skills"] = template["relevant_skills"]

        if "min_education" in pathway:
            reqs["min_education"] = pathway["min_education"]

        return reqs

    @classmethod
    def analyze_pathway_fit(
        cls,
        context: Optional[Dict[str, Any]] = None,
        session_obj: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute combined Eligibility and Skill Gap analysis on the student's selected pathway.
        """
        ctx = context or {}
        target_session = session_obj if session_obj is not None else (session if has_request_context() else None)

        # 1. Career Direction & Target Role
        direction = (
            ctx.get("career_direction")
            or (target_session.get("career_direction") if target_session else None)
            or "exploring"
        )
        direction = str(direction).strip().lower()

        # In exploring mode, target_role is only derived from an explicitly selected pathway
        if direction == "exploring":
            target_role = ctx.get("target_role") or (target_session.get("target_role") if target_session and target_session.get("selected_pathway") else None)
        else:
            target_role = (
                ctx.get("target_role")
                or (target_session.get("target_role") if target_session else None)
            )

        # 2. Selected Pathway
        selected_pathway = (
            ctx.get("selected_pathway")
            or (target_session.get("selected_pathway") if target_session else None)
        )

        # If known direction with target_role but no selected_pathway yet in session,
        # discover or synthesize the corresponding pathway
        if direction == "known" and target_role and not selected_pathway:
            discovery = PathwayDiscoveryService.discover_pathways(
                {"career_direction": "known", "target_role": target_role},
                session_obj=target_session
            )
            if discovery.get("pathways"):
                selected_pathway = discovery["pathways"][0]
                if target_session is not None:
                    target_session["selected_pathway"] = selected_pathway

        # If exploring and no pathway selected -> safe clarification
        if not selected_pathway:
            return {
                "status": "clarification_needed",
                "career_direction": direction,
                "target_role": None if direction == "exploring" else target_role,
                "selected_pathway": None,
                "message": "Please select a career pathway before running eligibility and skill analysis.",
                "is_selected": False,
                "eligibility": None,
                "skill_gap": None
            }

        # 3. Check for conflict in known mode
        if direction == "known" and target_role:
            is_conflict, conflict_msg = cls.check_target_pathway_conflict(target_role, selected_pathway)
            if is_conflict:
                return {
                    "status": "conflict_detected",
                    "error": conflict_msg,
                    "career_direction": direction,
                    "target_role": target_role,
                    "selected_pathway": selected_pathway,
                    "message": conflict_msg,
                    "is_selected": True,
                    "eligibility": None,
                    "skill_gap": None
                }

        # 4. Extract Student Profile Details
        student_profile_data: Dict[str, Any] = {}
        if "student_profile" in ctx and isinstance(ctx["student_profile"], dict):
            student_profile_data.update(ctx["student_profile"])
        elif target_session and target_session.get("exploration_profile"):
            student_profile_data.update(target_session.get("exploration_profile"))

        student_id = ctx.get("student_id") or (target_session.get("student_id") if target_session else None)
        if student_id and not student_profile_data:
            from profile.services import ProfileService
            db_profile = ProfileService.get_profile_by_id(int(student_id))
            if db_profile:
                if hasattr(db_profile, "to_dict"):
                    student_profile_data.update(db_profile.to_dict())
                elif isinstance(db_profile, dict):
                    student_profile_data.update(db_profile)

        # 5. Extract Pathway Requirements
        pathway_requirements = cls.get_pathway_requirements(selected_pathway)

        # 6. Execute Eligibility Engine (Reusing EligibilityService)
        eligibility_result = EligibilityService.check_eligibility(
            student_profile_data=student_profile_data,
            target_opportunity_data=pathway_requirements
        )

        # 7. Execute Skill Gap Engine (Reusing SkillGapService)
        student_skills = student_profile_data.get("skills", [])
        target_skills = (
            pathway_requirements.get("required_skills")
            or selected_pathway.get("relevant_skills")
            or selected_pathway.get("skills")
            or []
        )
        skill_gap_result = SkillGapService.analyze_gap(
            current_skills=student_skills,
            target_career_skills=target_skills
        )

        # 8. Build Factual Summary
        p_name = selected_pathway.get("name", "Target Pathway")
        edu_val = student_profile_data.get("education_level") or "Not provided"
        skills_val = ", ".join(student_skills) if student_skills else "None provided"
        missing_count = len(skill_gap_result.get("missing_skills", []))
        elig_status = eligibility_result.get("status", "NEEDS_VERIFICATION")

        factual_summary = (
            f"Your current profile shows an education background of '{edu_val}' with recorded skills in [{skills_val}]. "
            f"Eligibility verification for '{p_name}' evaluated to status '{elig_status}'. "
            f"Skill gap analysis shows a match rate of {skill_gap_result.get('match_rate', 0)}% "
            f"with {missing_count} missing skill(s) identified for this pathway."
        )

        return {
            "status": "success",
            "analysis_status": "complete",
            "career_direction": direction,
            "target_role": target_role or selected_pathway.get("name"),
            "selected_pathway": selected_pathway,
            "student_profile": student_profile_data,
            "pathway_requirements": pathway_requirements,
            "eligibility": eligibility_result,
            "skill_gap": skill_gap_result,
            "factual_summary": factual_summary,
            "next_step": "Continue to Personalized Action Plan"
        }
