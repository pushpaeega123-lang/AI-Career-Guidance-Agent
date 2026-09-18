import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union


class SkillGapService:
    """
    Deterministic, explainable Skill Gap Analysis Engine.
    Compares current student skills against target career / opportunity required skills.
    """

    # Curated broad learning areas taxonomy
    LEARNING_AREAS_MAP = {
        # Programming Languages
        "python": "Programming Languages",
        "java": "Programming Languages",
        "c++": "Programming Languages",
        "cpp": "Programming Languages",
        "c#": "Programming Languages",
        "csharp": "Programming Languages",
        "c": "Programming Languages",
        "javascript": "Programming Languages",
        "typescript": "Programming Languages",
        "go": "Programming Languages",
        "golang": "Programming Languages",
        "rust": "Programming Languages",
        "ruby": "Programming Languages",
        "php": "Programming Languages",
        "swift": "Programming Languages",
        "kotlin": "Programming Languages",
        "scala": "Programming Languages",
        "r": "Programming Languages",
        "dart": "Programming Languages",
        "lua": "Programming Languages",
        "bash": "Programming Languages",
        "shell": "Programming Languages",

        # Web & Frameworks
        "html": "Web Development & Frameworks",
        "html5": "Web Development & Frameworks",
        "css": "Web Development & Frameworks",
        "css3": "Web Development & Frameworks",
        "react": "Web Development & Frameworks",
        "reactjs": "Web Development & Frameworks",
        "angular": "Web Development & Frameworks",
        "angularjs": "Web Development & Frameworks",
        "vue": "Web Development & Frameworks",
        "vuejs": "Web Development & Frameworks",
        "svelte": "Web Development & Frameworks",
        "nextjs": "Web Development & Frameworks",
        "next.js": "Web Development & Frameworks",
        "nodejs": "Web Development & Frameworks",
        "node.js": "Web Development & Frameworks",
        "node": "Web Development & Frameworks",
        "express": "Web Development & Frameworks",
        "expressjs": "Web Development & Frameworks",
        "django": "Web Development & Frameworks",
        "flask": "Web Development & Frameworks",
        "fastapi": "Web Development & Frameworks",
        "spring": "Web Development & Frameworks",
        "spring boot": "Web Development & Frameworks",
        "asp.net": "Web Development & Frameworks",
        ".net": "Web Development & Frameworks",
        "dotnet": "Web Development & Frameworks",
        "laravel": "Web Development & Frameworks",
        "bootstrap": "Web Development & Frameworks",
        "tailwind": "Web Development & Frameworks",
        "tailwindcss": "Web Development & Frameworks",

        # Databases & Storage
        "sql": "Databases & Storage",
        "mysql": "Databases & Storage",
        "postgresql": "Databases & Storage",
        "postgres": "Databases & Storage",
        "mongodb": "Databases & Storage",
        "redis": "Databases & Storage",
        "sqlite": "Databases & Storage",
        "oracle": "Databases & Storage",
        "cassandra": "Databases & Storage",
        "dynamodb": "Databases & Storage",
        "elasticsearch": "Databases & Storage",
        "firebase": "Databases & Storage",
        "neo4j": "Databases & Storage",
        "mariadb": "Databases & Storage",

        # Cloud & DevOps
        "docker": "Cloud & DevOps",
        "kubernetes": "Cloud & DevOps",
        "k8s": "Cloud & DevOps",
        "aws": "Cloud & DevOps",
        "amazon web services": "Cloud & DevOps",
        "azure": "Cloud & DevOps",
        "gcp": "Cloud & DevOps",
        "google cloud": "Cloud & DevOps",
        "ci/cd": "Cloud & DevOps",
        "cicd": "Cloud & DevOps",
        "jenkins": "Cloud & DevOps",
        "terraform": "Cloud & DevOps",
        "ansible": "Cloud & DevOps",
        "linux": "Cloud & DevOps",
        "nginx": "Cloud & DevOps",
        "helm": "Cloud & DevOps",
        "prometheus": "Cloud & DevOps",
        "grafana": "Cloud & DevOps",

        # Data Science & AI / ML
        "machine learning": "Data Science & AI / ML",
        "ml": "Data Science & AI / ML",
        "deep learning": "Data Science & AI / ML",
        "dl": "Data Science & AI / ML",
        "artificial intelligence": "Data Science & AI / ML",
        "ai": "Data Science & AI / ML",
        "pandas": "Data Science & AI / ML",
        "numpy": "Data Science & AI / ML",
        "scikit-learn": "Data Science & AI / ML",
        "sklearn": "Data Science & AI / ML",
        "tensorflow": "Data Science & AI / ML",
        "pytorch": "Data Science & AI / ML",
        "keras": "Data Science & AI / ML",
        "nlp": "Data Science & AI / ML",
        "computer vision": "Data Science & AI / ML",
        "data analysis": "Data Science & AI / ML",
        "data visualization": "Data Science & AI / ML",
        "tableau": "Data Science & AI / ML",
        "power bi": "Data Science & AI / ML",
        "powerbi": "Data Science & AI / ML",
        "spark": "Data Science & AI / ML",
        "hadoop": "Data Science & AI / ML",

        # Version Control & Tools
        "git": "Version Control & Collaboration",
        "github": "Version Control & Collaboration",
        "gitlab": "Version Control & Collaboration",
        "bitbucket": "Version Control & Collaboration",
        "jira": "Version Control & Collaboration",
        "agile": "Version Control & Collaboration",
        "scrum": "Version Control & Collaboration",

        # Testing & QA
        "testing": "Testing & Quality Assurance",
        "unit testing": "Testing & Quality Assurance",
        "pytest": "Testing & Quality Assurance",
        "unittest": "Testing & Quality Assurance",
        "jest": "Testing & Quality Assurance",
        "mocha": "Testing & Quality Assurance",
        "selenium": "Testing & Quality Assurance",
        "cypress": "Testing & Quality Assurance",
        "qa": "Testing & Quality Assurance",
        "tdd": "Testing & Quality Assurance",

        # Cybersecurity & Networking
        "cybersecurity": "Cybersecurity & Networking",
        "security": "Cybersecurity & Networking",
        "cryptography": "Cybersecurity & Networking",
        "penetration testing": "Cybersecurity & Networking",
        "owasp": "Cybersecurity & Networking",
        "networking": "Cybersecurity & Networking",
        "tcp/ip": "Cybersecurity & Networking",
    }

    # Core foundational skills categorized as Critical by default fallback
    DEFAULT_CRITICAL_DOMAINS = {
        "Programming Languages",
        "Databases & Storage"
    }

    DEFAULT_RECOMMENDED_DOMAINS = {
        "Web Development & Frameworks",
        "Cloud & DevOps",
        "Data Science & AI / ML",
        "Testing & Quality Assurance",
        "Cybersecurity & Networking"
    }

    @staticmethod
    def _normalize_skill(skill: Any) -> str:
        """
        Normalize skill string:
        - Strip whitespace
        - Lowercase
        - Collapse multiple spaces
        - Normalize specific aliases (e.g. react.js -> react)
        """
        if skill is None:
            return ""
        s = str(skill).strip().lower()
        s = re.sub(r"\s+", " ", s)

        # Standardize common aliases
        alias_map = {
            "react.js": "react",
            "reactjs": "react",
            "vue.js": "vue",
            "vuejs": "vue",
            "angular.js": "angular",
            "angularjs": "angular",
            "node.js": "node",
            "nodejs": "node",
            "next.js": "nextjs",
            "c++": "cpp",
            "c#": "csharp",
            "postgres": "postgresql",
            "amazon web services": "aws",
            "google cloud": "gcp",
            "k8s": "kubernetes",
        }
        return alias_map.get(s, s)

    @classmethod
    def _extract_skill_list(cls, input_data: Any) -> Tuple[List[str], Dict[str, str], Dict[str, str]]:
        """
        Extract normalized skills, mapping from normalized to original display name,
        and explicit priority mapping if provided.
        Returns:
            (normalized_unique_skills, norm_to_display_map, norm_to_priority_map)
        """
        if input_data is None:
            return [], {}, {}

        norm_skills: List[str] = []
        norm_to_display: Dict[str, str] = {}
        norm_to_priority: Dict[str, str] = {}
        seen: Set[str] = set()

        def add_skill(raw_name: Any, explicit_priority: Optional[str] = None):
            if raw_name is None:
                return
            display_name = str(raw_name).strip()
            if not display_name:
                return
            norm = cls._normalize_skill(display_name)
            if norm and norm not in seen:
                seen.add(norm)
                norm_skills.append(norm)
                norm_to_display[norm] = display_name
                if explicit_priority:
                    norm_to_priority[norm] = explicit_priority.lower().strip()

        # Handle various input data structures
        if isinstance(input_data, dict):
            # Dict with priority buckets: {"critical": [...], "recommended": [...], "optional": [...]}
            has_priority_buckets = any(k in input_data for k in ("critical", "recommended", "optional", "mandatory"))
            if has_priority_buckets:
                for priority_key in ("critical", "mandatory", "recommended", "optional"):
                    p_val = input_data.get(priority_key, [])
                    effective_priority = "critical" if priority_key == "mandatory" else priority_key
                    if isinstance(p_val, (list, tuple, set)):
                        for item in p_val:
                            add_skill(item, explicit_priority=effective_priority)
                    elif isinstance(p_val, str):
                        for item in re.split(r"[,;\n\r]+", p_val):
                            add_skill(item, explicit_priority=effective_priority)
            else:
                # Dict with nested skills key (e.g. {"skills": [...]}, {"required_skills": [...]})
                for k in ("skills", "required_skills", "current_skills", "target_skills", "items", "data"):
                    if k in input_data:
                        sub_data = input_data[k]
                        sub_skills, sub_disp, sub_prio = cls._extract_skill_list(sub_data)
                        for s in sub_skills:
                            if s not in seen:
                                seen.add(s)
                                norm_skills.append(s)
                                norm_to_display[s] = sub_disp[s]
                                if s in sub_prio:
                                    norm_to_priority[s] = sub_prio[s]
                        break

        elif isinstance(input_data, (list, tuple, set)):
            for item in input_data:
                if isinstance(item, dict):
                    # Item with name and priority: {"name": "Python", "priority": "critical"}
                    skill_name = item.get("name") or item.get("skill") or item.get("title")
                    prio = item.get("priority") or item.get("level")
                    add_skill(skill_name, explicit_priority=prio)
                else:
                    # String or scalar item
                    item_str = str(item).strip()
                    if "," in item_str or ";" in item_str:
                        for split_item in re.split(r"[,;\n\r]+", item_str):
                            add_skill(split_item)
                    else:
                        add_skill(item_str)

        elif isinstance(input_data, str):
            for split_item in re.split(r"[,;\n\r]+", input_data):
                add_skill(split_item)

        return norm_skills, norm_to_display, norm_to_priority

    @classmethod
    def _map_to_learning_area(cls, norm_skill: str) -> str:
        """Map a normalized skill to its broad learning area."""
        # Exact lookup
        if norm_skill in cls.LEARNING_AREAS_MAP:
            return cls.LEARNING_AREAS_MAP[norm_skill]

        # Substring / token matching
        for key, area in cls.LEARNING_AREAS_MAP.items():
            if key in norm_skill or norm_skill in key:
                return area

        return "Specialized & Domain Tools"

    @classmethod
    def _determine_priority(
        cls,
        norm_skill: str,
        explicit_priority: Optional[str],
        position_index: int,
        total_missing: int,
    ) -> str:
        """
        Determine priority ('critical', 'recommended', 'optional') using explicit priority
        or documented deterministic fallback.
        """
        if explicit_priority in ("critical", "recommended", "optional"):
            return explicit_priority

        # Deterministic fallback based on learning area domain
        area = cls._map_to_learning_area(norm_skill)
        if area in cls.DEFAULT_CRITICAL_DOMAINS:
            return "critical"
        elif area in cls.DEFAULT_RECOMMENDED_DOMAINS:
            return "recommended"

        # Positional/count deterministic fallback for domain tools
        if total_missing <= 2 or position_index == 0:
            return "critical"
        elif position_index < (total_missing * 0.6):
            return "recommended"
        else:
            return "optional"

    @classmethod
    def analyze_gap(
        cls,
        current_skills: Any,
        target_career_skills: Any,
    ) -> Dict[str, Any]:
        """
        Analyze the gap between current student skills and target career skills.

        Returns structured result:
        {
            "matching_skills": ["Python", "SQL"],
            "missing_skills": ["Docker", "Kubernetes"],
            "match_rate": 50.0,
            "gap_percentage": 50.0,
            "total_required": 4,
            "total_matched": 2,
            "total_missing": 2,
            "priority_breakdown": {
                "critical": ["Docker"],
                "recommended": ["Kubernetes"],
                "optional": []
            },
            "learning_areas": [
                {
                    "area": "Cloud & DevOps",
                    "skills": ["Docker", "Kubernetes"],
                    "count": 2
                }
            ]
        }
        """
        stu_skills, stu_disp, _ = cls._extract_skill_list(current_skills)
        target_skills, target_disp, target_prio = cls._extract_skill_list(target_career_skills)

        stu_set = set(stu_skills)
        target_set = set(target_skills)

        matching_norm = [s for s in target_skills if s in stu_set]
        missing_norm = [s for s in target_skills if s not in stu_set]

        # Use display names preserving appropriate casing
        matching_display = [target_disp.get(s, s) for s in matching_norm]
        missing_display = [target_disp.get(s, s) for s in missing_norm]

        total_req = len(target_skills)
        total_matched = len(matching_norm)
        total_missing = len(missing_norm)

        if total_req == 0:
            match_rate = 100.0
            gap_percentage = 0.0
        else:
            match_rate = round((total_matched / total_req) * 100.0, 2)
            gap_percentage = round((total_missing / total_req) * 100.0, 2)

        # Build priority breakdown for missing skills
        priority_breakdown: Dict[str, List[str]] = {
            "critical": [],
            "recommended": [],
            "optional": []
        }

        for idx, s in enumerate(missing_norm):
            disp = target_disp.get(s, s)
            explicit_prio = target_prio.get(s)
            prio = cls._determine_priority(s, explicit_prio, idx, total_missing)
            priority_breakdown[prio].append(disp)

        # Build learning areas mapping for missing skills
        areas_grouped: Dict[str, List[str]] = {}
        for s in missing_norm:
            disp = target_disp.get(s, s)
            area = cls._map_to_learning_area(s)
            if area not in areas_grouped:
                areas_grouped[area] = []
            areas_grouped[area].append(disp)

        # Convert to sorted list of learning area objects (most missing skills first)
        learning_areas = [
            {
                "area": area,
                "skills": skills,
                "count": len(skills)
            }
            for area, skills in sorted(areas_grouped.items(), key=lambda item: len(item[1]), reverse=True)
        ]

        return {
            "matching_skills": matching_display,
            "missing_skills": missing_display,
            "match_rate": match_rate,
            "gap_percentage": gap_percentage,
            "total_required": total_req,
            "total_matched": total_matched,
            "total_missing": total_missing,
            "priority_breakdown": priority_breakdown,
            "learning_areas": learning_areas,
        }
