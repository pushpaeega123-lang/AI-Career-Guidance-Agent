"""
Student Interest Intelligence Engine (Member 2).
Normalizes student interest inputs and produces transparent, explainable
mappings to standardized career domains without external LLM dependencies.
"""

import re

# Standard Career Domains Catalogue
CAREER_DOMAINS = [
    "Technology & Software",
    "Data & AI",
    "Cybersecurity",
    "Engineering",
    "Healthcare",
    "Business & Management",
    "Finance & Commerce",
    "Education & Teaching",
    "Law",
    "Design & Creative",
    "Government & Public Service",
    "Media & Communication",
    "Science & Research",
    "Skilled & Technical Trades"
]

UNKNOWN_DOMAIN = "Unknown / Needs Further Exploration"
UNKNOWN_REASON = (
    "This interest is not currently indexed in the standard career taxonomy. "
    "It may represent an emerging specialization, a cross-disciplinary pursuit, or a personal hobby."
)

# Comprehensive Taxonomy Database: Canonical Names, Synonyms/Aliases, and Factual Domain Mappings with Reasons
INTEREST_TAXONOMY = {
    "Python": {
        "aliases": ["python", "python programming", "python3", "py"],
        "domains": [
            {
                "name": "Technology & Software",
                "reason": "Python is widely used in software development, backend engineering, scripting, and system automation."
            },
            {
                "name": "Data & AI",
                "reason": "Python is the primary language for data analysis, machine learning pipelines, and artificial intelligence research."
            }
        ]
    },
    "Java": {
        "aliases": ["java", "core java", "java programming", "spring boot"],
        "domains": [
            {
                "name": "Technology & Software",
                "reason": "Java is an enterprise-standard language utilized heavily in large-scale backend systems, Android apps, and microservices."
            }
        ]
    },
    "C++": {
        "aliases": ["c++", "cpp", "c plus plus"],
        "domains": [
            {
                "name": "Technology & Software",
                "reason": "C++ is foundational for high-performance computing, game engines, graphics pipelines, and systems programming."
            },
            {
                "name": "Engineering",
                "reason": "C++ is widely deployed in embedded firmware, robotics, automotive control systems, and hardware drivers."
            }
        ]
    },
    "Web Development": {
        "aliases": ["web development", "web dev", "frontend", "front end", "html", "css", "javascript", "react", "vue"],
        "domains": [
            {
                "name": "Technology & Software",
                "reason": "Web development forms the infrastructure of modern internet platforms, web applications, and interactive user interfaces."
            }
        ]
    },
    "Full Stack Development": {
        "aliases": ["full stack", "full stack development", "fullstack", "mern", "mean"],
        "domains": [
            {
                "name": "Technology & Software",
                "reason": "Full stack development bridges client-facing interfaces, application logic, and database systems."
            }
        ]
    },
    "Cloud Computing": {
        "aliases": ["cloud computing", "cloud architecture", "aws", "azure", "gcp", "google cloud", "cloud systems"],
        "domains": [
            {
                "name": "Technology & Software",
                "reason": "Cloud architecture enables distributed computing, scalable storage, and resilient infrastructure deployment."
            }
        ]
    },
    "DevOps": {
        "aliases": ["devops", "ci/cd", "docker", "kubernetes", "site reliability engineering", "sre"],
        "domains": [
            {
                "name": "Technology & Software",
                "reason": "DevOps integrates continuous integration, automated deployment, container orchestration, and infrastructure monitoring."
            }
        ]
    },
    "Artificial Intelligence": {
        "aliases": ["artificial intelligence", "ai", "genai", "generative ai", "deep learning", "neural networks"],
        "domains": [
            {
                "name": "Data & AI",
                "reason": "Artificial intelligence centers on cognitive computational models, deep neural networks, and automated reasoning."
            },
            {
                "name": "Technology & Software",
                "reason": "AI systems are integrated into software applications, autonomous tools, and intelligent developer platforms."
            }
        ]
    },
    "Machine Learning": {
        "aliases": ["machine learning", "ml", "supervised learning", "reinforcement learning"],
        "domains": [
            {
                "name": "Data & AI",
                "reason": "Machine learning focuses on statistical algorithms, feature engineering, and predictive models trained on datasets."
            }
        ]
    },
    "Data Science": {
        "aliases": ["data science", "data analytics", "data analysis", "big data", "data engineering", "sql", "analytics"],
        "domains": [
            {
                "name": "Data & AI",
                "reason": "Data science combines statistical exploration, quantitative modeling, and data pipelines to extract actionable intelligence."
            },
            {
                "name": "Science & Research",
                "reason": "Data science principles are used extensively across empirical scientific experimentation and quantitative studies."
            }
        ]
    },
    "Cybersecurity": {
        "aliases": ["cybersecurity", "cyber security", "ethical hacking", "infosec", "network security", "penetration testing", "cryptography"],
        "domains": [
            {
                "name": "Cybersecurity",
                "reason": "Cybersecurity deals with threat detection, vulnerability remediation, cryptographic defense, and digital asset security."
            },
            {
                "name": "Technology & Software",
                "reason": "Secure coding practices and network protocols are essential elements of enterprise software reliability."
            }
        ]
    },
    "Robotics": {
        "aliases": ["robotics", "iot", "internet of things", "embedded systems", "mechatronics", "autonomous systems"],
        "domains": [
            {
                "name": "Engineering",
                "reason": "Robotics unites mechanical design, electronic sensors, microcontrollers, and actuator control systems."
            },
            {
                "name": "Data & AI",
                "reason": "Modern robotics relies on computer vision, sensor fusion algorithms, and autonomous navigation models."
            }
        ]
    },
    "Mechanical Engineering": {
        "aliases": ["mechanical engineering", "cad", "thermodynamics", "automotive", "fluid mechanics", "manufacturing"],
        "domains": [
            {
                "name": "Engineering",
                "reason": "Mechanical engineering covers physical machinery, thermal dynamics, structural materials, and manufacturing systems."
            }
        ]
    },
    "Civil Engineering": {
        "aliases": ["civil engineering", "structural engineering", "construction", "surveying", "geotechnical"],
        "domains": [
            {
                "name": "Engineering",
                "reason": "Civil engineering encompasses public infrastructure, structural integrity design, transportation systems, and urban construction."
            }
        ]
    },
    "Electronics & Electrical": {
        "aliases": ["electronics", "electrical engineering", "vlsi", "circuits", "semiconductors", "pcb design"],
        "domains": [
            {
                "name": "Engineering",
                "reason": "Electronics focuses on circuit design, semiconductor devices, microprocessors, and power distribution systems."
            }
        ]
    },
    "Biology": {
        "aliases": ["biology", "biological sciences", "molecular biology", "genetics", "botany", "zoology"],
        "domains": [
            {
                "name": "Healthcare",
                "reason": "Biological foundations underpin clinical understanding of living organisms, cellular functions, and pathologies."
            },
            {
                "name": "Science & Research",
                "reason": "Biological study involves laboratory experimentation, genetic sequencing, and environmental observation."
            }
        ]
    },
    "Medicine": {
        "aliases": ["medicine", "medical science", "clinical", "nursing", "pharmacy", "pharmacology", "surgery", "mbbs"],
        "domains": [
            {
                "name": "Healthcare",
                "reason": "Medicine and clinical sciences address disease prevention, patient diagnosis, pharmacology, and therapeutic care."
            }
        ]
    },
    "Accounting": {
        "aliases": ["accounting", "chartered accountancy", "ca", "taxation", "auditing", "bookkeeping", "cpa"],
        "domains": [
            {
                "name": "Finance & Commerce",
                "reason": "Accounting entails financial reporting compliance, balance sheet analysis, tax computation, and statutory audit."
            }
        ]
    },
    "Finance": {
        "aliases": ["finance", "financial analysis", "investment banking", "fintech", "stock market", "economics"],
        "domains": [
            {
                "name": "Finance & Commerce",
                "reason": "Finance covers capital allocation, risk evaluation, portfolio management, macroeconomic analysis, and market operations."
            },
            {
                "name": "Business & Management",
                "reason": "Corporate financial planning directs enterprise resource management and strategic investments."
            }
        ]
    },
    "Business Management": {
        "aliases": ["business", "business management", "management", "mba", "entrepreneurship", "startup", "operations"],
        "domains": [
            {
                "name": "Business & Management",
                "reason": "Business management coordinates organizational strategy, team operations, enterprise leadership, and process execution."
            }
        ]
    },
    "Marketing": {
        "aliases": ["marketing", "digital marketing", "seo", "branding", "growth marketing", "social media marketing"],
        "domains": [
            {
                "name": "Business & Management",
                "reason": "Marketing drives audience acquisition, brand positioning, sales conversion strategies, and consumer market research."
            },
            {
                "name": "Media & Communication",
                "reason": "Campaign execution involves content creation, communication strategy, and public storytelling."
            }
        ]
    },
    "Teaching & Education": {
        "aliases": ["teaching", "education", "pedagogy", "training", "instructional design", "e-learning"],
        "domains": [
            {
                "name": "Education & Teaching",
                "reason": "Teaching focuses on pedagogical methodology, knowledge transfer, curriculum structuring, and learner mentoring."
            }
        ]
    },
    "Law & Legal Studies": {
        "aliases": ["law", "legal studies", "judiciary", "corporate law", "constitutional law", "intellectual property", "llb"],
        "domains": [
            {
                "name": "Law",
                "reason": "Law involves constitutional frameworks, jurisprudence, statutory interpretation, dispute resolution, and regulatory compliance."
            },
            {
                "name": "Government & Public Service",
                "reason": "Legal expertise intersects heavily with legislative policy, constitutional governance, and public regulatory bodies."
            }
        ]
    },
    "Graphic Design": {
        "aliases": ["graphic design", "design", "ui/ux", "ui/ux design", "product design", "illustration", "photoshop", "figma"],
        "domains": [
            {
                "name": "Design & Creative",
                "reason": "Graphic and UI/UX design encompasses visual composition, user empathy, wireframing, color theory, and digital interaction design."
            }
        ]
    },
    "Writing & Journalism": {
        "aliases": ["writing", "technical writing", "journalism", "content writing", "editing", "mass communication", "public relations"],
        "domains": [
            {
                "name": "Media & Communication",
                "reason": "Writing and journalism center on investigative research, narrative formulation, informational clarity, and mass communication."
            }
        ]
    },
    "Government & Civil Services": {
        "aliases": ["government", "civil services", "upsc", "public service", "public administration", "public policy", "governance"],
        "domains": [
            {
                "name": "Government & Public Service",
                "reason": "Civil services and governance focus on public administrative machinery, civic development programs, and state policy implementation."
            }
        ]
    },
    "Physics": {
        "aliases": ["physics", "astrophysics", "quantum mechanics", "optics"],
        "domains": [
            {
                "name": "Science & Research",
                "reason": "Physics explores natural physical phenomena, theoretical mathematical models, and fundamental forces of the universe."
            },
            {
                "name": "Engineering",
                "reason": "Applied physics serves as the foundation for semiconductor electronics, mechanics, and sensor engineering."
            }
        ]
    },
    "Chemistry": {
        "aliases": ["chemistry", "chemical science", "organic chemistry", "biochemistry", "materials science"],
        "domains": [
            {
                "name": "Science & Research",
                "reason": "Chemistry investigates molecular structures, chemical reactions, syntheses, and material properties."
            },
            {
                "name": "Healthcare",
                "reason": "Biochemistry and pharmaceutical chemistry are central to drug synthesis, toxicology, and diagnostic assays."
            }
        ]
    },
    "Skilled Trades & Networking": {
        "aliases": ["networking", "network administration", "hardware repair", "technician", "electrician", "skilled trades"],
        "domains": [
            {
                "name": "Skilled & Technical Trades",
                "reason": "Technical trades involve practical hands-on diagnostics, physical infrastructure wiring, hardware assembly, and maintenance."
            }
        ]
    }
}

# Compile reverse alias lookup index for O(1) matching
ALIAS_INDEX = {}
for canonical, data in INTEREST_TAXONOMY.items():
    ALIAS_INDEX[canonical.lower()] = canonical
    for alias in data.get("aliases", []):
        ALIAS_INDEX[alias.lower()] = canonical


class InterestIntelligenceService:
    """
    Core service for student interest intelligence.
    Normalizes arbitrary interest strings and maps them to transparent, explainable career domains.
    """

    @staticmethod
    def get_career_domains():
        """Returns the full list of standardized career domains."""
        return list(CAREER_DOMAINS)

    @staticmethod
    def parse_interest_input(interests_input) -> list[str]:
        """
        Extracts raw interest strings from string or list input.
        Handles comma-separated strings, lists, or mixed inputs safely.
        """
        if not interests_input:
            return []

        raw_items = []
        if isinstance(interests_input, str):
            raw_items = interests_input.split(',')
        elif isinstance(interests_input, list):
            for item in interests_input:
                if isinstance(item, str):
                    raw_items.extend(item.split(','))
                elif item is not None:
                    raw_items.append(str(item))

        # Strip whitespace and discard empty entries
        cleaned = [item.strip() for item in raw_items if item and item.strip()]
        return cleaned

    @staticmethod
    def normalize_single_interest(term: str) -> tuple[str, str, bool]:
        """
        Normalizes a single interest string.
        Returns: (canonical_name, original_cleaned, is_mapped)
        """
        cleaned = term.strip()
        normalized_key = cleaned.lower()

        # Direct alias/canonical lookup
        if normalized_key in ALIAS_INDEX:
            canonical_name = ALIAS_INDEX[normalized_key]
            return canonical_name, cleaned, True

        # Non-destructive fallback for unknown interest
        # Preserve original capitalization if title-cased, or title-case if all lowercase
        if cleaned.islower():
            fallback_name = cleaned.title()
        else:
            fallback_name = cleaned

        return fallback_name, cleaned, False

    @classmethod
    def analyze_interests(cls, interests_input) -> dict:
        """
        Main intelligence pipeline:
        1. Parses and normalizes incoming interests.
        2. Deduplicates while preserving original encounter order.
        3. Looks up career domains and factual explainability statements.
        4. Identifies unmapped/novel interests safely without crashing.
        5. Computes overall domain summary.
        """
        raw_terms = cls.parse_interest_input(interests_input)
        
        seen_canonical = set()
        structured_interests = []
        all_domains = []
        unmapped_interests = []

        for term in raw_terms:
            canonical_name, original, is_mapped = cls.normalize_single_interest(term)
            lower_name = canonical_name.lower()

            # Deduplication: Avoid processing the exact same interest twice
            if lower_name in seen_canonical:
                continue
            seen_canonical.add(lower_name)

            if is_mapped and canonical_name in INTEREST_TAXONOMY:
                domains_data = INTEREST_TAXONOMY[canonical_name].get("domains", [])
                structured_interests.append({
                    "name": canonical_name,
                    "original": original,
                    "is_mapped": True,
                    "domains": [
                        {
                            "name": d["name"],
                            "reason": d["reason"]
                        } for d in domains_data
                    ]
                })
                for d in domains_data:
                    if d["name"] not in all_domains:
                        all_domains.append(d["name"])
            else:
                # Safe handling for unknown interest
                unmapped_interests.append(canonical_name)
                structured_interests.append({
                    "name": canonical_name,
                    "original": original,
                    "is_mapped": False,
                    "domains": [
                        {
                            "name": UNKNOWN_DOMAIN,
                            "reason": UNKNOWN_REASON
                        }
                    ]
                })

        return {
            "status": "success",
            "interests": structured_interests,
            "domain_summary": all_domains,
            "unmapped_interests": unmapped_interests
        }
